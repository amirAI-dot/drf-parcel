"""
A validation error says the first problem in ``message`` and every problem in
``data.fields`` - each with its code, at a flat path.

If these fail, a form marks one field when three are wrong, a client cannot
tell "empty" from "too long" without reading translated text, or the second
item's quantity cannot be told from the first's.
"""

from typing import Any

from django.test import override_settings
from rest_framework.test import APIClient


def fields(answer: dict[str, Any]) -> dict[str, Any]:
    return answer['data']['fields']  # type: ignore[no-any-return]


def test_every_field_that_is_wrong_with_its_code(client: APIClient) -> None:
    order = {'name': 'far too long', 'items': [{'quantity': 1}, {'quantity': 0}]}

    response = client.post('/orders/', order, format='json')

    assert response.status_code == 400
    answer = response.json()
    assert answer['error_code'] == 'validation_error'
    assert fields(answer) == {
        'name': [
            {'code': 'max_length', 'message': 'Ensure this field has no more than 5 characters.'}
        ],
        'items.1.quantity': [
            {'code': 'min_value', 'message': 'Ensure this value is greater than or equal to 1.'}
        ],
    }


def test_the_message_is_the_first_problem(client: APIClient) -> None:
    order = {'name': 'far too long', 'items': [{'quantity': 0}]}

    answer = client.post('/orders/', order, format='json').json()

    assert answer['message'] == 'Ensure this field has no more than 5 characters.'


def test_a_field_left_out_is_required(client: APIClient) -> None:
    answer = client.post('/orders/', {}, format='json').json()

    assert fields(answer)['name'] == [{'code': 'required', 'message': 'This field is required.'}]


def test_a_problem_of_no_field_is_under_non_field_errors(client: APIClient) -> None:
    order = {'name': 'late', 'items': [{'quantity': 1}]}

    answer = client.post('/orders/', order, format='json').json()

    assert fields(answer) == {
        'non_field_errors': [{'code': 'invalid', 'message': 'The dates are the wrong way round.'}]
    }


def test_a_list_of_records_is_told_apart_by_position(client: APIClient) -> None:
    orders = [{'name': 'ok', 'items': []}, {'items': []}]

    answer = client.post('/orders/many/', orders, format='json').json()

    assert list(fields(answer)) == ['1.name']


@override_settings(DRF_PARCEL={'FIELD_ERRORS': 'messages'})
def test_the_project_asks_for_the_messages_alone(client: APIClient) -> None:
    answer = client.post('/orders/', {'items': []}, format='json').json()

    assert fields(answer) == {'name': ['This field is required.']}


@override_settings(DRF_PARCEL={'FIELD_PATH_SEPARATOR': '/'})
def test_the_project_joins_a_path_its_own_way(client: APIClient) -> None:
    order = {'name': 'ok', 'items': [{'quantity': 0}]}

    assert list(fields(client.post('/orders/', order, format='json').json())) == [
        'items/0/quantity'
    ]


def test_a_django_validation_error_reads_back_the_same_way(client: APIClient) -> None:
    response = client.get('/fail/django-validation/')

    assert response.status_code == 400
    assert fields(response.json()) == {
        'phone': [{'code': 'invalid', 'message': 'Enter a valid phone number.'}]
    }


def test_a_django_validation_error_of_no_field(client: APIClient) -> None:
    answer = client.get('/fail/django-validation-plain/').json()

    assert answer['message'] == 'The dates are the wrong way round.'
    assert list(fields(answer)) == ['non_field_errors']


def test_a_validation_error_with_nothing_in_it_still_says_something(client: APIClient) -> None:
    answer = client.get('/fail/empty-validation/').json()

    assert answer['message'] == 'Some of the information provided is not valid.'
    assert fields(answer) == {}


def test_a_list_of_records_in_the_shape_older_drf_gives(client: APIClient) -> None:
    """Before DRF 3.18, a list's errors were a list with an entry per record."""
    answer = client.get('/fail/list-validation/').json()

    assert fields(answer) == {
        '1.name': [{'code': 'required', 'message': 'This field is required.'}]
    }
