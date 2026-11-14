"""
What a success says when nobody wrote it a message.

It is read off the request itself, so a viewset, a plain ``APIView`` and a
custom ``@action`` all say something sensible and none has to remember:

======================  ===========  ==================
the request             the message  its key in MESSAGES
======================  ===========  ==================
answered 201            Created.     ``created``
``PUT`` or ``PATCH``    Saved.       ``saved``
``DELETE``              Deleted.     ``deleted``
anything else           Done.        ``done``
======================  ===========  ==================

A project replaces any of them with ``DRF_PARCEL['MESSAGES']``; a view, with
``envelope_messages``; one answer, by passing its own.
"""

from collections.abc import Mapping
from typing import Final

from django.utils.translation import gettext_lazy as _
from rest_framework import status

from drf_parcel import conf

#: The library's own sentence for each key.
DEFAULTS: Final[Mapping[str, object]] = {
    'created': _('Created.'),
    'saved': _('Saved.'),
    'deleted': _('Deleted.'),
    'done': _('Done.'),
}


def key_for(method: str | None, status_code: int) -> str:
    """Which of the four a request is, by its answer's status and its method."""
    if status_code == status.HTTP_201_CREATED:
        return 'created'

    if method in ('PUT', 'PATCH'):
        return 'saved'

    if method == 'DELETE':
        return 'deleted'

    return 'done'


def default_message(method: str | None, status_code: int) -> object:
    """The message a success says unless a view or an answer names its own."""
    key = key_for(method, status_code)
    return conf.messages().get(key, DEFAULTS[key])
