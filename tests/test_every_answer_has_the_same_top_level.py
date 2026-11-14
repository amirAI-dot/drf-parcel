"""
A client reads one shape and never special-cases a payload.

If these fail, a frontend that reads ``response.data`` finds the object on
one endpoint and the bare list on the next.
"""

from rest_framework.test import APIClient


def test_a_single_object_is_under_data(client: APIClient) -> None:
    answer = client.get('/rings/1/').json()

    assert answer == {
        'success': True,
        'status_code': 200,
        'message': 'Done.',
        'data': {'id': 1, 'name': 'Ring'},
    }


def test_a_list_is_under_data_too(client: APIClient) -> None:
    answer = client.get('/rings/').json()

    assert answer['data'] == [{'id': 1, 'name': 'Ring'}, {'id': 2, 'name': 'Necklace'}]
    assert answer['success'] is True


def test_a_list_that_is_not_paged_has_no_pagination_key(client: APIClient) -> None:
    assert 'pagination' not in client.get('/rings/').json()


def test_a_success_has_no_error_code(client: APIClient) -> None:
    assert 'error_code' not in client.get('/rings/1/').json()


def test_the_status_in_the_body_is_the_status_of_the_response(client: APIClient) -> None:
    response = client.post('/rings/', {'name': 'Bracelet'}, format='json')

    assert response.status_code == 201
    assert response.json()['status_code'] == 201


def test_a_custom_action_is_wrapped_like_any_other(client: APIClient) -> None:
    answer = client.post('/rings/polish/').json()

    assert answer['data'] == {'polished': 2}
    assert answer['success'] is True


def test_an_answer_that_says_nothing_has_an_empty_object_never_null(client: APIClient) -> None:
    assert client.patch('/explained/').json()['data'] == {}


def test_an_answer_that_is_not_an_object_is_still_under_data(client: APIClient) -> None:
    assert client.put('/explained/').json()['data'] == 'just text'
