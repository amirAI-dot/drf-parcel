"""
The exception handler: every failure a DRF view raises, answered in the envelope.

    REST_FRAMEWORK = {'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler'}

What it recognises, in order:

1. Django's own ``Http404``, ``PermissionDenied`` and ``ValidationError``,
   turned into DRF's.
2. A validation error - the first problem in ``message``, every problem in
   ``data.fields``, each with its code and a flat path.
3. Any ``APIException`` - DRF's, the library's, a project's own: its status,
   its code as ``error_code``, its detail as ``message``, its ``data``.
   DRF's own handler runs first, so the headers it adds - ``Retry-After``,
   ``WWW-Authenticate`` - stay on the answer.
4. An ``IntegrityError``, when ``HANDLE_INTEGRITY_ERRORS`` is on: a unique
   or foreign-key constraint is a 409; every other is a bug.
5. Anything else - a bug. A generic 500 whose text never leaves the server,
   logged with its traceback and reported. Under ``DEBUG`` it is raised
   instead, so Django's page shows it.

Every 5xx answered - a designed one too - is logged and reported, and
every failure answered marks the request's transaction for rollback.
"""

import logging
from collections.abc import Callable, Mapping
from functools import cache
from typing import Any, Final

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.fields import get_error_detail
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler as drf_exception_handler

from drf_parcel import conf
from drf_parcel.integrity import kind_of
from drf_parcel.responses import EnvelopeResponse, error_response

logger = logging.getLogger('drf_parcel')

#: Every code the library sends by itself - the ones ERROR_CODES may rename.
STANDARD_CODES: Final = (
    'validation_error',
    'parse_error',
    'invalid_cursor',
    'not_authenticated',
    'authentication_failed',
    'permission_denied',
    'not_found',
    'method_not_allowed',
    'not_acceptable',
    'already_exists',
    'conflict',
    'unsupported_media_type',
    'rate_limited',
    'internal_error',
    'service_unavailable',
)

#: DRF's own code the contract names otherwise. A validation error's is not
#: here: it is named where a validation error is answered, so a refusal that
#: happens to carry the code 'invalid' is not mistaken for a form.
_RENAMED_FROM_DRF: Final = {'throttled': 'rate_limited'}

_ALREADY_EXISTS = _('This already exists.')
_CHANGED_MEANWHILE = _('This was changed in the meantime. Please try again.')
_SOMETHING_WENT_WRONG = _('Something went wrong. Please try again.')
_NOT_VALID = _('Some of the information provided is not valid.')


def exception_handler(exc: Exception, context: Mapping[str, Any]) -> Response | None:
    """Turn anything a DRF view raised into the envelope - or, under DEBUG, let a bug through."""
    exc = _as_drf(exc)
    answered = drf_exception_handler(exc, dict(context))

    if answered is not None:
        assert isinstance(exc, exceptions.APIException)

        if answered.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            # A 5xx somebody raised on purpose is still the server failing:
            # it is logged and reported, though it says what it was raised with.
            _record(exc, context, f'A {answered.status_code} answered in %s')

        return _carry_headers(answered, _answer_to(exc, answered.status_code))

    if isinstance(exc, IntegrityError) and conf.get('HANDLE_INTEGRITY_ERRORS'):
        kind = kind_of(exc)

        if kind == 'unique':
            return _failure('already_exists', _ALREADY_EXISTS, status.HTTP_409_CONFLICT)

        if kind == 'foreign_key':
            return _failure('conflict', _CHANGED_MEANWHILE, status.HTTP_409_CONFLICT)

    return _unexpected(exc, context)


def _as_drf(exc: Exception) -> Exception:
    """Django's own failures, as the DRF exceptions of the same meaning."""
    if isinstance(exc, Http404):
        return exceptions.NotFound()

    if isinstance(exc, DjangoPermissionDenied):
        # A message somebody wrote for the person refused is said, as DRF says it;
        # Http404's is not, because Django's names the model that was looked for.
        return exceptions.PermissionDenied(exc.args[0] if exc.args else None)

    if isinstance(exc, DjangoValidationError):
        # The codes Django gave each message - 'required', 'unique' - are kept.
        detail = get_error_detail(exc)

        if isinstance(detail, dict) and NON_FIELD_ERRORS in detail:
            # A model's clean() files what belongs to no field under Django's
            # key, '__all__'; a client reads it under DRF's, as from a serializer.
            own = str(api_settings.NON_FIELD_ERRORS_KEY)
            detail = {
                (own if key == NON_FIELD_ERRORS else key): found for key, found in detail.items()
            }

        return exceptions.ValidationError(detail)

    return exc


