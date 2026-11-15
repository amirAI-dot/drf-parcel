"""
Pagination, in the envelope.

Two kinds, and each view chooses - a numbered list in one, an endless feed
in the next. ``pagination.type`` says which, so one component on a client
reads either without guessing::

    "pagination": {"type": "page", "count": 45, "page": 2, "pages": 3,
                   "page_size": 20, "has_next": true, "has_previous": true}

    "pagination": {"type": "cursor", "next_cursor": "cD0y...", "previous_cursor": null,
                   "page_size": 20, "has_next": true, "has_previous": false}

The page size is read from the view, then the paginator, then
``DRF_PARCEL['PAGE_SIZE']``, then DRF's own ``PAGE_SIZE``. A client may choose it only where that is
allowed - ``client_page_size`` on the view or the paginator, or
``DRF_PARCEL['CLIENT_PAGE_SIZE']`` - and always under a ceiling: without
one, ``?page_size=1000000`` is a request to read a whole table, open to
anybody. A size the client cannot have is not an error: it is the ceiling,
or the default.
"""

from collections.abc import Sequence
from typing import Any, Final
from urllib import parse

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DataError
from django.db.models import QuerySet
from rest_framework import pagination
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_parcel import conf
from drf_parcel.envelope import envelope_schema
from drf_parcel.exceptions import InvalidCursorError
from drf_parcel.responses import success_response

#: What reading a page raises when a cursor's position is no value of the
#: column the feed is ordered by - a number where a date is, a character the
#: database refuses.
_NOT_A_POSITION: Final = (ValueError, TypeError, DjangoValidationError, DataError)

#: The schema of a numbered page's ``pagination``.
PAGE_SCHEMA: Final[dict[str, Any]] = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'example': 'page', 'description': 'Always "page".'},
        'count': {'type': 'integer', 'description': 'Rows in the whole list.'},
        'page': {'type': 'integer', 'description': 'This page, from 1.'},
        'pages': {'type': 'integer', 'description': 'How many pages there are.'},
        'page_size': {'type': 'integer', 'description': 'The size used, after the ceiling.'},
        'has_next': {'type': 'boolean'},
        'has_previous': {'type': 'boolean'},
    },
    'required': ['type', 'count', 'page', 'pages', 'page_size', 'has_next', 'has_previous'],
}

#: The schema of a feed's ``pagination``.
CURSOR_SCHEMA: Final[dict[str, Any]] = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'example': 'cursor', 'description': 'Always "cursor".'},
        'next_cursor': {
            'type': 'string',
            'nullable': True,
            'description': 'Sent back as ?cursor= for the next page; null at the end.',
        },
        'previous_cursor': {'type': 'string', 'nullable': True},
        'page_size': {'type': 'integer', 'description': 'The size used, after the ceiling.'},
        'has_next': {'type': 'boolean'},
        'has_previous': {'type': 'boolean'},
    },
    'required': [
        'type',
        'next_cursor',
        'previous_cursor',
        'page_size',
        'has_next',
        'has_previous',
    ],
}


class _PageSize:
    """
    How many rows a page holds: the view's say, then the paginator's, then the project's.

    Each of ``page_size``, ``max_page_size`` and ``client_page_size`` is read
    the same way, so a view overrides any one of them by naming it.
    """

    #: None defers to the project: DRF_PARCEL's PAGE_SIZE, else DRF's own.
    page_size: int | None = None
    max_page_size: int | None = None
    client_page_size: bool | None = None

    view: APIView | None = None

    def _setting(self, name: str) -> Any:
        """One of the three, from the view, the paginator, or the project."""
        from_view = getattr(self.view, name, None)

        if from_view is not None:
            return from_view

        from_paginator = getattr(self, name)

        if from_paginator is not None:
            return from_paginator

        if name == 'page_size':
            return conf.page_size()

        return conf.get(name.upper())

    def get_schema_operation_parameters(self, view: APIView) -> list[dict[str, Any]]:
        """
        The query parameters, as DRF documents them - ``page_size`` only on a
        view that lets the client choose, with its ceiling.
        """
        self.view = view
        self.page_size_query_param = self.client_page_size_param()
        parameters: list[dict[str, Any]] = super().get_schema_operation_parameters(view)  # type: ignore[misc]

        for parameter in parameters:
            if parameter['name'] == self.page_size_query_param:
                parameter['schema'] = {
                    **parameter['schema'],
                    'minimum': 1,
                    'maximum': self._setting('max_page_size'),
                }

        return parameters

    def wraps(self) -> bool:
        """
        Whether a page is answered in the envelope: not in a view that opts
        out with ``parcel_wrap = False``, which is answered as DRF answers.
        """
        return getattr(self.view, 'parcel_wrap', True) is not False

    def client_page_size_param(self) -> str | None:
        """The parameter a client chooses with - none where it may not choose."""
        return str(conf.get('PAGE_SIZE_QUERY_PARAM')) if self._setting('client_page_size') else None

    def get_page_size(self, request: Request) -> int:
        """
        The size this page holds.

        The view's size, unless the client may choose and chose one it can
        have: a size above the ceiling is the ceiling, and nothing, zero, a
        negative number or a word is the view's size.
        """
        size: int = self._setting('page_size')
        param = self.client_page_size_param()

        if param is None:
            return size

        try:
            asked = int(request.query_params[param])
        except (KeyError, ValueError):
            return size

        if asked < 1:
            return size

        ceiling: int = self._setting('max_page_size')
        return min(asked, ceiling)


