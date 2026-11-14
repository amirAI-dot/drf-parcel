"""
A success's message is read off the request, and replaced at three levels.

If these fail, a toast after saving says "Done." where it should say
"Saved.", or a project's own wording is overruled by the library's.
"""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.parametrize(
    ('method', 'path', 'message'),
    [
        ('get', '/rings/', 'Done.'),
        ('get', '/rings/1/', 'Done.'),
        ('post', '/rings/', 'Created.'),
        ('put', '/rings/1/', 'Saved.'),
        ('patch', '/rings/1/', 'Saved.'),
        ('delete', '/rings/1/', 'Deleted.'),
        ('post', '/rings/polish/', 'Done.'),
    ],
)
def test_the_default_message_follows_the_request(
    client: APIClient, method: str, path: str, message: str
) -> None:
    assert getattr(client, method)(path).json()['message'] == message


def test_a_view_names_its_own_message_by_action(client: APIClient) -> None:
    assert client.post('/named-rings/').json()['message'] == 'The ring was added.'
    assert client.post('/named-rings/polish/').json()['message'] == 'Polished.'


def test_an_action_the_view_did_not_name_keeps_the_default(client: APIClient) -> None:
    assert client.delete('/named-rings/1/').json()['message'] == 'Deleted.'


def test_a_plain_view_names_its_own_message_by_method(client: APIClient) -> None:
    assert client.post('/totals/').json()['message'] == 'Totals were counted.'


def test_an_answer_that_names_its_message_says_it(client: APIClient) -> None:
    assert client.put('/totals/').json()['message'] == 'Totals were replaced.'


def test_an_explicit_answer_without_a_message_says_the_requests_default(
    client: APIClient,
) -> None:
    assert client.get('/totals/').json()['message'] == 'Done.'
    assert client.delete('/totals/').json()['message'] == 'Deleted.'


@override_settings(DRF_PARCEL={'MESSAGES': {'created': 'Saved successfully.', 'done': 'OK.'}})
def test_the_project_replaces_a_default(client: APIClient) -> None:
    assert client.post('/rings/').json()['message'] == 'Saved successfully.'
    assert client.get('/rings/').json()['message'] == 'OK.'
    assert client.delete('/rings/1/').json()['message'] == 'Deleted.'


@override_settings(DRF_PARCEL={'MESSAGES': {'created': 'Saved successfully.'}})
def test_a_view_overrules_the_project(client: APIClient) -> None:
    assert client.post('/named-rings/').json()['message'] == 'The ring was added.'


def test_a_failure_keeps_its_own_message(client: APIClient) -> None:
    answer = client.post('/explained/').json()

    assert answer['message'] == 'This province has branches and cannot be deleted.'
