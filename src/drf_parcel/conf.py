"""
The ``DRF_PARCEL`` setting, read and checked.

Every key lives in one dictionary in the project's settings, and the default
needs none of them::

    DRF_PARCEL = {
        'PAGE_SIZE': 20,
        'MESSAGES': {'created': _('Saved successfully.')},
    }

A key the library does not know is refused rather than ignored: a misspelt
``PAGE_SZIE`` that is silently ignored is a page size that never changes, and
nobody can tell why.

The setting is read on every use rather than once, so a test that overrides
it - and a project that changes it - is answered by what it says now.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

#: Every key the setting may hold, and what it is when left out.
DEFAULTS: Final[Mapping[str, object]] = MappingProxyType(
    {
        'PAGE_SIZE': 20,
        'MAX_PAGE_SIZE': 100,
        'CLIENT_PAGE_SIZE': False,
        'PAGE_SIZE_QUERY_PARAM': 'page_size',
        'FIELD_ERRORS': 'detailed',
        'FIELD_PATH_SEPARATOR': '.',
        'ERROR_CODES': MappingProxyType({}),
        'HANDLE_INTEGRITY_ERRORS': False,
        'RAISE_UNHANDLED_IN_DEBUG': True,
        'REPORTER': None,
        'MESSAGES': MappingProxyType({}),
    }
)

#: The default success messages a project may replace, by key.
MESSAGE_KEYS: Final = ('created', 'saved', 'deleted', 'done')


def raw() -> Mapping[str, object]:
    """The setting as written, refused when it is not a dictionary of known keys."""
    written = getattr(settings, 'DRF_PARCEL', {})

    if not isinstance(written, Mapping):
        raise ImproperlyConfigured('DRF_PARCEL must be a dictionary.')

    unknown = sorted(set(written) - set(DEFAULTS))

    if unknown:
        raise ImproperlyConfigured(
            f'DRF_PARCEL has keys the library does not know: {", ".join(unknown)}. '
            f'It knows {", ".join(DEFAULTS)}.'
        )

    return written


def get(key: str) -> object:
    """One key of the setting, or its default when the project left it out."""
    return raw().get(key, DEFAULTS[key])


def messages() -> Mapping[str, object]:
    """The project's replacements for the default success messages, by key."""
    replaced = get('MESSAGES')

    if not isinstance(replaced, Mapping):
        raise ImproperlyConfigured("DRF_PARCEL['MESSAGES'] must be a dictionary.")

    unknown = sorted(set(replaced) - set(MESSAGE_KEYS))

    if unknown:
        raise ImproperlyConfigured(
            f"DRF_PARCEL['MESSAGES'] has keys the library does not know: {', '.join(unknown)}. "
            f'It knows {", ".join(MESSAGE_KEYS)}.'
        )

    return replaced
