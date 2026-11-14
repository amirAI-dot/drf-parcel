"""
The explicit answers work in a view that does not use the mixin.

If these fail, a project that adopts the library one view at a time has to
change every view at once.
"""

from rest_framework.test import APIClient


def test_an_explicit_success_is_in_the_envelope(client: APIClient) -> None:
    assert client.get('/plain/').json() == {
        'success': True,
        'status_code': 200,
        'message': 'Done.',
        'data': {'total': 12},
    }


def test_a_201_says_created_without_knowing_the_method(client: APIClient) -> None:
    assert client.post('/plain/').json()['message'] == 'Created.'


def test_a_bare_answer_is_left_as_it_is(client: APIClient) -> None:
    assert client.put('/plain/').json() == {'total': 12}
