"""
A feed is read by cursor: the client sends back what it was given.

If these fail, "load more" repeats a row or skips one, a client sending
back a mangled cursor is told the list does not exist - or anybody who can
write a cursor by hand fills the error log with bugs that are not bugs.
"""

import logging
from base64 import b64encode
from typing import Any

import pytest
from rest_framework.test import APIClient

from tests.conftest import MakeItems


def names(answer: dict[str, object]) -> list[str]:
    return [row['name'] for row in answer['data']]  # type: ignore[attr-defined,index]


def test_the_first_page_says_how_to_ask_for_the_next(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(5)

    answer = client.get('/feed/').json()

    assert names(answer) == ['item-5', 'item-4']
    pagination = answer['pagination']
    assert pagination['type'] == 'cursor'
    assert pagination['page_size'] == 2
    assert pagination['has_next'] is True
    assert pagination['has_previous'] is False
    assert pagination['previous_cursor'] is None
    assert isinstance(pagination['next_cursor'], str)
    assert set(pagination) == {
        'type',
        'next_cursor',
        'previous_cursor',
        'page_size',
        'has_next',
        'has_previous',
    }


def test_the_cursor_sent_back_reads_on_without_repeating(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(5)
    first = client.get('/feed/').json()

    second = client.get('/feed/', {'cursor': first['pagination']['next_cursor']}).json()
    third = client.get('/feed/', {'cursor': second['pagination']['next_cursor']}).json()

    assert names(second) == ['item-3', 'item-2']
    assert names(third) == ['item-1']
    assert third['pagination']['has_next'] is False
    assert third['pagination']['next_cursor'] is None


def test_the_previous_cursor_reads_back(client: APIClient, make_items: MakeItems) -> None:
    make_items(5)
    first = client.get('/feed/').json()
    second = client.get('/feed/', {'cursor': first['pagination']['next_cursor']}).json()

    back = client.get('/feed/', {'cursor': second['pagination']['previous_cursor']}).json()

    assert names(back) == ['item-5', 'item-4']


def test_a_cursor_has_no_count_and_no_page(client: APIClient, make_items: MakeItems) -> None:
    make_items(5)

    pagination = client.get('/feed/').json()['pagination']

    assert 'count' not in pagination
    assert 'page' not in pagination


def test_a_cursor_the_server_cannot_read_is_the_clients_mistake(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(5)

    response = client.get('/feed/', {'cursor': 'not a cursor'})

    assert response.status_code == 400
    assert response.json()['error_code'] == 'invalid_cursor'


def by_hand(inside: str) -> str:
    """A cursor nobody was given: well formed, saying whatever its writer liked."""
    return b64encode(inside.encode()).decode()


def test_a_cursor_whose_position_is_no_number_is_the_clients_mistake(
    client: APIClient, make_items: MakeItems, caplog: pytest.LogCaptureFixture
) -> None:
    make_items(5)

    response = client.get('/feed/by-number/', {'cursor': by_hand('p=abc')})

    assert response.status_code == 400
    assert response.json()['error_code'] == 'invalid_cursor'
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


def test_a_cursor_whose_position_is_no_date_is_an_invalid_cursor_not_a_form(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(5)

    answer = client.get('/feed/', {'cursor': by_hand('p=abc')}).json()

    assert answer['error_code'] == 'invalid_cursor'
    assert answer['data'] == {}


def test_a_cursor_kept_while_the_order_changes_is_refused_not_a_bug(
    client: APIClient, make_items: MakeItems
) -> None:
    """A table re-sorted by another column, by a client that kept the old cursor."""
    make_items(5)
    given = client.get('/feed/sortable/').json()['pagination']['next_cursor']

    response = client.get('/feed/sortable/', {'cursor': given, 'ordering': 'id'})

    assert response.status_code == 400
    assert response.json()['error_code'] == 'invalid_cursor'


def test_a_cursor_holding_a_character_the_database_refuses_is_not_a_bug(
    client: APIClient, make_items: MakeItems
) -> None:
    """PostgreSQL refuses a NUL in text; SQLite reads on. Neither is a 500."""
    make_items(5)

    response = client.get('/feed/sortable/', {'cursor': by_hand('p=a%00b'), 'ordering': 'name'})

    assert response.status_code in (200, 400)


def test_a_feed_asked_for_without_a_cursor_is_its_first_page(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(5)

    assert names(client.get('/feed/by-number/').json()) == ['item-5', 'item-4']


def test_the_client_chooses_a_size_under_the_ceiling(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(5)

    assert len(client.get('/feed/', {'page_size': '3'}).json()['data']) == 3
    assert client.get('/feed/', {'page_size': '9'}).json()['pagination']['page_size'] == 3


def test_the_order_is_the_paginators_when_the_view_names_none(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(5)

    assert names(client.get('/feed/oldest-first/').json()) == ['item-1', 'item-2']


def test_a_cursor_changed_by_hand_is_refused(client: APIClient, make_items: MakeItems) -> None:
    """A signed cursor with one character changed is not the cursor the server gave."""
    make_items(5)
    given = client.get('/feed/').json()['pagination']['next_cursor']
    changed = given[:-1] + ('A' if given[-1] != 'A' else 'B')

    response = client.get('/feed/', {'cursor': changed})

    assert response.status_code == 400
    assert response.json()['error_code'] == 'invalid_cursor'


def test_a_cursor_signed_with_another_key_is_refused(
    client: APIClient, make_items: MakeItems, settings: Any
) -> None:
    make_items(5)
    given = client.get('/feed/').json()['pagination']['next_cursor']
    settings.SECRET_KEY = 'a-key-the-cursor-was-not-signed-with'

    assert client.get('/feed/', {'cursor': given}).json()['error_code'] == 'invalid_cursor'


def test_a_key_rotated_with_fallbacks_keeps_the_cursors_given(
    client: APIClient, make_items: MakeItems, settings: Any
) -> None:
    """Django's SECRET_KEY_FALLBACKS: a client paging through a feed is not cut off."""
    make_items(5)
    given = client.get('/feed/').json()['pagination']['next_cursor']
    settings.SECRET_KEY_FALLBACKS = [settings.SECRET_KEY]
    settings.SECRET_KEY = 'the-new-key'

    assert names(client.get('/feed/', {'cursor': given}).json()) == ['item-3', 'item-2']


def test_a_bug_while_a_feed_is_read_is_a_bug_cursor_or_not(
    client: APIClient, make_items: MakeItems, caplog: pytest.LogCaptureFixture
) -> None:
    """
    A good cursor, and rows the project's own code cannot read: a 500, logged -
    never mistaken for the client's cursor, which would hide the bug.
    """
    make_items(5)
    given = client.get('/feed/').json()['pagination']['next_cursor']

    with caplog.at_level(logging.ERROR, logger='drf_parcel'):
        response = client.get('/feed/broken/', {'cursor': given})

    assert response.status_code == 500
    assert response.json()['error_code'] == 'internal_error'
    assert [record for record in caplog.records if record.name == 'drf_parcel']
