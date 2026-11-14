"""Lists of items, paged each way a project pages them."""

from rest_framework import generics, serializers

from drf_parcel.pagination import CursorPagination, PageNumberPagination
from drf_parcel.responses import EnvelopeMixin
from tests.project.shelf.models import Item


class ItemSerializer(serializers.ModelSerializer[Item]):
    class Meta:
        model = Item
        fields = ('id', 'name')


class ItemList(EnvelopeMixin, generics.ListAPIView[Item]):
    """Numbered pages, by the project's default paginator and page size."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class SizedItemList(ItemList):
    """A view that sets its own size, and lets the client choose under its own ceiling."""

    page_size = 3
    client_page_size = True
    max_page_size = 5


class UnpagedItemList(ItemList):
    """A list read whole, on purpose."""

    pagination_class = None


class PlainItemList(generics.ListAPIView[Item]):
    """Numbered pages in a view without the mixin."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination


class Feed(EnvelopeMixin, generics.ListAPIView[Item]):
    """An endless feed, newest first, by the view's own ordering."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = CursorPagination
    ordering = '-created_at'
    page_size = 2
    client_page_size = True
    max_page_size = 3


class OldestFirstPagination(CursorPagination):
    ordering = 'created_at'


class OldestFirstFeed(EnvelopeMixin, generics.ListAPIView[Item]):
    """A feed whose order is the paginator's, not the view's."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = OldestFirstPagination
    page_size = 2


class FourAPage(PageNumberPagination):
    page_size = 4


class FourAPageItemList(ItemList):
    """A view whose size is its paginator's."""

    pagination_class = FourAPage


class OptedOutItemList(ItemList):
    """A list whose caller expects DRF's own page: the view opts out, its pages too."""

    parcel_wrap = False


class OptedOutFeed(Feed):
    parcel_wrap = False
