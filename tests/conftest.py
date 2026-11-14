"""What every test may ask for: a client that speaks to the test project, and rows to page."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import pytest
from rest_framework.test import APIClient

from tests.project.shelf.models import Item

MakeItems = Callable[[int], list[Item]]


@pytest.fixture
def client() -> APIClient:
    """A client that asks for JSON, as a frontend does."""
    return APIClient()


@pytest.fixture
def make_items(db: None) -> MakeItems:
    """``count`` items, named item-1 onwards, each made a minute after the one before."""

    def make(count: int) -> list[Item]:
        start = datetime(2026, 1, 1, tzinfo=UTC)
        return Item.objects.bulk_create(
            Item(name=f'item-{number}', created_at=start + timedelta(minutes=number))
            for number in range(1, count + 1)
        )

    return make
