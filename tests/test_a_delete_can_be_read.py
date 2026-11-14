"""
A delete answers 200 with the envelope, not a 204 with nothing.

A 204 carries no body by definition, so an envelope put in one is thrown
away and the client is left with no message to show and nothing to parse.
"""

from rest_framework.test import APIClient


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
