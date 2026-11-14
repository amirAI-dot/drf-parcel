# Write your own errors

## A DomainError

```python
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from drf_parcel.exceptions import DomainError


class ProvinceInUseError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'province_in_use'
    default_detail = _('This province has branches and cannot be deleted.')
```

DRF's own names: `default_code` is sent as `error_code`, `default_detail` as
`message`. Mark the sentence with `gettext_lazy`, so it is said in the
request's language.

## Raise it with what a client can act on

```python
raise ProvinceInUseError(data={'branches': 3})
raise ProvinceInUseError(_('Move its 3 branches first.'), data={'branches': 3})
raise ProvinceInUseError(code='province_locked')
```

`data` is what a client acts on - which record is in the way, how long to
wait. Never what a person must not read elsewhere: it leaves the server as it
is.

## From a service, a task, a command

A `DomainError` is an ordinary exception too. A service raises it, and the
rule holds wherever it is reached from:

```python
def delete_province(province):
    branches = province.branches.count()
    if branches:
        raise ProvinceInUseError(data={'branches': branches})
    province.delete()
```

A Celery task or a management command catches it like any other exception.

## The ones the library ships

| class | status | `error_code` |
|---|---|---|
| `InvalidInputError` | 400 | `validation_error` |
| `InvalidCursorError` | 400 | `invalid_cursor` |
| `AuthenticationFailedError` | 401 | `authentication_failed` |
| `PermissionDeniedError` | 403 | `permission_denied` |
| `NotFoundError` | 404 | `not_found` |
| `ConflictError` | 409 | `conflict` |
| `RateLimitedError` | 429 | `rate_limited` |
| `ServiceUnavailableError` | 503 | `service_unavailable` |

Where DRF has an exception of the same meaning, the library's is also DRF's -
`NotFoundError` is a `NotFound` - so code that catches DRF's keeps working.

## Errors from before the library

Any subclass of DRF's `APIException` answers in the envelope unchanged. Give
it a `data` attribute and that is sent too. Django's own `ValidationError` - a
model's `clean()` - reads back as a validation error, field by field.
