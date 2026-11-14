"""
A page setting that cannot work is reported by ``manage.py check``.

If these fail, a ceiling below the page size - or a page size of "20" - is
found by the first client that asks for a list, not by whoever deployed it.
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


def test_the_check_runs_with_the_projects_checks() -> None:
    from django.core.checks import run_checks

    with override_settings(DRF_PARCEL={'PAGE_SIZE': 50, 'MAX_PAGE_SIZE': 10}):
        assert 'drf_parcel.E003' in ids(run_checks())  # type: ignore[arg-type]


@override_settings(REST_FRAMEWORK={'PAGE_SIZE': 500})
def test_drfs_own_page_size_above_the_ceiling() -> None:
    problems = check_settings()

    assert ids(problems) == ['drf_parcel.E003']
    assert '(500)' in problems[0].msg