def _answer_to(exc: exceptions.APIException, status_code: int) -> EnvelopeResponse:
    if isinstance(exc, exceptions.ValidationError):
        problems = _field_problems(exc.detail)
        first = next((message for found in problems.values() for _code, message in found), None)
        return _failure(
            'validation_error',
            _NOT_VALID if first is None else first,
            status_code,
            data={'fields': _shaped(problems)},
        )

    data: dict[str, Any] = {}
    own = getattr(exc, 'data', None)

    if isinstance(own, Mapping):
        data.update(own)

    wait = getattr(exc, 'wait', None) if isinstance(exc, exceptions.Throttled) else None

    if wait is not None:
        # DRF has already rounded it up to the whole seconds of its Retry-After header.
        data['retry_after'] = int(wait)

    message = _first_message(exc.detail) or exc.default_detail
    return _failure(_code_of(exc), message, status_code, data=data)


def _code_of(exc: exceptions.APIException) -> str:
    """
    The exception's own code: the one it was raised with, else its class's -
    else DRF's own, for a class that names none: a failure is never without one.
    """
    code = (
        getattr(exc.detail, 'code', None)
        or exc.default_code
        or exceptions.APIException.default_code
    )
    return _RENAMED_FROM_DRF.get(code, code)


def _first_message(detail: Any) -> str:
    """One sentence out of DRF's detail, which may be a list or a dictionary of them."""
    if isinstance(detail, Mapping):
        return _first_message(next(iter(detail.values()), ''))

    if isinstance(detail, list):
        return _first_message(detail[0]) if detail else ''

    return str(detail)


Problems = dict[str, list[tuple[str, str]]]


def _field_problems(detail: Any) -> Problems:
    """
    Every problem DRF found, by the flat path of the field it belongs to.

    A nested serializer's field is ``items.0.quantity``; a problem that
    belongs to no field is under DRF's ``NON_FIELD_ERRORS_KEY``.
    """
    problems: Problems = {}
    separator = str(conf.get('FIELD_PATH_SEPARATOR'))

    def walk(found: Any, path: str) -> None:
        if isinstance(found, Mapping):
            for key, inner in found.items():
                walk(inner, f'{path}{separator}{key}' if path else str(key))
        elif isinstance(found, list):
            for index, inner in enumerate(found):
                if isinstance(inner, Mapping | list):
                    walk(inner, f'{path}{separator}{index}' if path else str(index))
                else:
                    walk(inner, path)
        else:
            key = path or str(api_settings.NON_FIELD_ERRORS_KEY)
            code = getattr(found, 'code', None) or 'invalid'
            problems.setdefault(key, []).append((code, str(found)))

    walk(detail, '')
    return problems


def _shaped(problems: Problems) -> dict[str, list[Any]]:
    """Each problem as ``{code, message}``, or as its message alone, as the project chose."""
    if conf.get('FIELD_ERRORS') == 'messages':
        return {path: [message for _code, message in found] for path, found in problems.items()}

    return {
        path: [{'code': code, 'message': message} for code, message in found]
        for path, found in problems.items()
    }


def _unexpected(exc: Exception, context: Mapping[str, Any]) -> Response | None:
    """A bug: raised under DEBUG; otherwise logged, reported and answered with nothing in it."""
    if settings.DEBUG and conf.get('RAISE_UNHANDLED_IN_DEBUG'):
        return None

    _record(exc, context, 'Unhandled exception in %s')
    return _failure('internal_error', _SOMETHING_WENT_WRONG, status.HTTP_500_INTERNAL_SERVER_ERROR)


def _record(exc: Exception, context: Mapping[str, Any], what: str) -> None:
    """A 5xx, logged with its traceback and handed to the reporter."""
    view = context.get('view')
    logger.error(what, type(view).__name__ if view else 'a view', exc_info=exc)
    _report(exc, context)


def _report(exc: Exception, context: Mapping[str, Any]) -> None:
    """Hand the bug to the project's reporter; one that fails costs a log line, not the answer."""
    path = conf.get('REPORTER')

    if not path:
        return

    try:
        _reporter(str(path))(exc, context)
    except Exception:
        logger.exception('The REPORTER %s failed', path)


@cache
def _reporter(path: str) -> Callable[[Exception, Mapping[str, Any]], object]:
    reporter: Callable[[Exception, Mapping[str, Any]], object] = import_string(path)
    return reporter


def _failure(
    code: str,
    message: object,
    status_code: int,
    *,
    data: Mapping[str, Any] | None = None,
) -> EnvelopeResponse:
    """
    A failure in the envelope, under the project's name for its code - and its
    write undone: ``error_response`` marks the transaction for rollback.
    """
    return error_response(
        message=message,
        error_code=_renamed(code),
        status_code=status_code,
        data=dict(data or {}),
    )


def _renamed(code: str) -> str:
    """
    The project's name for a code, from ``ERROR_CODES``.

    A renaming that cannot work - reported by ``manage.py check`` - is passed
    over rather than allowed to break the answer to a failure.
    """
    renamed = conf.get('ERROR_CODES')
    new = renamed.get(code) if isinstance(renamed, Mapping) else None
    return new if isinstance(new, str) and new else code


def _carry_headers(answered: Response, response: EnvelopeResponse) -> EnvelopeResponse:
    """The headers DRF's own handler put on its answer - Retry-After, WWW-Authenticate."""
    for header, value in answered.items():
        if header.lower() != 'content-type':
            response[header] = value

    return response
