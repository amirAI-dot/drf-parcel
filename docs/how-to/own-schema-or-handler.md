# Use your own schema class or handler

## An AutoSchema of the project's

```python
from drf_spectacular.openapi import AutoSchema
from drf_parcel.schema import ParcelSchemaMixin


class ProjectSchema(ParcelSchemaMixin, AutoSchema):
    ...                                    # the project's own customisation
```

```python
REST_FRAMEWORK = {'DEFAULT_SCHEMA_CLASS': 'config.schema.ProjectSchema'}
```

## An exception handler of the project's

A handler that does something before or after the library's calls it - and
says so with `functools.wraps`, so the schema still knows failures are in the
envelope:

```python
import functools

from drf_parcel.handlers import exception_handler


@functools.wraps(exception_handler)
def project_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response['X-Request-Id'] = context['request'].META.get('HTTP_X_REQUEST_ID', '')
    return response
```

Without `functools.wraps` the answers are the same, but the schema documents
no error envelope: it promises only what it can tell.

## Outside DRF

The handler shapes what reaches a DRF view. An address matching no URL, or a
failure in a middleware, is Django's to answer, with the project's
`handler404` and `handler500` - those are the whole project's, its admin site
and web pages too, and the library does not reach into them.
