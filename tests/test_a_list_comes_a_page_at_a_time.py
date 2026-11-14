"""
A long list comes a page at a time, and says how to ask for the next.

If these fail, a pager on the client draws the wrong number of pages, or a
list that grows every week is read whole on every request.
"""

from rest_framework.test import APIClient

from tests.conftest import MakeItems


def test_a_page_says_where_it_is_in_the_list(client: APIClient, make_items: MakeItems) -> None:
    make_items(45)

    answer = client.get('/items/', {'page': 2}).json()

    assert answer['pagination'] == {
        'type': 'page',
        'count': 45,
        'page': 2,
        'pages': 3,
        'page_size': 20,
        'has_next': True,
        'has_previous': True,
    }
    assert [item['name'] for item in answer['data']][:2] == ['item-21', 'item-22']


def test_the_rows_are_under_data_and_nothing_else_is(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(3)

    answer = client.get('/items/').json()

    assert set(answer) == {'success', 'status_code', 'message', 'data', 'pagination'}
    assert len(answer['data']) == 3
    assert answer['message'] == 'Done.'


def test_the_last_page_has_no_next(client: APIClient, make_items: MakeItems) -> None:
    make_items(45)

    pagination = client.get('/items/', {'page': 3}).json()['pagination']

    assert pagination['has_next'] is False
    assert pagination['has_previous'] is True


def test_an_empty_list_is_one_empty_page(client: APIClient, db: None) -> None:
    answer = client.get('/items/').json()

    assert answer['data'] == []
    assert answer['pagination']['count'] == 0
    assert answer['pagination']['pages'] == 1


def test_a_page_past_the_end_is_not_found(client: APIClient, make_items: MakeItems) -> None:
    make_items(3)

    assert client.get('/items/', {'page': 9}).status_code == 404


def test_a_page_carries_no_links_to_build_on_the_wrong_host(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(45)

    pagination = client.get('/items/').json()['pagination']

    assert 'next' not in pagination
    assert 'previous' not in pagination


def test_a_list_read_whole_on_purpose_has_no_pagination(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(25)

    answer = client.get('/items/unpaged/').json()

    assert len(answer['data']) == 25
    assert 'pagination' not in answer


def test_a_page_is_in_the_envelope_without_the_mixin(
    client: APIClient, make_items: MakeItems
) -> None:
    make_items(3)

    answer = client.get('/items/plain/').json()

    assert answer['success'] is True
    assert answer['pagination']['type'] == 'page'
