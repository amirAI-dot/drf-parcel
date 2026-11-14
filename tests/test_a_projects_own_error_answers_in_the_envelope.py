"""
A project's own error - the library's kind or one written before it - answers
in the envelope, with its status, its code and what a client can act on.

If these fail, a client branching on ``province_in_use`` finds a generic
code, or the record in the way is not in the answer.
"""

from rest_framework.test import APIClient


def test_a_domain_error_says_its_code_message_and_data(client: APIClient) -> None:
    response = client.get('/fail/domain/')

    assert response.status_code == 409
    assert response.json() == {
        'success': False,
        'status_code': 409,
        'message': 'This province has branches and cannot be deleted.',
        'data': {'branches': 3},
        'error_code': 'province_in_use',
    }


def test_a_message_given_where_it_is_raised_is_the_one_said(client: APIClient) -> None:
    assert client.get('/fail/domain-message/').json()['message'] == 'Move its 3 branches first.'


def test_a_code_given_where_it_is_raised_is_the_one_sent(client: APIClient) -> None:
    assert client.get('/fail/domain-code/').json()['error_code'] == 'province_locked'


def test_an_error_written_before_the_library_needs_no_change(client: APIClient) -> None:
    response = client.get('/fail/legacy/')

    assert response.status_code == 402
    assert response.json() == {
        'success': False,
        'status_code': 402,
        'message': 'Pay first.',
        'data': {},
        'error_code': 'payment_required',
    }


def test_an_older_error_that_carries_data_sends_it(client: APIClient) -> None:
    assert client.get('/fail/legacy-data/').json()['data'] == {'amount': 12}


def test_an_error_whose_detail_is_a_dictionary_says_its_first_sentence(client: APIClient) -> None:
    assert client.get('/fail/legacy-dict/').json()['message'] == 'Too little.'


def test_an_error_with_an_empty_detail_says_its_class_sentence(client: APIClient) -> None:
    assert client.get('/fail/legacy-empty/').json()['message'] == 'Pay first.'
