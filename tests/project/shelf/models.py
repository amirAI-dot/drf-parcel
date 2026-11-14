from django.db import models


class Item(models.Model):
    """A row to page through: a name, and when it was made, for a feed's order."""

    name = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name
