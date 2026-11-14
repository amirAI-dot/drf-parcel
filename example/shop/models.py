"""A shop: products with a stock, and the orders that take from it."""

from django.db import models


class Product(models.Model):
    """Something to sell. A name is held once - the database keeps that, too."""

    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    """An order of one product, newest first - read as a feed, by cursor."""

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quantity = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.quantity} x {self.product}'
