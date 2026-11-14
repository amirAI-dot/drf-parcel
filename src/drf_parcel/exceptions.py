"""
A project's own errors, and the common ones the library ships.

A ``DomainError`` is DRF's ``APIException`` with one thing added: ``data``,
what a client can act on - which record is in the way, how long to wait::

    class ProvinceInUse(DomainError):
        status_code = 409
        default_code = 'province_in_use'
        default_detail = _('This province has branches and cannot be deleted.')

    raise ProvinceInUse(data={'branches': 3})

Its names are DRF's own: ``default_code`` is sent as ``error_code``,
``default_detail`` as ``message``. Being an ``APIException``, it answers
sensibly under DRF's own handler too, and a Celery task or a management
command catches it like any other exception.

Where DRF has an exception of the same meaning, the library's is also that
exception - ``NotFoundError`` is a ``NotFound`` - so code that catches DRF's,
and DRF's own handling of it, keep working.
"""

from collections.abc import Mapping
from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class DomainError(exceptions.APIException):
    """A rule of the project was broken, said in the envelope with ``data`` beside it."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_code = 'error'
    default_detail = _('The request could not be completed.')

    def __init__(
        self,
        detail: Any = None,
        code: str | None = None,
        *,
        data: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(detail, code)
        #: What a client can act on. Never what a person must not read elsewhere.
        self.data: dict[str, Any] = dict(data or {})


class InvalidInputError(DomainError):
    """What was sent cannot be used - said by a service, where no serializer is."""

    default_code = 'validation_error'
    default_detail = _('Some of the information provided is not valid.')


class InvalidCursorError(DomainError):
    """A cursor the server cannot read: the client sent back something it was never given."""

    default_code = 'invalid_cursor'
    default_detail = _('The cursor is not valid.')


class AuthenticationFailedError(DomainError, exceptions.AuthenticationFailed):
    """The credentials sent are wrong, or no longer good."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'authentication_failed'
    default_detail = _('Sign in again to continue.')


class PermissionDeniedError(DomainError, exceptions.PermissionDenied):
    """The caller is known, and may not do this."""

    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'permission_denied'
    default_detail = _('You do not have permission to do this.')


class NotFoundError(DomainError, exceptions.NotFound):
    """The record does not exist - or does not exist for this caller."""

    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'not_found'
    default_detail = _('It was not found.')


class ConflictError(DomainError):
    """The request is right, and the state of things refuses it."""

    status_code = status.HTTP_409_CONFLICT
    default_code = 'conflict'
    default_detail = _('This conflicts with a change made in the meantime.')


class RateLimitedError(DomainError):
    """Too many attempts, too quickly. Put ``retry_after`` in ``data`` when it is known."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_code = 'rate_limited'
    default_detail = _('Too many attempts. Please wait and try again.')


class ServiceUnavailableError(DomainError):
    """Something the server depends on is not answering."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = 'service_unavailable'
    default_detail = _('This service is not available right now. Please try again later.')
