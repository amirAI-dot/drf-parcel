"""
The shop's rules. A view hands off to these; they raise the shop's errors, and
the library's handler says them in the envelope - a rule holds the same whether
it is reached from the API, a command or a task.
"""

from django.db import transaction
from django.db.models import F

from shop.errors import OutOfStockError, StillOrderedError
from shop.models import Order, Product


def place_order(product: Product, quantity: int) -> Order:
    """An order, taken from the stock - or OutOfStockError, saying how many there are."""
    with transaction.atomic():
        locked = Product.objects.select_for_update().get(pk=product.pk)

        if locked.stock < quantity:
            raise OutOfStockError(data={'available': locked.stock})

        Product.objects.filter(pk=locked.pk).update(stock=F('stock') - quantity)
        return Order.objects.create(product=locked, quantity=quantity)


def delete_product(product: Product) -> None:
    """A product with no orders is deleted; one with orders says how many are in the way."""
    orders = product.orders.count()

    if orders:
        raise StillOrderedError(data={'orders': orders})

    product.delete()
