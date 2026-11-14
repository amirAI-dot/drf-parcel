from django.db import models


class Item(models.Model):
    """A row to page through: a name, and when it was made, for a feed's order."""

    name = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ('id',)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """A name that may be held once - for a unique constraint the database keeps."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name
