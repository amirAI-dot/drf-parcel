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
``DRF_PARCEL['PAGE_SIZE']``. A client may choose it only where that is
allowed - ``client_page_size`` on the view or the paginator, or
``DRF_PARCEL['CLIENT_PAGE_SIZE']`` - and always under a ceiling: without
one, ``?page_size=1000000`` is a request to read a whole table, open to
anybody. A size the client cannot have is not an error: it is the ceiling,
or the default.
"""

from collections.abc import Sequence
from typing import Any
from urllib import parse

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import pagination, status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.request import Request
from rest_framework.views import APIView

from drf_parcel import conf
from drf_parcel.responses import EnvelopeResponse, success_response


class InvalidCursor(APIException):
    """A cursor the server cannot read: the client sent back something it was never given."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_cursor'
    default_detail = _('The cursor is not valid.')


class _PageSize:
    """
    How many rows a page holds: the view's say, then the paginator's, then the project's.

    Each of ``page_size``, ``max_page_size`` and ``client_page_size`` is read
    the same way, so a view overrides any one of them by naming it.
    """

    #: None defers to the project: DRF's own PAGE_SIZE is not read here.
    page_size: int | None = None
    max_page_size: int | None = None
    client_page_size: bool | None = None

    view: APIView | None = None

    def _setting(self, name: str) -> Any:
        """One of the three, from the view, the paginator, or ``DRF_PARCEL``."""
        from_view = getattr(self.view, name, None)

        if from_view is not None:
            return from_view

        from_paginator = getattr(self, name)

        if from_paginator is not None:
            return from_paginator

        return conf.get(name.upper())

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

    def get_paginated_response(self, data: Any) -> EnvelopeResponse:
        return success_response(data, pagination=self.pagination_meta())

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
    """

    def paginate_queryset(
        self, queryset: QuerySet[Any] | Sequence[Any], request: Request, view: APIView | None = None
    ) -> list[Any] | None:
        self.view = view
        self.page_size_query_param = self.client_page_size_param()
        self.ordering = getattr(view, 'ordering', None) or self.ordering
        return super().paginate_queryset(queryset, request, view)

    def decode_cursor(self, request: Request) -> pagination.Cursor | None:
        """A cursor that cannot be read is the client's mistake: 400, not DRF's 404."""
        try:
            return super().decode_cursor(request)
        except NotFound as unreadable:
            raise InvalidCursor from unreadable

    def get_paginated_response(self, data: Any) -> EnvelopeResponse:
        return success_response(data, pagination=self.pagination_meta())

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
