"""``manage.py example_data`` - products and orders to try the API with."""

from typing import Any

from django.core.management.base import BaseCommand

from shop.models import Order, Product

PRODUCTS = [
    ('Ring', '120.00', 4),
    ('Necklace', '340.00', 2),
    ('Bracelet', '95.50', 0),
    *((f'Earring {number}', '40.00', 10) for number in range(1, 26)),
]


class Command(BaseCommand):
    help = 'Make products and orders to try the example with.'

    def handle(self, *args: Any, **options: Any) -> None:
        for name, price, stock in PRODUCTS:
            Product.objects.get_or_create(name=name, defaults={'price': price, 'stock': stock})

        ring = Product.objects.get(name='Ring')

        if not ring.orders.exists():
            Order.objects.create(product=ring, quantity=1, paid=True)
            Order.objects.create(product=ring, quantity=2)

        self.stdout.write(
            f'{Product.objects.count()} products and {Order.objects.count()} orders are ready.'
        )
