"""
Answering in the envelope.

``success_response`` and ``error_response`` answer one request explicitly.
``EnvelopeMixin`` wraps whatever a view returns, once, in
``finalize_response`` - so no handler, ``list``, ``create`` or a custom
``@action``, has to remember.

What is never wrapped: a response that is not JSON (a file, a stream, a
redirect, a page rendered by another renderer), a view that opts out with
``parcel_wrap = False``, and a response already in the envelope.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from drf_parcel.envelope import build_envelope
from drf_parcel.messages import default_message

if TYPE_CHECKING:
    from rest_framework.views import APIView

    _ViewBase = APIView
else:
    _ViewBase = object


class EnvelopeResponse(Response):
    """
    A response whose data is already the envelope.

    Its class is what says so - not the keys in its data, which a view's own
    payload could happen to share.
    """

    #: Whether the message was chosen by whoever answered, rather than by default.
    message_given: bool = True


def success_response(
    data: Any = None,
    *,
    message: object = None,
    status_code: int = status.HTTP_200_OK,
    pagination: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
) -> EnvelopeResponse:
    """
    A success, in the envelope.

    Without a ``message`` it says the default for its status - and, in a
    view with ``EnvelopeMixin``, the default for its request, which also
    knows the method.
    """
    response = EnvelopeResponse(
        build_envelope(
            success=True,
            status_code=status_code,
            message=default_message(None, status_code) if message is None else message,
            data=data,
            pagination=pagination,
        ),
        status=status_code,
        headers=headers,
    )
    response.message_given = message is not None
    return response


def error_response(
    *,
    message: object,
    error_code: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None,
    headers: Mapping[str, str] | None = None,
) -> EnvelopeResponse:
    """A failure, in the envelope."""
    return EnvelopeResponse(
        build_envelope(
            success=False,
            status_code=status_code,
            message=message,
            data=data,
            error_code=error_code,
        ),
        status=status_code,
        headers=headers,
    )


class EnvelopeMixin(_ViewBase):
    """
    Wraps what a view answers in the envelope.

    ``envelope_messages`` names a view's own message for each action - or,
    on a plain ``APIView``, for each method::

        envelope_messages = {'create': _('The product was added.')}
        envelope_messages = {'post': _('Signed in.')}
    """

    #: A message of the view's own, by action or by method in lower case.
    envelope_messages: Mapping[str, object] = {}

    #: False leaves every answer of this view as it is - a webhook, a health check.
    parcel_wrap: bool = True

    # DRF's stubs say Response; at runtime it is any Django response - a file, a
    # redirect - which is why the type is asked before anything is wrapped.
    def finalize_response(
        self, request: Request, response: Response, *args: Any, **kwargs: Any
    ) -> Response:
        if self.parcel_wrap and isinstance(response, Response):
            if isinstance(response, EnvelopeResponse):
                self._say_the_requests_message(request, response)
            elif _is_success(response) and _speaks_json(request):
                response = self._wrap(request, response)

        return super().finalize_response(request, response, *args, **kwargs)

    def envelope_message(self, request: Request, status_code: int) -> object:
        """The message a success of this view says, when the answer chose none."""
        own = self.envelope_messages
        action = getattr(self, 'action', None)

        if action is not None and action in own:
            return own[action]

        method = (request.method or '').lower()

        if method in own:
            return own[method]

        return default_message(request.method, status_code)

    def _wrap(self, request: Request, response: Response) -> EnvelopeResponse:
        """A bare success, put in the envelope."""
        # The message is chosen by the status the view meant - a 204 is a delete.
        message = self.envelope_message(request, response.status_code)

        # A 204 carries no body by definition, so the envelope would be thrown
        # away. Answering 200 is what lets the client read it.
        status_code = (
            status.HTTP_200_OK
            if response.status_code == status.HTTP_204_NO_CONTENT
            else response.status_code
        )
        data = None if response.status_code == status.HTTP_204_NO_CONTENT else response.data

        wrapped = success_response(data, message=message, status_code=status_code)

        # The view's own headers stay - all but the type, which the renderer says.
        for header, value in response.items():
            if header.lower() != 'content-type':
                wrapped[header] = value

        for name, cookie in response.cookies.items():
            wrapped.cookies[name] = cookie

        return wrapped

    def _say_the_requests_message(self, request: Request, response: EnvelopeResponse) -> None:
        """A success that chose no message says the one for its request."""
        envelope = response.data

        if response.message_given or not envelope['success']:
            return

        envelope['message'] = str(self.envelope_message(request, response.status_code))


def _is_success(response: Response) -> bool:
    return status.is_success(response.status_code)


def _speaks_json(request: Request) -> bool:
    """
    Whether the answer is rendered as JSON - or as DRF's browsable page of it.

    A CSV, a PDF or a template is another renderer's shape, and wrapping it
    would break it.
    """
    # A success always follows content negotiation; without one, DRF renders JSON.
    renderer = getattr(request, 'accepted_renderer', None)
    return renderer is None or 'json' in renderer.media_type or renderer.format == 'api'
