# drf-parcel

One response shape for a Django REST framework API - success, page and error
alike - and the generated schema saying exactly that shape.

[فارسی](https://github.com/amirAI-dot/drf-parcel/blob/main/README.fa.md)

```json
{"success": true,  "status_code": 200, "message": "Done.",    "data": {"id": 7}}
{"success": true,  "status_code": 200, "message": "Done.",    "data": [], "pagination": {"type": "page", "count": 45, "page": 2, "pages": 3, "page_size": 20, "has_next": true, "has_previous": true}}
{"success": false, "status_code": 409, "message": "...",      "data": {"branches": 3}, "error_code": "province_in_use"}
```

A client reads one shape and never special-cases a payload: the answer is
under `data`, a person reads `message`, and code branches on `error_code` -
never on the message, which is translated.

**[The documentation](https://amirai-dot.github.io/drf-parcel/)** - a
quickstart, a tutorial, how-to guides, the reference - in English and
Persian.

## In a project

```bash
pip install 'drf-parcel[schema]'      # the schema extra brings drf-spectacular
```

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'drf_parcel',
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
}
```

Each line is independent: the handler alone gives the error envelope and
nothing else, and a project adopts the rest one view at a time.

```python
from drf_parcel.pagination import CursorPagination
from drf_parcel.responses import EnvelopeMixin, success_response


class ProductViewSet(EnvelopeMixin, ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    page_size = 12
    client_page_size = True          # the client may send ?page_size=
    max_page_size = 48               # and never gets more
    envelope_messages = {'create': _('The product was added.')}


class NotificationViewSet(EnvelopeMixin, ModelViewSet):
    pagination_class = CursorPagination
    ordering = '-created_at'


class TotalsView(EnvelopeMixin, APIView):
    def get(self, request):
        return success_response({'total': 12}, message=_('Totals.'))
```

`EnvelopeMixin` wraps what a view answers once, in `finalize_response`, so
no action - `list`, `create`, a custom `@action` - has to remember. A delete
answers 200 with the envelope rather than a 204 with nothing. A file, a
stream, a redirect or a CSV is left alone, and so is a view with
`parcel_wrap = False`.

A shop that uses every part of it, to run and read, is in
[`example/`](example/README.md).

## Errors

```python
from drf_parcel.exceptions import DomainError


class ProvinceInUse(DomainError):
    status_code = 409
    default_code = 'province_in_use'
    default_detail = _('This province has branches and cannot be deleted.')


raise ProvinceInUse(data={'branches': 3})
```

A `DomainError` is DRF's `APIException` with `data` added, so a project's
existing errors answer in the envelope unchanged. The handler also:

* says a validation error's first problem in `message` and every problem in
  `data.fields`, each with its code at a flat path - `items.0.quantity`;
* answers DRF's and Django's own failures with a standard code -
  `not_authenticated`, `permission_denied`, `not_found`, `rate_limited` with
  `retry_after` ... - and keeps the headers DRF puts on them;
* answers anything unexpected with a generic 500 whose text never leaves the
  server: it is logged with its traceback and handed to your `REPORTER`.
  Under `DEBUG` it is raised, so Django's page shows it;
* undoes the request's write behind every failure it answers.

## Pagination

Numbered pages or a cursor, chosen per view. `pagination.type` says which, so
one component on a client reads either. A client chooses the page size only
where a view allows it, and always under a ceiling.

## The schema

With `ParcelAutoSchema` - or `ParcelSchemaMixin` in your own `AutoSchema` -
the OpenAPI document says what the wire carries: every success inside the
envelope, each page as its own envelope, `page_size` only where it is
accepted, and the error envelope as every operation's `default` answer.

## Settings

One dictionary, `DRF_PARCEL`. A key the library does not know stops the
project at start-up rather than being ignored, and `manage.py check` reports
a value that cannot work. Every key, every shape and every error code is in
[the contract](docs/contract.md).

## Languages

Every sentence the library says is in the request's language. It ships
Persian; DRF's own messages come in DRF's languages.

## Supported

Python 3.11 to 3.14; Django 5.2, 6.0 and 6.1; Django REST framework 3.16 and
later; drf-spectacular 0.28 and later, for the schema.

## Working on it

Every check runs through [nox](https://nox.thea.codes), the same sessions
locally and in CI.

```bash
uv tool install nox
```

```bash
nox -s lint types tests
```

`tests` runs every supported Python and Django; `oldest` runs the oldest
release of everything supported; `package` builds the wheel and checks what
is in it. The suite runs on SQLite by default, and on PostgreSQL with
`DRF_PARCEL_TEST_DATABASE=postgres` and the standard `PG*` variables.

After changing a marked string, translate it in
`src/drf_parcel/locale/fa/LC_MESSAGES/django.po` and compile it:

```bash
nox -s messages
```

## Licence

BSD 3-Clause - see [`LICENSE`](LICENSE).
