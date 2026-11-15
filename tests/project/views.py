"""
The views the suite asks: each answers one way a real view can.

A viewset over a list held in memory, so the shape is tested and nothing
about a database is.
"""

from collections.abc import Mapping
from typing import Any, ClassVar

from django.http import FileResponse, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_parcel.responses import EnvelopeMixin, error_response, success_response

RINGS = [{'id': 1, 'name': 'Ring'}, {'id': 2, 'name': 'Necklace'}]


class RingViewSet(EnvelopeMixin, viewsets.ViewSet):
    """Every action of a viewset, answering bare, as DRF's own do."""

    def list(self, request: Request) -> Response:
        return Response(RINGS)

    def retrieve(self, request: Request, pk: str) -> Response:
        return Response(RINGS[0])

    def create(self, request: Request) -> Response:
        return Response({'id': 3, 'name': 'Bracelet'}, status=status.HTTP_201_CREATED)

    def update(self, request: Request, pk: str) -> Response:
        return Response(RINGS[0])

    def partial_update(self, request: Request, pk: str) -> Response:
        return Response(RINGS[0])

    def destroy(self, request: Request, pk: str) -> Response:
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def polish(self, request: Request) -> Response:
        return Response({'polished': 2})


class NamedRingViewSet(RingViewSet):
    """A viewset that names its own messages, for some actions."""

    envelope_messages: ClassVar[Mapping[str, object]] = {
        'create': _('The ring was added.'),
        'polish': _('Polished.'),
    }


class TotalsView(EnvelopeMixin, APIView):
    """A plain view: one explicit answer, one bare, one that names its message by method."""

    envelope_messages: ClassVar[Mapping[str, object]] = {'post': _('Totals were counted.')}

    def get(self, request: Request) -> Response:
        return success_response({'total': 12})

    def post(self, request: Request) -> Response:
        return Response({'total': 12})

    def put(self, request: Request) -> Response:
        return success_response({'total': 12}, message=_('Totals were replaced.'))

    def delete(self, request: Request) -> Response:
        return success_response()


class NoContentView(EnvelopeMixin, APIView):
    """A delete answered explicitly with a 204 - which no client could read."""

    def delete(self, request: Request) -> Response:
        return success_response(status_code=status.HTTP_204_NO_CONTENT)


class PlainNoContentView(APIView):
    """The same, in a view without the mixin."""

    def delete(self, request: Request) -> Response:
        return success_response(status_code=status.HTTP_204_NO_CONTENT)


class ExplainedView(EnvelopeMixin, APIView):
    """Answers that carry a header, a cookie, a failure or a value that is not an object."""

    def get(self, request: Request) -> Response:
        response = Response({'total': 12}, headers={'X-Total': '12'})
        response.set_cookie('seen', 'yes')
        return response

    def post(self, request: Request) -> Response:
        return error_response(
            message=_('This province has branches and cannot be deleted.'),
            error_code='province_in_use',
            status_code=status.HTTP_409_CONFLICT,
            data={'branches': 3},
        )

    def put(self, request: Request) -> Response:
        return Response('just text')

    def patch(self, request: Request) -> Response:
        return Response(None)

    def delete(self, request: Request) -> Response:
        return Response({'detail': 'Made by hand.'}, status=status.HTTP_400_BAD_REQUEST)


class PlainView(APIView):
    """A view with no mixin: only an explicit answer is in the envelope."""

    def get(self, request: Request) -> Response:
        return success_response({'total': 12})

    def post(self, request: Request) -> Response:
        return success_response({'id': 3}, status_code=status.HTTP_201_CREATED)

    def put(self, request: Request) -> Response:
        return Response({'total': 12})


class CountedView(EnvelopeMixin, APIView):
    """An answer that costs something to make, cached as DRF's documentation shows."""

    asked = 0

    @method_decorator(cache_page(60))
    def get(self, request: Request) -> Response:
        type(self).asked += 1
        return Response({'asked': type(self).asked})


class OwnTypeView(EnvelopeMixin, APIView):
    """A view that names the type of its JSON itself, as a versioned API does."""

    def get(self, request: Request) -> Response:
        return Response({'total': 12}, content_type='application/vnd.shop.v2+json')


class OptedOutView(EnvelopeMixin, APIView):
    """A webhook whose caller expects a shape of its own."""

    parcel_wrap = False

    def post(self, request: Request) -> Response:
        return Response({'received': True})


class NotJsonView(EnvelopeMixin, APIView):
    """Answers that are not JSON, one way each."""

    def get(self, request: Request) -> HttpResponse:
        return HttpResponse('plain text', content_type='text/plain')

    def post(self, request: Request) -> HttpResponseRedirect:
        return HttpResponseRedirect('/elsewhere/')

    def put(self, request: Request) -> StreamingHttpResponse:
        return StreamingHttpResponse(iter([b'a', b'b']), content_type='text/plain')

    def patch(self, request: Request) -> FileResponse:
        return FileResponse(iter([b'%PDF-']), content_type='application/pdf')


class CsvRenderer(BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict[str, Any] | None = None,
    ) -> bytes:
        return '\n'.join(','.join(str(value) for value in row.values()) for row in data).encode()


class CsvView(EnvelopeMixin, APIView):
    """A list a client may ask for as CSV or as JSON."""

    renderer_classes = (JSONRenderer, CsvRenderer)

    def get(self, request: Request) -> Response:
        return Response(RINGS)
