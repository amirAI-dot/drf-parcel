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
