"""A project's own exception handler, built on the library's - as projects write them."""

import functools
from collections.abc import Mapping
from typing import Any

from rest_framework.response import Response

from drf_parcel.handlers import exception_handler


@functools.wraps(exception_handler)
def project_exception_handler(exc: Exception, context: Mapping[str, Any]) -> Response | None:
    """Adds nothing here; a real one might tag the response, or count failures."""
    return exception_handler(exc, context)
