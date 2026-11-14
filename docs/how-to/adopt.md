# Adopt it in an existing project

A project that already answers in an envelope of its own - a
`success_response` helper, a mixin that overrides `list` and `create`, an
exception handler - moves to the library one part at a time, and its errors
keep working unchanged.

## 1. Compare the shapes

What a client of a typical hand-made envelope reads, and what it reads after:

| | before - a common hand-made envelope | after |
|---|---|---|
| success | `success`, `status_code`, `message`, `data` | the same |
| a page | `next`, `previous`, `total_pages`, `current_page`, `page_size` | `type`, `count`, `page`, `pages`, `page_size`, `has_next`, `has_previous` |
| validation | the first problem in `message` | the first problem in `message` **and** every problem in `data.fields` |
| a code | `validation_error`, `authentication_error`, ... | [the standard codes](../reference/error-codes.md), renamed to yours if you like |
| a delete | often a 204 with a body nobody receives | a 200 with the envelope |

The success shape and `message` stay as they were. What a frontend has to
change is the pager, and only if it read `next` and `current_page`.

## 2. Install the handler first

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
}
```

Remove the project's own handler. Its `APIException` subclasses need no
change: each answers with its `status_code`, its `default_code` as
`error_code` and its `detail` as `message` - and `data`, if it has one.

If the clients branch on the old codes, keep them:

```python
DRF_PARCEL = {
    'ERROR_CODES': {
        'not_authenticated': 'authentication_error',
        'authentication_failed': 'authentication_error',
    },
}
```

The project's own codes are never renamed - only the library's.

## 3. Replace the mixin

Where a view had the project's mixin, give it `EnvelopeMixin` instead, and
delete the overridden `list`, `create`, `retrieve`, `update` and `destroy`:
the mixin wraps whatever the view answers, in one place.

```python
from drf_parcel.responses import EnvelopeMixin, success_response
```

A view that called the project's `success_response(request, data=...)` calls
the library's `success_response(data)` - no `request`, and a `message` only
when it has something to say.

## 4. Replace the paginator

```python
REST_FRAMEWORK = {
    ...,
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
}
```

A project that set `REST_FRAMEWORK['PAGE_SIZE']` keeps its size: the library
reads it when `DRF_PARCEL['PAGE_SIZE']` is not set. If that size is above
100, raise `DRF_PARCEL['MAX_PAGE_SIZE']` too - `manage.py check` says so
(E003).

## 5. Check, then test

```bash
python manage.py check
python manage.py test
```

Tests that read `response.data['next']` or a 204 change with the shapes in
step 1; the others pass as they did. Adopt it one app at a time if the
project is large: each view without the mixin answers as before.
