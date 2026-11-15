"""
A failure answered undoes what the request wrote.

If this fails, a project with ``ATOMIC_REQUESTS`` keeps half a write behind
an error the client was told about - a payment recorded for an order that
was refused.

And a failure a view returns - ``error_response`` - is a failure all the
same: raising it or returning it, the client was told no.
"""

import pytest
from django.db import connection
from rest_framework.test import APIClient

from tests.project.shelf.models import Item


@pytest.mark.django_db(transaction=True)
def test_a_domain_error_rolls_the_request_back(
    client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(connection.settings_dict, 'ATOMIC_REQUESTS', True)

    response = client.get('/fail/write-then-fail/')

    assert response.status_code == 409
    assert not Item.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_a_failure_returned_by_hand_rolls_the_request_back_too(
    client: APIClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(connection.settings_dict, 'ATOMIC_REQUESTS', True)

    response = client.post('/refused/')

    assert response.status_code == 409
    assert not Item.objects.exists()
