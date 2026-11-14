# The contract

> **Status: draft, for the owner to decide.** Every shape that leaves the
> server, every error code, and every setting. The code follows this
> document; a change to what a client receives is a change here first.
> The questions still open are listed at the end.
>
> Persian: [`contract.fa.md`](contract.fa.md).

---

## 1. The envelope

Every answer has the same top level, success and failure alike, so a client
reads one shape and never special-cases a payload.

| key | type | present | meaning |
|---|---|---|---|
| `success` | boolean | always | whether the request did what it asked |
| `status_code` | integer | always | the HTTP status, repeated in the body |
| `message` | string | always | one sentence for a person, in the request's language |
| `data` | object or array | always | the answer: one object, a list, or `{}` |
| `pagination` | object | only on a paged list | how to ask for the next page |
| `error_code` | string | only on a failure | what a client branches on |

Rules:

* **A key is either always there or there for a reason.** `pagination` on a
  list that is not paged would be an empty promise; `error_code` on a
  success would be a code for nothing. Neither is ever sent empty.
* **`data` is never `null`.** Nothing to say is `{}`.
* **`message` is for people, `error_code` is for code.** The message is
  translated and will change; a client that compares it breaks the day a
  sentence is reworded.
* **`status_code` equals the HTTP status** of the response it is in, always.

### A single object

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": {"id": 7, "name": "Ring"}
}
```

### Created

```json
{
  "success": true,
  "status_code": 201,
  "message": "Created.",
  "data": {"id": 8, "name": "Necklace"}
}
```

### Deleted

A `204 No Content` carries no body by definition, so the envelope would be
thrown away. A delete answers **200** with the envelope instead:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Deleted.",
  "data": {}
}
```

### A list that is not paged

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": [{"id": 1}, {"id": 2}]
}
```

### What is never wrapped

* a response that is not JSON - a file, a PDF, a stream, a redirect;
* a view that opts out (`parcel_wrap = False`), for a webhook or a health
  check whose caller expects a shape of its own;
* a response already in the envelope - `success_response` returns one, and
  it is not wrapped twice.

---

## 2. Pagination

Two kinds, and **each view chooses** - a numbered list in one, an endless
feed in the next. `pagination.type` says which, so one component on the
client can read either without guessing.

### By page number

`GET /products/?page=2&page_size=20`

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": [{"id": 21}, {"id": 22}],
  "pagination": {
    "type": "page",
    "count": 45,
    "page": 2,
    "pages": 3,
    "page_size": 20,
    "has_next": true,
    "has_previous": true
  }
}
```

| key | meaning |
|---|---|
| `count` | rows in the whole list |
| `page` | this page, from 1 |
| `pages` | how many pages there are |
| `page_size` | the size actually used - after the ceiling, see 2.3 |
| `has_next`, `has_previous` | whether the neighbours exist |

No `next` / `previous` links: the client is on another domain and builds
`?page=3` itself, and a server behind a proxy builds its own links with the
wrong scheme or host.

A page past the end is **404** (`not_found`), as DRF does.

### By cursor

