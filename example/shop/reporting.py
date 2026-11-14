"""Where the example reports a bug - in a real project, Sentry or something like it."""

import logging
from collections.abc import Mapping
from typing import Any

logger = logging.getLogger('shop.bugs')


def report(exc: Exception, context: Mapping[str, Any]) -> None:
    """Called by drf-parcel with each unexpected exception, never with one somebody designed."""
    logger.warning('A bug was reported: %r', exc)
