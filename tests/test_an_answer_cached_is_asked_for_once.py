"""
A view cached with ``cache_page`` is still cached when its answer is wrapped.

If this fails, a list a project cached for an hour - as DRF's documentation
shows, with ``cache_page`` on the method - is read from the database on
every request, and nothing says so.
"""

from collections.abc import Iterator

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from tests.project.views import CountedView


@pytest.fixture(autouse=True)
def _nothing_cached(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(CountedView, 'asked', 0)
    cache.clear()
    yield
    cache.clear()


def test_the_second_request_is_answered_from_the_cache(client: APIClient) -> None:
    first = client.get('/counted/')
    second = client.get('/counted/')

    assert first.json()['data'] == {'asked': 1}
    assert second.json() == first.json()
    assert CountedView.asked == 1


def test_the_cached_answer_is_in_the_envelope_once(client: APIClient) -> None:
    client.get('/counted/')

    assert client.get('/counted/').json() == {
        'success': True,
        'status_code': 200,
        'message': 'Done.',
        'data': {'asked': 1},
    }
