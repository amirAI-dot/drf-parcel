"""Views described by the schema tests - one for each thing the schema has to say."""

from typing import Any

from django.urls import path
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, pagination, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.routers import SimpleRouter

from drf_parcel.responses import EnvelopeMixin
from tests.project.shelf.models import Item
from tests.project.shelf.views import (
    Feed,
    ItemSerializer,
    OptedOutFeed,
    OptedOutItemList,
    PlainItemList,
    SizedItemList,
)
from tests.project.views import CsvRenderer


class ItemViewSet(EnvelopeMixin, viewsets.ModelViewSet[Item]):
    """Every action of a viewset over a model, paged by the project's default."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class PlainItemDetail(generics.RetrieveAPIView[Item]):
    """A view without the mixin: what it answers is not wrapped, so neither is its schema."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class OptedOutItemDetail(EnvelopeMixin, generics.RetrieveAPIView[Item]):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    parcel_wrap = False


class CsvItemList(EnvelopeMixin, generics.ListAPIView[Item]):
    """A list read whole, in JSON or as CSV - only the JSON is wrapped."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = None
    renderer_classes = (JSONRenderer, CsvRenderer)


class OwnFailureView(EnvelopeMixin, generics.CreateAPIView[Item]):
    """A view that documents its own 400 - which is kept."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @extend_schema(responses={201: ItemSerializer, 400: OpenApiResponse(description='Our own.')})
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().post(request, *args, **kwargs)


class SilentView(EnvelopeMixin, generics.GenericAPIView[Item]):
    """A success documented with no body, which the mixin still answers in the envelope."""

    serializer_class = ItemSerializer

    @extend_schema(responses={200: None})
    def get(self, request: Request) -> Response:
        return Response()


class LooseListView(EnvelopeMixin, generics.ListAPIView[Item]):
    """A paged list documented by a raw schema: drf-spectacular describes the page inline."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @extend_schema(responses={200: {'type': 'object', 'properties': {'name': {'type': 'string'}}}})
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class DrfPagedItemList(EnvelopeMixin, generics.ListAPIView[Item]):
    """Paged by DRF's own paginator: its bare page is put in the envelope, like any answer."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = pagination.PageNumberPagination


class HiddenView(EnvelopeMixin, generics.RetrieveAPIView[Item]):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @extend_schema(exclude=True)
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


router = SimpleRouter()
router.register('items', ItemViewSet, basename='documented-item')

urlpatterns = [
    path('sized/', SizedItemList.as_view()),
    path('feed/', Feed.as_view()),
    path('plain-list/', PlainItemList.as_view()),
    path('plain/<int:pk>/', PlainItemDetail.as_view()),
    path('opted-out/<int:pk>/', OptedOutItemDetail.as_view()),
    path('csv/', CsvItemList.as_view()),
    path('own-failure/', OwnFailureView.as_view()),
    path('silent/', SilentView.as_view()),
    path('loose/', LooseListView.as_view()),
    path('hidden/<int:pk>/', HiddenView.as_view()),
    path('drf-paged/', DrfPagedItemList.as_view()),
    path('opted-out-list/', OptedOutItemList.as_view()),
    path('opted-out-feed/', OptedOutFeed.as_view()),
    *router.urls,
]
