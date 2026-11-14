# Installation

## The package

```bash
pip install 'drf-parcel[schema]'      # with drf-spectacular, for the schema
pip install drf-parcel                # without it
```

It needs Python 3.11 or later, Django 5.2 or later and Django REST framework
3.16 or later. The `schema` extra brings drf-spectacular 0.28 or later; leave
it out if the project generates no OpenAPI document, and nothing else in the
library needs it.

## The settings

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'drf_parcel',          # for its Persian catalogue and its start-up checks
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
}
```

**Each of the three lines is independent.** The handler alone gives the
error envelope and nothing else; the paginator alone gives paged lists in
the envelope; the schema class alone describes what the other two answer.
Take the one a project is ready for.

The successes of a view are wrapped by `EnvelopeMixin`, on the view - see the
[quickstart](quickstart.md).

## Languages

Messages are said in the request's language. With Django's
`LocaleMiddleware`, a request with `Accept-Language: fa` is answered in
Persian:

```python
MIDDLEWARE = [
    ...,
    'django.middleware.locale.LocaleMiddleware',
    ...,
]
```

## Check it

```bash
python manage.py check
```

A key in `DRF_PARCEL` the library does not know, or a value that cannot
work - a ceiling below the page size, a reporter that does not import - is
reported here, before a client finds it. Every check is listed in
[the reference](../reference/checks.md).
