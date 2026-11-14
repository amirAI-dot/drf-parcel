"""
The generated OpenAPI document, saying what the wire carries.

drf-spectacular reads serializers, so on its own it documents what is
*inside* the envelope: a frontend generating its types from it writes
``response.id`` where the truth is ``response.data.id``, and finds out at
runtime. This module is installed as the schema class::

    REST_FRAMEWORK = {'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema'}

or, for a project with an ``AutoSchema`` of its own, mixed into it::

    class ProjectSchema(ParcelSchemaMixin, AutoSchema): ...

and it documents:

* every success of a view with ``EnvelopeMixin`` inside the envelope - a
  delete as the 200 it answers, not a bodiless 204;
* a paged list in the envelope of its own kind, page or cursor - the
  paginator says which, in a view with the mixin or without - as
  ``ItemPage`` or ``ItemCursorPage``;
* ``page_size`` only on a view that lets the client choose it, with its
  ceiling (the paginators' own parameters);
* the error envelope as one shared component, the ``default`` answer of
  every operation, and the validation error - with ``data.fields`` - as the
  400 of every operation that takes a body. Only while the project answers
  failures with this library's handler: otherwise its failures are DRF's
  shape, and the schema does not promise another.

A view without the mixin is documented as it answers. One that answers with
``success_response`` by hand is in the envelope at runtime and not here: it
should have the mixin.

This is the only module that imports drf-spectacular: it is the ``schema``
extra, and nothing else needs it.
"""

import inspect
from typing import Any, Final

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import ResolvedComponent
from rest_framework.settings import api_settings

from drf_parcel import conf
from drf_parcel.envelope import envelope_schema
from drf_parcel.handlers import exception_handler
from drf_parcel.pagination import CursorPagination, PageNumberPagination
from drf_parcel.responses import EnvelopeMixin

#: The shared components every operation's failures refer to.
ERROR_COMPONENT: Final = 'ErrorEnvelope'
VALIDATION_ERROR_COMPONENT: Final = 'ValidationErrorEnvelope'

_ERROR_DESCRIPTION: Final = 'A failure, in the envelope. Branch on `error_code`, never `message`.'
_VALIDATION_DESCRIPTION: Final = (
    'What was sent is not valid: the first problem in `message`, every problem in `data.fields`.'
)


class ParcelSchemaMixin:
    """Mixed into an ``AutoSchema``: the envelope, said in the schema."""

    # Set by drf-spectacular before an operation is described.
    view: Any
    registry: Any
    _parcel_pages: set[str]

    def get_operation(self, *args: Any, **kwargs: Any) -> dict[str, Any] | None:
        self._parcel_pages = set()
        operation: dict[str, Any] | None = super().get_operation(*args, **kwargs)  # type: ignore[misc]

        if operation is None:
            return None

        responses = operation['responses']

        if _wraps(self.view):
            _wrap_successes(responses, self._pages())

        if _handler_is_installed():
            self._document_failures(operation, responses)

        return operation

    def get_paginated_name(self, serializer_name: str) -> str:
        """
        The name of a page's component: ``ItemPage``, ``ItemCursorPage``.

        Named apart from drf-spectacular's ``PaginatedItemList``, which a view
        paged by DRF's own paginator still gets - and a view that opts out,
        whose pages are DRF's shape - as their shapes differ. A page of this
        library's is already the whole envelope, so it is remembered and not
        wrapped a second time.
        """
        paginator = self._get_paginator()

        if not isinstance(paginator, PageNumberPagination | CursorPagination) or not (
            paginator.wraps()
        ):
            drf_page: str = super().get_paginated_name(serializer_name)  # type: ignore[misc]
            return drf_page

        if isinstance(paginator, PageNumberPagination):
            name = f'{serializer_name}Page'
        else:
            name = f'{serializer_name}CursorPage'

        self._pages().add(name)
        return name

    def _get_paginator(self) -> Any:
        """The view's paginator, told which view it serves - so it knows if the view opted out."""
        paginator = super()._get_paginator()  # type: ignore[misc]

        if isinstance(paginator, PageNumberPagination | CursorPagination):
            paginator.view = self.view

        return paginator

    def _pages(self) -> set[str]:
        """
        The names of this operation's pages that are already the envelope.

        Kept on the instance, and made when first asked for: drf-spectacular
        may name a page outside ``get_operation``.
        """
        pages: set[str] = vars(self).setdefault('_parcel_pages', set())
        return pages

    def _document_failures(self, operation: dict[str, Any], responses: dict[str, Any]) -> None:
        responses.setdefault(
            'default', _refer(self._component(ERROR_COMPONENT, _error_schema()), _ERROR_DESCRIPTION)
        )

        if 'requestBody' in operation:
            responses.setdefault(
                '400',
                _refer(
                    self._component(VALIDATION_ERROR_COMPONENT, _validation_error_schema()),
                    _VALIDATION_DESCRIPTION,
                ),
            )

    def _component(self, name: str, schema: dict[str, Any]) -> dict[str, str]:
        component = ResolvedComponent(  # type: ignore[no-untyped-call]
            name=name, type=ResolvedComponent.SCHEMA, schema=schema, object=name
        )
        self.registry.register_on_missing(component)
        reference: dict[str, str] = component.ref
        return reference


