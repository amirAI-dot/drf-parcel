# Settings

## `DRF_PARCEL`

One dictionary, every key optional. A key the library does not know stops the
project - `manage.py check` reports it (E001) - rather than being ignored: a
misspelt `PAGE_SZIE` that is silently ignored is a page size that never
changes.

```python
DRF_PARCEL = {
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'CLIENT_PAGE_SIZE': False,
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
    'FIELD_ERRORS': 'detailed',
    'FIELD_PATH_SEPARATOR': '.',
    'ERROR_CODES': {},
    'HANDLE_INTEGRITY_ERRORS': False,
    'RAISE_UNHANDLED_IN_DEBUG': True,
    'REPORTER': None,
    'MESSAGES': {},
}
```

The setting is read on every use, so `override_settings` in a test takes
effect at once.

### Pages

| key | default | |
|---|---|---|
| `PAGE_SIZE` | `20` | the page size when a view names none. Left out, DRF's own `REST_FRAMEWORK['PAGE_SIZE']` is read when it is set, and only then 20 |
| `MAX_PAGE_SIZE` | `100` | the ceiling on a size the client chooses |
| `CLIENT_PAGE_SIZE` | `False` | whether the client may choose the size |
| `PAGE_SIZE_QUERY_PARAM` | `'page_size'` | the query parameter it chooses with |

### Failures { #failures }

| key | default | |
|---|---|---|
| `FIELD_ERRORS` | `'detailed'` | `'detailed'`: `{code, message}` for each problem; `'messages'`: the text alone, DRF's shape |
| `FIELD_PATH_SEPARATOR` | `'.'` | how a nested field's path is joined: `items.0.quantity` |
| `ERROR_CODES` | `{}` | a [standard code](error-codes.md) renamed: `{'validation_error': 'validation_failed'}` |
| `HANDLE_INTEGRITY_ERRORS` | `False` | answer a unique or foreign-key constraint with a 409 - [how-to](../how-to/database-constraints.md) |
| `RAISE_UNHANDLED_IN_DEBUG` | `True` | under `DEBUG`, raise a bug for Django's error page instead of answering the 500 |
| `REPORTER` | `None` | the dotted path to a function called as `report(exc, context)` with each 5xx |

### Messages

| key | default | |
|---|---|---|
| `MESSAGES` | `{}` | a default success message replaced, by its key: `created`, `saved`, `deleted`, `done` |

## On a view

| attribute | default | |
|---|---|---|
| `page_size` | the project's | this view's page size |
| `max_page_size` | the project's | this view's ceiling |
| `client_page_size` | the project's | whether this view's client may choose the size |
| `ordering` | the paginator's | a cursor's order |
| `envelope_messages` | `{}` | this view's own message, by action - `{'create': ...}` - or, on a plain `APIView`, by method - `{'post': ...}` |
| `parcel_wrap` | `True` | `False` leaves every answer of the view as DRF gives it |

## In `REST_FRAMEWORK`

| key | value |
|---|---|
| `EXCEPTION_HANDLER` | `'drf_parcel.handlers.exception_handler'` |
| `DEFAULT_PAGINATION_CLASS` | `'drf_parcel.pagination.PageNumberPagination'` or `'...CursorPagination'` |
| `DEFAULT_SCHEMA_CLASS` | `'drf_parcel.schema.ParcelAutoSchema'` |
| `NON_FIELD_ERRORS_KEY` | DRF's own; the key a problem of no field is under in `data.fields` |
