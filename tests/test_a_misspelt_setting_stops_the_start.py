"""
A setting the library does not know is refused, never ignored.

If these fail, ``PAGE_SZIE`` is silently ignored and a page size never
changes - and nobody can tell why.
"""

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from rest_framework.test import APIClient

from drf_parcel import conf


@override_settings(DRF_PARCEL={'PAGE_SZIE': 50})
def test_an_unknown_key_is_refused() -> None:
    with pytest.raises(ImproperlyConfigured, match='PAGE_SZIE'):
        conf.get('PAGE_SIZE')


@override_settings(DRF_PARCEL=['PAGE_SIZE'])
def test_a_setting_that_is_not_a_dictionary_is_refused() -> None:
    with pytest.raises(ImproperlyConfigured, match='must be a dictionary'):
        conf.get('PAGE_SIZE')


@override_settings(DRF_PARCEL={'MESSAGES': {'creatd': 'Saved.'}})
def test_an_unknown_message_key_is_refused(client: APIClient) -> None:
    with pytest.raises(ImproperlyConfigured, match='creatd'):
        client.get('/rings/')


@override_settings(DRF_PARCEL={'MESSAGES': 'Saved.'})
def test_messages_that_are_not_a_dictionary_are_refused() -> None:
    with pytest.raises(ImproperlyConfigured, match='must be a dictionary'):
        conf.messages()


def test_a_key_left_out_is_its_default() -> None:
    assert conf.get('PAGE_SIZE') == 20


@override_settings(DRF_PARCEL={'PAGE_SIZE': 50})
def test_a_key_written_is_what_it_says() -> None:
    assert conf.get('PAGE_SIZE') == 50
