"""
What is wrong with the ``DRF_PARCEL`` setting, said when the project starts.

A setting that would only fail on the first request that reads it fails
instead on ``manage.py check`` and ``runserver`` - before a client finds it.
"""

from collections.abc import Mapping, Sequence
from typing import Any

from django.apps import AppConfig
from django.core.checks import CheckMessage, Error
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from rest_framework import pagination

from drf_parcel import conf
from drf_parcel.handlers import STANDARD_CODES

#: The parameters the paginators read themselves: which page, and from where.
_PAGINATORS_OWN_PARAMS = (
    pagination.PageNumberPagination.page_query_param,
    pagination.CursorPagination.cursor_query_param,
)


def check_settings(
    app_configs: Sequence[AppConfig] | None = None, **kwargs: Any
) -> list[CheckMessage]:
    """Every problem with the setting, each with what to do about it."""
    try:
        conf.raw()
        conf.messages()
    except ImproperlyConfigured as refused:
        return [Error(str(refused), id='drf_parcel.E001')]

    return _page_size_problems() + _error_problems()


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
    elif param in _PAGINATORS_OWN_PARAMS:
        problems.append(
            Error(
                f"DRF_PARCEL['PAGE_SIZE_QUERY_PARAM'] is {param!r}, which a paginator "
                f'already reads for something else.',
                hint='A request for page 2 would also be a request for a page of two rows.',
                id='drf_parcel.E011',
            )
        )

    return problems


def _error_problems() -> list[CheckMessage]:
    problems: list[CheckMessage] = []

    if conf.get('FIELD_ERRORS') not in ('detailed', 'messages'):
        problems.append(
            Error(
                "DRF_PARCEL['FIELD_ERRORS'] must be 'detailed' or 'messages'.",
                id='drf_parcel.E006',
            )
        )

    separator = conf.get('FIELD_PATH_SEPARATOR')

    if not isinstance(separator, str) or not separator:
        problems.append(
            Error(
                "DRF_PARCEL['FIELD_PATH_SEPARATOR'] must be a character or more.",
                id='drf_parcel.E007',
            )
        )

    problems.extend(_error_code_problems())

    for name in ('HANDLE_INTEGRITY_ERRORS', 'RAISE_UNHANDLED_IN_DEBUG'):
        if not isinstance(conf.get(name), bool):
            problems.append(
                Error(f"DRF_PARCEL['{name}'] must be True or False.", id='drf_parcel.E009')
            )

    problems.extend(_reporter_problems())
    return problems


def _error_code_problems() -> list[CheckMessage]:
    renamed = conf.get('ERROR_CODES')

    if not isinstance(renamed, Mapping):
        return [Error("DRF_PARCEL['ERROR_CODES'] must be a dictionary.", id='drf_parcel.E008')]

    problems: list[CheckMessage] = []
    unknown = sorted(set(renamed) - set(STANDARD_CODES))

    if unknown:
        problems.append(
            Error(
                f"DRF_PARCEL['ERROR_CODES'] renames codes the library does not send: "
                f'{", ".join(unknown)}.',
                hint=f'It sends {", ".join(STANDARD_CODES)}.',
                id='drf_parcel.E008',
            )
        )

    if not all(isinstance(new, str) and new for new in renamed.values()):
        problems.append(
            Error(
                "Every new name in DRF_PARCEL['ERROR_CODES'] must be a word.",
                id='drf_parcel.E008',
            )
        )

    return problems


def _reporter_problems() -> list[CheckMessage]:
    path = conf.get('REPORTER')

    if path is None:
        return []

    try:
        reporter = import_string(path) if isinstance(path, str) else None
    except ImportError:
        reporter = None

    if not callable(reporter):
        return [
            Error(
                f"DRF_PARCEL['REPORTER'] must be the dotted path to a function, not {path!r}.",
                hint='It is called with each unexpected exception and its context.',
                id='drf_parcel.E010',
            )
        ]

    return []


def _is_positive_whole_number(value: object) -> bool:
    # True is an int to Python, and is no page size.
    return isinstance(value, int) and not isinstance(value, bool) and value > 0
