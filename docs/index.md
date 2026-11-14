# drf-parcel

One response shape for a Django REST framework API - success, page and error
alike - and the generated schema saying exactly that shape.

```json
{"success": true,  "status_code": 200, "message": "Done.", "data": {"id": 7, "name": "Ring"}}
```

```json
{"success": false, "status_code": 409, "message": "There is not enough of this product in stock.",
 "data": {"available": 0}, "error_code": "out_of_stock"}
```

A client reads one shape and never special-cases a payload: the answer is
under `data`, a person reads `message`, and code branches on `error_code` -
never on the message, which is translated.

<div class="grid cards" markdown>

- **Every answer in one envelope** - a viewset, a plain `APIView`, a custom
  `@action`, a page and a failure alike, with a message that says what
  happened.
- **Pages by number or by cursor**, chosen per view; the client chooses the
  page size where you allow it, and never gets more than the ceiling.
- **Every failure in the same envelope** - each field's problem with its
  code, DRF's and Django's errors with a standard code, your own errors with
  the `data` a client acts on, and a bug that never tells its secrets.
- **The schema says what arrives** - drf-spectacular documents the envelope,
  not only what is inside it, so a generated client reads `response.data.id`.

</div>

Your existing `APIException`s keep working, unchanged. Each part is used
alone, so a project adopts it one view at a time. Every sentence comes in
English and Persian.

## Install

```bash
pip install 'drf-parcel[schema]'
```

```python
INSTALLED_APPS = [..., 'rest_framework', 'drf_parcel']

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
}
```

## Where to go next

| | |
|---|---|
| [Quickstart](getting-started/quickstart.md) | a first view in the envelope, in five minutes |
| [The tutorial](tutorial/index.md) | the example shop, built a part at a time |
| [How-to guides](how-to/index.md) | one question a project meets, answered in a few steps - adopting it in an existing project first |
| [The contract](contract.md) | every shape, every error code, every setting - what the code promises |
| [Reference](reference/index.md) | settings, error codes, start-up checks, and the Python API |
| [Explanation](explanation/index.md) | why it is built the way it is, and how it compares |
| [Questions](faq.md) | what people ask first |
| [The example shop](https://github.com/amirAI-dot/drf-parcel/tree/main/example) | a project using all of it, to run |

Python 3.11 to 3.14; Django 5.2, 6.0 and 6.1; Django REST framework 3.16 and
later; drf-spectacular 0.28 and later, for the schema.
