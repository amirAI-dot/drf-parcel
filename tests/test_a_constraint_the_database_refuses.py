"""
A constraint the database refuses is answered by its kind - read from the
driver's code, never from its text - when the project turns the net on.

If these fail, two people taking the same name at once get "server error",
or a column's name from the database's message reaches the client.
"""

import sqlite3

import pytest
from django.db import IntegrityError
from django.test import override_settings
from rest_framework.test import APIClient

from drf_parcel.integrity import kind_of


@pytest.mark.django_db
def test_without_the_net_a_constraint_is_a_bug(client: APIClient) -> None:
    assert client.post('/tags/').json()['error_code'] == 'internal_error'


@pytest.mark.django_db
@override_settings(DRF_PARCEL={'HANDLE_INTEGRITY_ERRORS': True})
def test_a_value_taken_in_the_meantime_already_exists(client: APIClient) -> None:
    response = client.post('/tags/')

    assert response.status_code == 409
    answer = response.json()
    assert answer['error_code'] == 'already_exists'
    assert answer['message'] == 'This already exists.'
    assert b'shelf_tag' not in response.content


@pytest.mark.django_db
@override_settings(DRF_PARCEL={'HANDLE_INTEGRITY_ERRORS': True})
def test_a_value_left_empty_is_still_a_bug(client: APIClient) -> None:
    """A not-null the serializer let through is the server's to fix, not the person's."""
    response = client.put('/tags/')

    assert response.status_code == 500
    assert response.json()['error_code'] == 'internal_error'


def caused_by(cause: BaseException) -> IntegrityError:
    error = IntegrityError('the text is never read')
    error.__cause__ = cause
    return error


class PostgresError(Exception):
    def __init__(self, sqlstate: str) -> None:
        self.sqlstate = sqlstate


class Psycopg2Error(Exception):
    def __init__(self, pgcode: str) -> None:
        self.pgcode = pgcode


def sqlite_error(code: int) -> sqlite3.IntegrityError:
    error = sqlite3.IntegrityError('constraint failed')
    error.sqlite_errorcode = code
    return error


@pytest.mark.parametrize(
    ('cause', 'kind'),
    [
        (PostgresError('23505'), 'unique'),
        (PostgresError('23503'), 'foreign_key'),
        (PostgresError('23502'), 'not_null'),
        (PostgresError('23514'), 'check'),
        (PostgresError('23P01'), None),
        (Psycopg2Error('23505'), 'unique'),
        (sqlite_error(2067), 'unique'),
        (sqlite_error(1555), 'unique'),
        (sqlite_error(787), 'foreign_key'),
        (sqlite_error(1299), 'not_null'),
        (sqlite_error(275), 'check'),
        (Exception(1062, 'Duplicate entry'), 'unique'),
        (Exception(1451, 'Cannot delete'), 'foreign_key'),
        (Exception(1452, 'Cannot add'), 'foreign_key'),
        (Exception(1048, 'cannot be null'), 'not_null'),
        (Exception(3819, 'Check constraint'), 'check'),
        (Exception(9999, 'Something else'), None),
        (Exception('words only'), None),
    ],
)
def test_the_kind_is_read_from_each_drivers_code(cause: BaseException, kind: str | None) -> None:
    assert kind_of(caused_by(cause)) == kind


def test_an_error_with_no_cause_is_of_no_known_kind() -> None:
    assert kind_of(IntegrityError('no cause')) is None


@override_settings(DRF_PARCEL={'HANDLE_INTEGRITY_ERRORS': True})
def test_a_foreign_key_changed_in_the_meantime_is_a_conflict() -> None:
    from rest_framework.test import APIRequestFactory

    from drf_parcel.handlers import exception_handler

    request = APIRequestFactory().get('/')
    response = exception_handler(caused_by(PostgresError('23503')), {'request': request})

    assert response is not None
    assert response.status_code == 409
    assert response.data['error_code'] == 'conflict'