class PageNumberPagination(_PageSize, pagination.PageNumberPagination):
    """
    Numbered pages: ``?page=2``.

    No ``next`` or ``previous`` link: a client on another domain builds
    ``?page=3`` itself, and a server behind a proxy builds its own links with
    the wrong scheme or host. A page past the end is a 404, as DRF answers.
    """

    def paginate_queryset(
        self, queryset: QuerySet[Any] | Sequence[Any], request: Request, view: APIView | None = None
    ) -> list[Any] | None:
        self.view = view
        self.page_size_query_param = self.client_page_size_param()
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data: Any) -> Response:
        if not self.wraps():
            return super().get_paginated_response(data)

        return success_response(data, pagination=self.pagination_meta())

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """The envelope a page answers in: the rows under ``data``, the pager beside them."""
        if not self.wraps():
            drf_page: dict[str, Any] = super().get_paginated_response_schema(schema)
            return drf_page

        return envelope_schema(schema, pagination=PAGE_SCHEMA)

    def pagination_meta(self) -> dict[str, Any]:
        """Everything a client needs to draw a pager, and nothing else."""
        assert self.request is not None
        assert self.page is not None
        return {
            'type': 'page',
            'count': self.page.paginator.count,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'page_size': self.get_page_size(self.request),
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
        }


class CursorPagination(_PageSize, pagination.CursorPagination):
    """
    An endless feed: ``?cursor=...``.

    A cursor is opaque - the client sends back what it was given. There is
    no count and no page number: not counting is the point of a cursor, on a
    table too large to count on every request.

    The order is the view's ``ordering``, or the paginator's; an ordering
    filter on the view, when there is one, decides as DRF's does.

    A cursor that decodes and still cannot be used - made by hand, or given
    for another order than the one now asked for - is the same 400 as one
    that cannot be read, never a bug.
    """

    def paginate_queryset(
        self, queryset: QuerySet[Any] | Sequence[Any], request: Request, view: APIView | None = None
    ) -> list[Any] | None:
        self.view = view
        self.page_size_query_param = self.client_page_size_param()
        self.ordering = getattr(view, 'ordering', None) or self.ordering

        if request.query_params.get(self.cursor_query_param) is None:
            return super().paginate_queryset(queryset, request, view)

        try:
            return super().paginate_queryset(queryset, request, view)
        except _NOT_A_POSITION as unusable:
            raise InvalidCursorError from unusable

    def decode_cursor(self, request: Request) -> pagination.Cursor | None:
        """A cursor that cannot be read is the client's mistake: 400, not DRF's 404."""
        try:
            return super().decode_cursor(request)
        except NotFound as unreadable:
            raise InvalidCursorError from unreadable

    def get_paginated_response(self, data: Any) -> Response:
        if not self.wraps():
            return super().get_paginated_response(data)

        return success_response(data, pagination=self.pagination_meta())

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """The envelope a feed answers in: the rows under ``data``, the cursors beside them."""
        if not self.wraps():
            drf_page: dict[str, Any] = super().get_paginated_response_schema(schema)
            return drf_page

        return envelope_schema(schema, pagination=CURSOR_SCHEMA)

    def pagination_meta(self) -> dict[str, Any]:
        """The cursors to send back, and whether there is anything to send them for."""
        return {
            'type': 'cursor',
            'next_cursor': self._cursor_in(self.get_next_link()),
            'previous_cursor': self._cursor_in(self.get_previous_link()),
            'page_size': self.page_size,
            'has_next': self.has_next,
            'has_previous': self.has_previous,
        }

    def _cursor_in(self, link: str | None) -> str | None:
        """The cursor alone, out of the link DRF builds around it."""
        if link is None:
            return None

        query = parse.parse_qs(parse.urlsplit(link).query)
        return query[self.cursor_query_param][0]
