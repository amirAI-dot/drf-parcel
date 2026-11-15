"""
Every failure DRF or Django raises answers with the code the contract names,
and keeps the headers DRF puts on it.

If these fail, a client cannot tell "sign in" from "not allowed", or retries
a throttled request at once because ``Retry-After`` was lost.
"""

import base64

import pytest
from django.test import override_settings
from rest_framework.test import APIClient


def test_a_record_that_is_not_there(client: APIClient) -> None:
    response = client.get('/fail/http404/')

    assert response.status_code == 404
    assert response.json()['error_code'] == 'not_found'


def test_a_404_does_not_name_what_was_looked_for(client: APIClient) -> None:
    """Django's text names the model; "is there a patient?" is not the client's to learn."""
    assert 'Patient' not in client.get('/fail/http404/').json()['message']


@pytest.mark.parametrize('how', ['django-permission', 'drf-permission'])
def test_a_caller_who_may_not(client: APIClient, how: str) -> None:
    response = client.get(f'/fail/{how}/')

    assert response.status_code == 403
    assert response.json()['error_code'] == 'permission_denied'


def test_a_refusal_keeps_the_sentence_written_for_it(client: APIClient) -> None:
    """DRF's own handler says it; dropping it told the person less than DRF did."""
    response = client.get('/fail/django-permission-message/')

    assert response.status_code == 403
    assert response.json()['message'] == 'You may only edit your own orders.'


def test_a_refusal_with_no_sentence_says_the_general_one(client: APIClient) -> None:
    assert client.get('/fail/django-permission/').json()['message'] == (
        'You do not have permission to perform this action.'
    )


def test_nobody_signed_in(client: APIClient) -> None:
    response = client.get('/signed-in/')

    assert response.status_code == 401
    assert response.json()['error_code'] == 'not_authenticated'
    assert response['WWW-Authenticate'].startswith('Basic')


def test_credentials_that_are_wrong(client: APIClient, db: None) -> None:
    wrong = base64.b64encode(b'nobody:wrong').decode()

    response = client.get('/signed-in/', HTTP_AUTHORIZATION=f'Basic {wrong}')

    assert response.status_code == 401
    assert response.json()['error_code'] == 'authentication_failed'


def test_a_body_that_is_not_json(client: APIClient) -> None:
    response = client.put('/read-only/', '{not json', content_type='application/json')

    assert response.status_code == 400
    assert response.json()['error_code'] == 'parse_error'


def test_a_body_of_a_type_the_view_does_not_read(client: APIClient) -> None:
    response = client.put('/read-only/', 'a=1', content_type='text/plain')

    assert response.status_code == 415
    assert response.json()['error_code'] == 'unsupported_media_type'


def test_a_method_the_view_has_not_got(client: APIClient) -> None:
    response = client.delete('/read-only/')

    assert response.status_code == 405
    assert response.json()['error_code'] == 'method_not_allowed'
    assert 'GET' in response['Allow']


def test_an_accept_nobody_can_answer(client: APIClient) -> None:
    response = client.get('/read-only/', HTTP_ACCEPT='application/xml')

    assert response.status_code == 406
    assert response.json()['error_code'] == 'not_acceptable'


def test_throttled_says_how_long_to_wait_in_the_body_and_the_header(client: APIClient) -> None:
    response = client.get('/fail/throttled/')

    assert response.status_code == 429
    assert response.json()['error_code'] == 'rate_limited'
    assert response.json()['data'] == {'retry_after': 13}
    assert response['Retry-After'] == '13'


def test_throttled_without_a_wait_says_none(client: APIClient) -> None:
    assert client.get('/fail/throttled-no-wait/').json()['data'] == {}


def test_a_failure_has_no_pagination_and_a_type_of_json(client: APIClient) -> None:
    response = client.get('/fail/domain/')

    assert 'pagination' not in response.json()
    assert response['Content-Type'] == 'application/json'


@override_settings(
    DRF_PARCEL={'ERROR_CODES': {'not_found': 'missing', 'validation_error': 'validation_failed'}}
)
def test_the_project_renames_a_standard_code(client: APIClient) -> None:
    assert client.get('/fail/http404/').json()['error_code'] == 'missing'
    assert client.post('/orders/', {}, format='json').json()['error_code'] == 'validation_failed'


@pytest.mark.parametrize('renamed', [['not_found'], {'not_found': 5}, {'not_found': ''}])
def test_a_renaming_that_cannot_work_never_breaks_the_answer(
    client: APIClient, renamed: object
) -> None:
    """manage.py check reports it; a failure answered meanwhile is still answered."""
    with override_settings(DRF_PARCEL={'ERROR_CODES': renamed}):
        response = client.get('/fail/http404/')

    assert response.status_code == 404
    assert response.json()['error_code'] == 'not_found'


@override_settings(DRF_PARCEL={'ERROR_CODES': {'not_found': 'missing'}})
def test_a_projects_own_code_is_not_renamed(client: APIClient) -> None:
    assert client.get('/fail/domain/').json()['error_code'] == 'province_in_use'


def test_a_refusal_raised_with_the_code_invalid_is_not_called_a_validation_error(
    client: APIClient,
) -> None:
    """A client told validation_error looks for data.fields, and a refusal has none."""
    response = client.get('/fail/refused-as-invalid/')

    assert response.status_code == 403
    assert response.json()['error_code'] == 'invalid'
    assert response.json()['data'] == {}