`GET /notifications/?cursor=cD0yMDI2LTExLTE0&page_size=20`

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": [{"id": 90}, {"id": 89}],
  "pagination": {
    "type": "cursor",
    "next_cursor": "cD0yMDI2LTExLTEz",
    "previous_cursor": "cj0xJnA9MjAyNi0xMS0xNA",
    "page_size": 20,
    "has_next": true,
    "has_previous": true
  }
}
```

A cursor is opaque: the client sends back what it was given and never
builds one. There is no `count` and no `page` - not counting is the point of
a cursor, on a table too large to count on every request. `has_next` is in
both kinds, so a "load more" button works with either.

A cursor the server cannot read is **400** (`invalid_cursor`).

### 2.3 The client choosing the page size

Off by default. When a view allows it, the client sends `?page_size=`, and
the server **always** applies a ceiling - without one, `?page_size=1000000`
is a request to read a whole table, open to anybody.

| the client sends | the server uses |
|---|---|
| nothing | the view's `page_size` |
| `24`, within the ceiling | 24 |
| `500`, above the ceiling | the ceiling - no error: paging is not where to be strict |
| `0`, `-3`, `abc` | the view's `page_size` |
| anything, while the view does not allow it | the view's `page_size`; the parameter is ignored and **not in the schema** |

`pagination.page_size` always says the size used, so a client asking for
500 sees that it got 100.

---

## 3. Errors

The same envelope, with `success: false` and an `error_code`.

```json
{
  "success": false,
  "status_code": 409,
  "error_code": "province_in_use",
  "message": "This province has branches and cannot be deleted.",
  "data": {"branches": 3}
}
```

`data` holds what a client can act on - which record is in the way, how
long to wait. It is `{}` when there is nothing.

### 3.1 Validation

The first problem in `message`, every problem in `data.fields`:

```json
{
  "success": false,
  "status_code": 400,
  "error_code": "validation_error",
  "message": "Enter a valid phone number.",
  "data": {
    "fields": {
      "phone": [{"code": "invalid", "message": "Enter a valid phone number."}],
      "items.0.quantity": [{"code": "min_value", "message": "Ensure this value is greater than or equal to 1."}],
      "non_field_errors": [{"code": "invalid", "message": "The dates are the wrong way round."}]
    }
  }
}
```

* A screen that shows one sentence reads `message`; a form that marks each
  field reads `fields` - and a client written for the old one-message shape
  keeps working.
* Each problem carries its **`code`** (`required`, `max_length`, `unique`,
  `invalid` ...) so a client can tell "empty" from "taken" without reading
  translated text.
* A nested field is one **flat path**, joined with `.`: `items.0.quantity`
  is the quantity of the first item.
* Errors that belong to no field are under DRF's own key,
  `non_field_errors` (its `NON_FIELD_ERRORS_KEY` setting).
* Django's own `ValidationError` - a model's `clean()`, a service - reads
  back exactly the same way.

### 3.2 The standard error codes

| status | `error_code` | raised by | `data` |
|---|---|---|---|
| 400 | `validation_error` | a serializer, a Django `ValidationError` | `fields` |
| 400 | `parse_error` | a body that is not valid JSON | `{}` |
| 400 | `invalid_cursor` | a cursor the server cannot read | `{}` |
| 401 | `not_authenticated` | no credentials | `{}` |
| 401 | `authentication_failed` | wrong or expired credentials | `{}` |
| 403 | `permission_denied` | DRF's or Django's `PermissionDenied` | `{}` |
| 404 | `not_found` | `NotFound`, Django's `Http404` | `{}` |
| 405 | `method_not_allowed` | a method the view has not got | `{}` |
| 406 | `not_acceptable` | an `Accept` nobody can answer | `{}` |
| 409 | `already_exists` | a unique `IntegrityError`, when turned on (3.5) | `{}` |
| 409 | `conflict` | a foreign-key `IntegrityError`, when turned on (3.5) | `{}` |
| 415 | `unsupported_media_type` | a body type the view does not read | `{}` |
| 429 | `rate_limited` | throttling | `retry_after`, in seconds |
| 500 | `internal_error` | anything nobody designed | `{}` |
| 503 | `service_unavailable` | `ServiceUnavailableError` | `{}` |

Every name can be changed in the settings (`ERROR_CODES`), for a project
whose clients already branch on other words.

**Headers are kept.** DRF puts `Retry-After` on a 429, `Allow` on a 405 and
`WWW-Authenticate` on a 401; each stays on the response.

### 3.3 A project's own errors

```python
from drf_parcel.exceptions import DomainError

class ProvinceInUse(DomainError):
    status_code = 409
    default_code = 'province_in_use'
    default_detail = _('This province has branches and cannot be deleted.')