class ParcelAutoSchema(ParcelSchemaMixin, AutoSchema):
    """drf-spectacular's ``AutoSchema``, saying the envelope."""


def _wraps(view: Any) -> bool:
    """Whether the view's successes are wrapped at runtime - by the mixin, unless it opts out."""
    return isinstance(view, EnvelopeMixin) and view.parcel_wrap


def _handler_is_installed() -> bool:
    """
    Whether failures are answered by this library's handler - directly, or by
    a project's own that calls it and says so with ``functools.wraps``.
    """
    return inspect.unwrap(api_settings.EXCEPTION_HANDLER) is exception_handler


def _wrap_successes(responses: dict[str, Any], pages: set[str]) -> None:
    """Each success inside the envelope, as the mixin answers it."""
    if '204' in responses:
        # The mixin answers a 204 as a 200 with the envelope, so the client can read it.
        responses.setdefault('200', {'description': ''})
        del responses['204']

    for code, response in responses.items():
        if not code.startswith('2'):
            continue

        content = response.setdefault('content', {'application/json': {'schema': {}}})

        for media_type, media in content.items():
            if 'json' not in media_type:
                continue

            inner = media.get('schema', {})

            if not _is_envelope(inner, pages):
                media['schema'] = envelope_schema(inner or {'type': 'object'})


def _is_envelope(schema: dict[str, Any], pages: set[str]) -> bool:
    """A page of this library's, by reference or inline, is already the whole envelope."""
    reference = schema.get('$ref', '')

    if reference:
        return bool(reference.rsplit('/', 1)[-1] in pages)

    return 'success' in schema.get('properties', {})


def _refer(reference: dict[str, str], description: str) -> dict[str, Any]:
    return {
        'description': description,
        'content': {'application/json': {'schema': reference}},
    }


def _error_schema() -> dict[str, Any]:
    return envelope_schema(
        {
            'type': 'object',
            'additionalProperties': True,
            'description': 'What a client can act on - which record is in the way, how long '
            'to wait. Empty when there is nothing.',
        },
        error=True,
    )


def _validation_error_schema() -> dict[str, Any]:
    if conf.get('FIELD_ERRORS') == 'messages':
        problem: dict[str, Any] = {'type': 'string'}
    else:
        problem = {
            'type': 'object',
            'properties': {
                'code': {'type': 'string', 'description': 'required, max_length, unique, ...'},
                'message': {'type': 'string'},
            },
            'required': ['code', 'message'],
        }

    fields = {
        'type': 'object',
        'description': 'Every problem, by the flat path of its field (items.0.quantity).',
        'additionalProperties': {'type': 'array', 'items': problem},
    }
    return envelope_schema(
        {'type': 'object', 'properties': {'fields': fields}, 'required': ['fields']},
        error=True,
    )
