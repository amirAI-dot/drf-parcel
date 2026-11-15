"""
A setting that cannot work is reported by ``manage.py check``.

If these fail, a ceiling below the page size, a page size of "20" or a
reporter that does not import is found by the first request that needs it,
not by whoever deployed it.
"""

import pytest
from django.core.checks import Error
from django.test import override_settings

from drf_parcel.checks import check_settings


def ids(problems: list[Error]) -> list[str | None]:
    return [problem.id for problem in problems]


def test_the_defaults_are_sound() -> None:
    assert check_settings() == []


@override_settings(DRF_PARCEL={'PAGE_SZIE': 20})
def test_an_unknown_key_is_reported() -> None:
    problems = check_settings()

    assert ids(problems) == ['drf_parcel.E001']
    assert 'PAGE_SZIE' in problems[0].msg


@override_settings(DRF_PARCEL={'MESSAGES': {'creatd': 'Saved.'}})
def test_an_unknown_message_key_is_reported() -> None:
    assert ids(check_settings()) == ['drf_parcel.E001']


@pytest.mark.parametrize('size', [0, -5, '20', True, 2.5])
def test_a_page_size_that_is_not_a_positive_whole_number(size: object) -> None:
    with override_settings(DRF_PARCEL={'PAGE_SIZE': size}):
        assert ids(check_settings()) == ['drf_parcel.E002']


@override_settings(DRF_PARCEL={'MAX_PAGE_SIZE': 0})
def test_a_ceiling_that_is_not_a_positive_whole_number() -> None:
    assert ids(check_settings()) == ['drf_parcel.E002']


@override_settings(DRF_PARCEL={'PAGE_SIZE': 50, 'MAX_PAGE_SIZE': 10})
def test_a_ceiling_below_the_page_size() -> None:
    assert ids(check_settings()) == ['drf_parcel.E003']


@override_settings(DRF_PARCEL={'CLIENT_PAGE_SIZE': 'yes'})
def test_client_page_size_that_is_not_true_or_false() -> None:
    assert ids(check_settings()) == ['drf_parcel.E004']


@pytest.mark.parametrize('param', ['', 5])
def test_a_query_parameter_with_no_name(param: object) -> None:
    with override_settings(DRF_PARCEL={'PAGE_SIZE_QUERY_PARAM': param}):
        assert ids(check_settings()) == ['drf_parcel.E005']


@pytest.mark.parametrize('param', ['page', 'cursor'])
def test_a_query_parameter_a_paginator_already_reads(param: str) -> None:
    """?page=2 would ask for the second page and for a page of two rows at once."""
    with override_settings(DRF_PARCEL={'PAGE_SIZE_QUERY_PARAM': param}):
        assert ids(check_settings()) == ['drf_parcel.E011']


def test_the_check_runs_with_the_projects_checks() -> None:
    from django.core.checks import run_checks

    with override_settings(DRF_PARCEL={'PAGE_SIZE': 50, 'MAX_PAGE_SIZE': 10}):
        assert 'drf_parcel.E003' in ids(run_checks())  # type: ignore[arg-type]


@override_settings(REST_FRAMEWORK={'PAGE_SIZE': 500})
def test_drfs_own_page_size_above_the_ceiling() -> None:
    problems = check_settings()

    assert ids(problems) == ['drf_parcel.E003']
    assert '(500)' in problems[0].msg


def a_reporter() -> None:
    """A reporter that is a function - the kind accepted."""


NOT_CALLABLE = 'a string'


@pytest.mark.parametrize('value', ['short', None])
def test_field_errors_that_is_neither_shape(value: object) -> None:
    with override_settings(DRF_PARCEL={'FIELD_ERRORS': value}):
        assert ids(check_settings()) == ['drf_parcel.E006']


@pytest.mark.parametrize('value', ['', 0])
def test_a_path_separator_that_is_not_a_character(value: object) -> None:
    with override_settings(DRF_PARCEL={'FIELD_PATH_SEPARATOR': value}):
        assert ids(check_settings()) == ['drf_parcel.E007']


@override_settings(DRF_PARCEL={'ERROR_CODES': ['not_found']})
def test_error_codes_that_are_not_a_dictionary() -> None:
    assert ids(check_settings()) == ['drf_parcel.E008']


@override_settings(DRF_PARCEL={'ERROR_CODES': {'province_in_use': 'x'}})
def test_renaming_a_code_the_library_does_not_send() -> None:
    problems = check_settings()

    assert ids(problems) == ['drf_parcel.E008']
    assert 'province_in_use' in problems[0].msg


@pytest.mark.parametrize('new', ['', 5])
def test_renaming_a_code_to_nothing(new: object) -> None:
    with override_settings(DRF_PARCEL={'ERROR_CODES': {'not_found': new}}):
        assert ids(check_settings()) == ['drf_parcel.E008']


@pytest.mark.parametrize('name', ['HANDLE_INTEGRITY_ERRORS', 'RAISE_UNHANDLED_IN_DEBUG'])
def test_a_switch_that_is_not_true_or_false(name: str) -> None:
    with override_settings(DRF_PARCEL={name: 'yes'}):
        assert ids(check_settings()) == ['drf_parcel.E009']


@pytest.mark.parametrize(
    'path',
    [
        'tests.nowhere.reporter',
        'tests.test_a_misconfigured_setting_is_caught_at_start.NOT_CALLABLE',
        42,
    ],
)
def test_a_reporter_that_is_not_a_function(path: object) -> None:
    with override_settings(DRF_PARCEL={'REPORTER': path}):
        assert ids(check_settings()) == ['drf_parcel.E010']


@override_settings(
    DRF_PARCEL={'REPORTER': 'tests.test_a_misconfigured_setting_is_caught_at_start.a_reporter'}
)
def test_a_reporter_that_imports() -> None:
    assert check_settings() == []
