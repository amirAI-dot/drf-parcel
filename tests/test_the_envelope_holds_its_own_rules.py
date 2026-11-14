"""
The envelope refuses to be built wrong.

If these fail, a success could carry an ``error_code`` or a failure leave
one out - and a client branching on ``error_code`` would branch on nothing.
"""

import pytest
from django.utils.translation import gettext_lazy as _

from drf_parcel.envelope import build_envelope


def test_a_success_carries_no_error_code() -> None:
    with pytest.raises(ValueError, match='no error_code'):
        build_envelope(success=True, status_code=200, message='', error_code='x')


def test_a_failure_names_its_error_code() -> None:
    with pytest.raises(ValueError, match='must name its error_code'):
        build_envelope(success=False, status_code=400, message='')


def test_a_failure_is_not_a_page() -> None:
    with pytest.raises(ValueError, match='not a page'):
        build_envelope(
            success=False, status_code=400, message='', error_code='x', pagination={'page': 1}
        )


def test_a_page_keeps_its_pagination() -> None:
    envelope = build_envelope(success=True, status_code=200, message='', pagination={'page': 2})

    assert envelope['pagination'] == {'page': 2}


def test_a_lazy_message_becomes_text() -> None:
    envelope = build_envelope(success=True, status_code=200, message=_('Done.'))

    assert type(envelope['message']) is str
