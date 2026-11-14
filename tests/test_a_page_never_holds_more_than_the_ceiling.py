"""
A client may choose the page size only where a view allows it, and never
above the ceiling.

If these fail, ``?page_size=1000000`` reads a whole table for anybody who
asks - or a client asking for 500 believes it got 500.
"""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from tests.conftest import MakeItems


@pytest.mark.parametrize(
    ('asked', 'used'),
    [
        (None, 3),
        ('4', 4),
        ('5', 5),
        ('500', 5),
        ('0', 3),
        ('-3', 3),
        ('abc', 3),
    ],
)
def test_a_size_the_client_asks_for(
    client: APIClient, make_items: MakeItems, asked: str | None, used: int
) -> None:
    make_items(20)
    query = {} if asked is None else {'page_size': asked}

    answer = client.get('/items/sized/', query).json()

    assert answer['pagination']['page_size'] == used
    assert len(answer['data']) == used


def test_a_view_that_does_not_allow_it_ignores_the_parameter(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(30)

    answer = client.get('/items/', {'page_size': '5'}).json()

    assert answer['pagination']['page_size'] == 20
    assert len(answer['data']) == 20


@override_settings(DRF_PARCEL={'CLIENT_PAGE_SIZE': True, 'MAX_PAGE_SIZE': 25})
def test_the_project_allows_it_for_every_view(client: APIClient, make_items: MakeItems) -> None:
    make_items(30)

    assert client.get('/items/', {'page_size': '7'}).json()['pagination']['page_size'] == 7
    assert client.get('/items/', {'page_size': '99'}).json()['pagination']['page_size'] == 25


@override_settings(DRF_PARCEL={'CLIENT_PAGE_SIZE': True, 'PAGE_SIZE_QUERY_PARAM': 'limit'})
def test_the_project_names_the_parameter(client: APIClient, make_items: MakeItems) -> None:
    make_items(30)

    assert client.get('/items/', {'limit': '7'}).json()['pagination']['page_size'] == 7
    assert client.get('/items/', {'page_size': '7'}).json()['pagination']['page_size'] == 20


@override_settings(DRF_PARCEL={'PAGE_SIZE': 10})
def test_the_project_sets_the_size_a_view_does_not(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(30)

    assert client.get('/items/').json()['pagination']['page_size'] == 10
    assert client.get('/items/sized/').json()['pagination']['page_size'] == 3


@override_settings(DRF_PARCEL={'PAGE_SIZE': 10})
def test_a_paginator_sets_the_size_its_view_does_not(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(30)

    assert client.get('/items/four/').json()['pagination']['page_size'] == 4