raise ProvinceInUse(data={'branches': 3})
raise ProvinceInUse(_('Move its 3 branches first.'), data={'branches': 3})
```

**`DomainError` is DRF's `APIException`**, with one thing added: `data`.
Its names are DRF's own - `status_code`, `default_code` (sent as
`error_code`), `default_detail` (sent as `message`) - so there is nothing
new to learn, and there is one kind of error, not two.

```python
class DomainError(APIException):
    status_code = 400
    default_code = 'error'
    default_detail = _('The request could not be completed.')

    def __init__(self, detail=None, code=None, *, data=None):
        super().__init__(detail, code)
        self.data = data or {}
```

* **It works without this library's handler.** A project that installs the
  mixin and keeps DRF's own handler still gets the right status, its
  `set_rollback`, and a sensible answer - not a 500.
* **It is an ordinary exception too.** A service raises it, and a Celery
  task or a management command catches it like any other.
* **The rollback is the handler's, not the class's.** DRF's own handler
  calls `set_rollback`; this library replaces that handler, so its handler
  calls it itself, on every path (3.6).
* **The message is made text when it is raised**, as DRF does - in the
  request's language inside a request. One raised outside a request is in
  the default language.

The library ships the common ones - `InvalidInputError`,
`AuthenticationFailedError`, `PermissionDeniedError`, `NotFoundError`,
`ConflictError`, `RateLimitedError`, `ServiceUnavailableError`.

**A project's existing errors keep working.** Any subclass of DRF's
`APIException`, `DomainError` or not, answers in the envelope with no
change: its `status_code`, its `default_code` as `error_code`, its
`detail` as `message`, and `data` when it has one.

### 3.4 What is never said

An unexpected exception answers **500** with a generic sentence. Its text
never leaves the server - it can hold a query, a file path, a person's
name - and it is the only failure logged as an error, with its traceback.
A 404 or a wrong phone number is not logged as an error at all.

* With `DEBUG = True` it is raised instead, so Django's error page shows
  the traceback (`RAISE_UNHANDLED_IN_DEBUG`).
* `REPORTER` names a function called with each 500 - for Sentry or
  anything like it.

### 3.5 Database integrity

Off by default. A constraint the database refuses was normally caught
earlier, by the serializer or the service; this is a safety net, turned on
with `HANDLE_INTEGRITY_ERRORS`.

The kind of constraint is read from the code the database driver reports -
never from its text, which changes with the database, its version and its
language:

| constraint | PostgreSQL `sqlstate` | SQLite `sqlite_errorcode` | MySQL `errno` |
|---|---|---|---|
| unique | `23505` | `2067`, `1555` | `1062` |
| foreign key | `23503` | `787` | `1451`, `1452` |
| not null | `23502` | `1299` | `1048` |
| check | `23514` | `275` | `3819` |

| constraint | answer | why |
|---|---|---|
| unique | 409 `already_exists` | two requests at once: the input was right, and the row was taken between the check and the write |
| foreign key | 409 `conflict` | the row it points at was deleted or changed in between |
| not null | 500 `internal_error` | a rule the serializer should have stated is missing - a bug, which the person cannot fix |
| check | 500 `internal_error` | the same |
| a code not known | 500 `internal_error` | unknown is refused |

A 500 here is every 500 (3.4): logged with its traceback, reported, raised
under `DEBUG` - a bug has been found. The message is always a generic,
translated sentence: neither the database's text nor a constraint's or a
column's name leaves the server. Which field was taken is the
serializer's to say.

### 3.6 The transaction

Every failure answered marks the request's transaction for rollback
(`set_rollback`), so a project with `ATOMIC_REQUESTS` never keeps half a
write behind an error.

### 3.7 Outside DRF

The handler covers what reaches a DRF view. An address matching no URL
never does. Two optional views answer those in the envelope too:

```python
handler404 = 'drf_parcel.views.not_found'
handler500 = 'drf_parcel.views.server_error'
```

---

## 4. Using it

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',  # the schema extra
}
```

