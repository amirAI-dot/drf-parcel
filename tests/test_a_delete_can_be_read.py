"""
A delete answers 200 with the envelope, not a 204 with nothing.

A 204 carries no body by definition, so an envelope put in one is thrown
away and the client is left with no message to show and nothing to parse.
"""

import pytest
from rest_framework.test import APIClient

from drf_parcel.responses import success_response


def test_a_delete_answers_200_with_a_body(client: APIClient) -> None:
    response = client.delete('/rings/1/')

    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'status_code': 200,
        'message': 'Deleted.',
        'data': {},
    }


def test_an_explicit_answer_to_a_delete_says_deleted(client: APIClient) -> None:
    response = client.delete('/totals/')

    assert response.status_code == 200
    assert response.json()['message'] == 'Deleted.'


def test_an_explicit_204_is_answered_as_a_200_with_its_body(client: APIClient) -> None:
    """success_response(status_code=204) built an envelope no client could read."""
    response = client.delete('/no-content/')

    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'status_code': 200,
        'message': 'Deleted.',
        'data': {},
    }


def test_an_explicit_204_without_the_mixin_is_a_200_too(client: APIClient) -> None:
    response = client.delete('/no-content/plain/')

    assert response.status_code == 200
    assert response.json()['status_code'] == 200


def test_a_205_is_left_as_the_view_gave_it(client: APIClient) -> None:
    """A 205 tells the client to clear its form, and has no body to put an envelope in."""
    response = client.post('/reset/')

    assert response.status_code == 205
    assert response.content == b''


def test_success_response_refuses_a_205() -> None:
    with pytest.raises(ValueError, match='205 carries no body'):
        success_response(status_code=205)


def test_an_options_answer_is_in_the_envelope(client: APIClient) -> None:
    """The contract's decision: OPTIONS is a success like any other."""
    answer = client.options('/totals/').json()

    assert answer['success'] is True
    assert answer['data']['name'] == 'Totals'
