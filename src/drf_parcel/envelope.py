"""
The envelope - the one place its shape is assembled.

Every answer has the same top level, success and failure alike::

    {"success": true,  "status_code": 200, "message": "...", "data": {}}
    {"success": true,  "status_code": 200, "message": "...", "data": [], "pagination": {}}
    {"success": false, "status_code": 409, "message": "...", "data": {}, "error_code": "..."}

Two places building the envelope become two shapes, so nothing else in the
library writes these keys.
"""

from collections.abc import Mapping
from typing import Any

#: The keys every envelope carries, whatever it answers.
KEYS = ('success', 'status_code', 'message', 'data')


def build_envelope(
    *,
    success: bool,
    status_code: int,
    message: object,
    data: Any = None,
    pagination: Mapping[str, Any] | None = None,
    error_code: str | None = None,
) -> dict[str, Any]:
    """
    The envelope, from its parts.

    ``message`` may be a lazy translation: it becomes text here, under the
    language active when the answer is built. ``data`` that says nothing is
    ``{}``, never ``null``.

    A key is either always there or there for a reason, so a failure must
    name its ``error_code`` and a success must not, and only a success is a
    page.
    """
    if success and error_code is not None:
        raise ValueError('A success carries no error_code.')

    if not success and not error_code:
        raise ValueError('A failure must name its error_code.')

    if not success and pagination is not None:
        raise ValueError('A failure is not a page.')

    envelope: dict[str, Any] = {
        'success': success,
        'status_code': status_code,
        'message': str(message),
        'data': {} if data is None else data,
    }

    if pagination is not None:
        envelope['pagination'] = dict(pagination)

    if error_code is not None:
        envelope['error_code'] = error_code

    return envelope


def envelope_schema(
    data: Mapping[str, Any],
    *,
    pagination: Mapping[str, Any] | None = None,
    error: bool = False,
) -> dict[str, Any]:
    """
    The OpenAPI schema of an envelope around ``data`` - the shape above, as a schema.

    Kept beside ``build_envelope`` so that the shape and its description
    change together.
    """
    properties: dict[str, Any] = {
        # Not an enum: drf-spectacular would lift each into a component of its own.
        'success': {
            'type': 'boolean',
            'example': not error,
            'description': 'Always false on a failure.' if error else 'Always true on a success.',
        },
        'status_code': {'type': 'integer'},
        'message': {'type': 'string'},
        'data': dict(data),
    }
    required = list(KEYS)

    if pagination is not None:
        properties['pagination'] = dict(pagination)
        required.append('pagination')

    if error:
        properties['error_code'] = {'type': 'string'}
        required.append('error_code')

    return {'type': 'object', 'properties': properties, 'required': required}
