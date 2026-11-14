"""
What is wrong with the ``DRF_PARCEL`` setting, said when the project starts.

A setting that would only fail on the first request that reads it fails
instead on ``manage.py check`` and ``runserver`` - before a client finds it.
"""

from collections.abc import Sequence
from typing import Any

from django.apps import AppConfig
from django.core.checks import CheckMessage, Error
from django.core.exceptions import ImproperlyConfigured

from drf_parcel import conf


def check_settings(
    app_configs: Sequence[AppConfig] | None = None, **kwargs: Any
) -> list[CheckMessage]:
    """Every problem with the setting, each with what to do about it."""
    try:
        conf.raw()
        conf.messages()
    except ImproperlyConfigured as refused:
        return [Error(str(refused), id='drf_parcel.E001')]

    return _page_size_problems()


def _page_size_problems() -> list[CheckMessage]:
    problems: list[CheckMessage] = []
    page_size = conf.page_size()
    ceiling = conf.get('MAX_PAGE_SIZE')

    # The page size may be DRF's own PAGE_SIZE, so it is named by what it is.
    for name, value in (
        ('The page size', page_size),
        ("DRF_PARCEL['MAX_PAGE_SIZE']", ceiling),
    ):
        if not _is_positive_whole_number(value):
            problems.append(
                Error(
                    f'{name} must be a whole number above zero, not {value!r}.',
                    hint="It is DRF_PARCEL['PAGE_SIZE'], else REST_FRAMEWORK['PAGE_SIZE'].",
                    id='drf_parcel.E002',
                )
            )

    if not problems and ceiling < page_size:  # type: ignore[operator]
        problems.append(
            Error(
                f"DRF_PARCEL['MAX_PAGE_SIZE'] ({ceiling}) is below the page size ({page_size}).",
                hint='The ceiling on a size the client chooses cannot be below the default size.',
                id='drf_parcel.E003',
            )
        )

    if not isinstance(conf.get('CLIENT_PAGE_SIZE'), bool):
        problems.append(
            Error("DRF_PARCEL['CLIENT_PAGE_SIZE'] must be True or False.", id='drf_parcel.E004')
        )

    param = conf.get('PAGE_SIZE_QUERY_PARAM')

    if not isinstance(param, str) or not param:
        problems.append(
            Error(
                "DRF_PARCEL['PAGE_SIZE_QUERY_PARAM'] must be the name of a query parameter.",
                id='drf_parcel.E005',
            )
        )

    return problems


def _is_positive_whole_number(value: object) -> bool:
    # True is an int to Python, and is no page size.
    return isinstance(value, int) and not isinstance(value, bool) and value > 0