Each line is independent: the handler alone gives the error envelope and
nothing else.

```python
from drf_parcel.pagination import CursorPagination
from drf_parcel.responses import EnvelopeMixin, success_response

class ProductViewSet(EnvelopeMixin, ModelViewSet):
    page_size = 12
    client_page_size = True
    max_page_size = 48
    envelope_messages = {'create': _('The product was added.')}

class NotificationViewSet(EnvelopeMixin, ModelViewSet):
    pagination_class = CursorPagination
    ordering = '-created_at'

class TotalsView(EnvelopeMixin, APIView):
    def get(self, request):
        return success_response(data={'total': 12}, message=_('Totals.'))
```

`EnvelopeMixin` wraps the response once, in `finalize_response`, so no
handler - `list`, `create`, a custom `@action` - has to remember.

---

## 5. Settings

One dictionary. A key the library does not know is refused at start-up
rather than ignored - a misspelt `PAGE_SZIE` that is silently ignored is a
page size that never changes, and nobody can tell why.

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
}
```

| key | default | what it decides |
|---|---|---|
| `PAGE_SIZE` | `20` | the page size when a view names none |
| `MAX_PAGE_SIZE` | `100` | the ceiling on a size the client chooses |
| `CLIENT_PAGE_SIZE` | `False` | whether the client may choose the size |
| `PAGE_SIZE_QUERY_PARAM` | `'page_size'` | the parameter it chooses it with |
| `FIELD_ERRORS` | `'detailed'` | `'detailed'`: `{code, message}` per problem; `'messages'`: the text alone, DRF's shape |
| `FIELD_PATH_SEPARATOR` | `'.'` | how a nested field's path is joined |
| `ERROR_CODES` | `{}` | a standard code renamed: `{'validation_error': 'validation_failed'}` |
| `HANDLE_INTEGRITY_ERRORS` | `False` | 3.5 |
| `RAISE_UNHANDLED_IN_DEBUG` | `True` | 3.4 |
| `REPORTER` | `None` | a dotted path to a function called with each 500 |

A view overrides the page settings with attributes of the same name in
lower case: `page_size`, `max_page_size`, `client_page_size`.

Checked at start-up: `MAX_PAGE_SIZE` below `PAGE_SIZE`, a `REPORTER` that
does not import, a code in `ERROR_CODES` the library does not have.

---

## 6. The schema

With the `schema` extra (`pip install 'drf-parcel[schema]'`), the generated
OpenAPI document says what the wire carries:

* every 2xx answer inside the envelope - `data` is the serializer,
  `pagination` the kind the view uses;
* `page_size` documented only on a view that lets the client choose it;
* the error envelope as one shared component, referenced by every
  operation, with `data.fields` on the ones that validate input.

A frontend generating its types from the schema then writes
`response.data.id`, which is what arrives.

---

## 7. Translation

Every message the library says is marked for translation and said in the
request's language. The library ships Persian; a project adds another
language in its own catalogue.

---

## 8. Open questions

For the owner to decide before stage 1.

1. ~~One code for a failed sign-in, or two?~~ **Decided: two**, DRF's own
   codes - `not_authenticated` (none sent) and `authentication_failed`
   (wrong or expired). A client renews a session on the second and only
   signs the person in on the first.
2. ~~`validation_failed` or `validation_error`?~~ **Decided:
   `validation_error`** - what three of the four projects' clients already
   read, and what the similar libraries say. DRF's own code, `invalid`, is
   also a field's code, so it is not used. The library's class is
   `InvalidInputError`.
3. ~~`IntegrityError`: 409 or 400?~~ **Decided: by the kind of constraint**,
   read from the driver's code (3.5).
4. **Default messages**: "Done." for every success (DayarDarman), or one per
   action - "Created.", "Deleted.", "List retrieved." (Elin, Hilacare)?
5. **`handler404` and `handler500`** (3.7): in the first release, or later?
