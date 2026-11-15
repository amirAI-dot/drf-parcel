"""
An unexpected exception answers a generic 500, and its text never leaves
the server - it is logged and reported instead.

If these fail, a query with a patient's phone number in it is sent to
whoever caused the bug, or the bug is answered and nobody hears of it.
"""

import logging
from typing import Any

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

REPORTED: list[Exception] = []


def reporter(exc: Exception, context: dict[str, Any]) -> None:
    REPORTED.append(exc)


def failing_reporter(exc: Exception, context: dict[str, Any]) -> None:
    raise ConnectionError('the reporting service is down')


def test_a_bug_answers_500_saying_nothing(client: APIClient) -> None:
    response = client.get('/fail/bug/')

    assert response.status_code == 500
    assert response.json() == {
        'success': False,
        'status_code': 500,
        'message': 'Something went wrong. Please try again.',
        'data': {},
        'error_code': 'internal_error',
    }
    assert b'09120000000' not in response.content


def test_a_bug_is_logged_with_its_traceback(
    client: APIClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.ERROR, logger='drf_parcel'):
        client.get('/fail/bug/')

    [record] = [record for record in caplog.records if record.name == 'drf_parcel']
    assert record.levelno == logging.ERROR
    assert 'FailingView' in record.getMessage()
    assert record.exc_info is not None


def test_a_failure_somebody_designed_is_not_logged_as_an_error(
    client: APIClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.ERROR, logger='drf_parcel'):
        client.get('/fail/domain/')
        client.get('/fail/http404/')

    assert [record for record in caplog.records if record.name == 'drf_parcel'] == []


@override_settings(DEBUG=True)
def test_under_debug_a_bug_is_raised_for_djangos_page(client: APIClient) -> None:
    with pytest.raises(RuntimeError, match='SELECT'):
        client.get('/fail/bug/')


@override_settings(DEBUG=True, DRF_PARCEL={'RAISE_UNHANDLED_IN_DEBUG': False})
def test_under_debug_the_project_may_ask_for_the_envelope_still(client: APIClient) -> None:
    assert client.get('/fail/bug/').json()['error_code'] == 'internal_error'


@override_settings(DRF_PARCEL={'REPORTER': 'tests.test_a_bug_never_tells_its_secrets.reporter'})
def test_a_bug_is_handed_to_the_reporter(client: APIClient) -> None:
    REPORTED.clear()

    client.get('/fail/bug/')

    [reported] = REPORTED
    assert isinstance(reported, RuntimeError)


@override_settings(DRF_PARCEL={'REPORTER': 'tests.test_a_bug_never_tells_its_secrets.reporter'})
def test_a_designed_failure_is_not_reported(client: APIClient) -> None:
    REPORTED.clear()

    client.get('/fail/domain/')

    assert REPORTED == []


@override_settings(
    DRF_PARCEL={'REPORTER': 'tests.test_a_bug_never_tells_its_secrets.failing_reporter'}
)
def test_a_reporter_that_fails_costs_a_log_line_not_the_answer(
    client: APIClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.ERROR, logger='drf_parcel'):
        response = client.get('/fail/bug/')

    assert response.status_code == 500
    assert any('REPORTER' in record.getMessage() for record in caplog.records)


@override_settings(DRF_PARCEL={'REPORTER': 'tests.test_a_bug_never_tells_its_secrets.reporter'})
@pytest.mark.parametrize(
    ('how', 'status_code', 'code'),
    [('designed-500', 500, 'upstream_failed'), ('designed-503', 503, 'service_unavailable')],
)
def test_a_5xx_raised_on_purpose_is_logged_and_reported_too(
    client: APIClient, caplog: pytest.LogCaptureFixture, how: str, status_code: int, code: str
) -> None:
    """
    The server failing is the server failing, raised on purpose or not: nobody
    hears of a payment provider that stopped answering if it is never logged.
    """
    REPORTED.clear()

    with caplog.at_level(logging.ERROR, logger='drf_parcel'):
        response = client.get(f'/fail/{how}/')

    assert response.status_code == status_code
    assert response.json()['error_code'] == code
    [record] = [record for record in caplog.records if record.name == 'drf_parcel']
    assert record.getMessage() == f'A {status_code} answered in FailingView'
    assert record.exc_info is not None
    assert len(REPORTED) == 1


def test_a_5xx_raised_on_purpose_says_the_sentence_it_was_raised_with(
    client: APIClient,
) -> None:
    """A designed 5xx is not a bug's text: its sentence was written to be read."""
    assert client.get('/fail/designed-500/').json()['message'] == (
        'The payment provider did not answer.'
    )
