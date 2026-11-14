"""
A feed is read by cursor: the client sends back what it was given.

If these fail, "load more" repeats a row or skips one, or a client sending
back a mangled cursor is told the list does not exist.
"""

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
    assert response.data['detail'].code == 'invalid_cursor'


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
