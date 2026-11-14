"""
The shop's API - every part of drf-parcel, each where a project puts it.

* ``ProductViewSet`` - numbered pages, a size the client may choose under a
  ceiling, a message of its own for one action, and a custom action that
  answers explicitly.
* ``OrderViewSet`` - a feed read by cursor, newest first; a serializer's
  validation, a domain error with ``data``, and an older-style error.
* ``HealthView`` - a view whose caller expects a shape of its own, left out.
"""

from typing import Any

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_parcel.pagination import CursorPagination
from drf_parcel.responses import EnvelopeMixin, success_response
from shop import services
from shop.errors import PaymentRequiredError
from shop.models import Order, Product


class ProductSerializer(serializers.ModelSerializer[Product]):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock')


class ProductViewSet(EnvelopeMixin, viewsets.ModelViewSet[Product]):
    """Products, a numbered page at a time."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # drf-parcel: the client may send ?page_size=, and never gets more than 20.
    client_page_size = True
    max_page_size = 20

    # drf-parcel: this view's own sentence for one action; the rest say the default.
    envelope_messages = {'create': _('The product was added.')}

    def perform_destroy(self, instance: Product) -> None:
        services.delete_product(instance)

    @action(detail=True, methods=['post'])
    def restock(self, request: Request, pk: str) -> Response:
        """Add to the stock - an answer written by hand, with a message of its own."""
        product = self.get_object()
        product.stock += int(request.data.get('quantity', 0))
        product.save(update_fields=['stock'])
        return success_response(
            ProductSerializer(product).data, message=_('The stock was updated.')
        )


class OrderSerializer(serializers.ModelSerializer[Order]):
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    class Meta:
        model = Order
        fields = ('id', 'product', 'quantity', 'paid', 'created_at')
        read_only_fields = ('paid', 'created_at')

    def create(self, validated_data: dict[str, Any]) -> Order:
        return services.place_order(validated_data['product'], validated_data['quantity'])


class OrderViewSet(
    EnvelopeMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet[Order],
):
    """Orders, as a feed: newest first, read on by cursor."""

    queryset = Order.objects.select_related('product')
    serializer_class = OrderSerializer

    # drf-parcel: this view pages by cursor; every other by number.
    pagination_class = CursorPagination
    ordering = '-created_at'

    @action(detail=True, methods=['get'])
    def receipt(self, request: Request, pk: str) -> Response:
        """A receipt, for a paid order - an error written before the library, unchanged."""
        order = self.get_object()

        if not order.paid:
            raise PaymentRequiredError

        return Response({'order': order.pk, 'total': str(order.quantity * order.product.price)})


class HealthView(EnvelopeMixin, APIView):
    """Asked by a load balancer that expects {"ok": true} - so it stays out of the envelope."""

    parcel_wrap = False

    @extend_schema(responses=inline_serializer('Health', fields={'ok': serializers.BooleanField()}))
    def get(self, request: Request) -> Response:
        return Response({'ok': True})
