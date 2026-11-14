# Changelog

[فارسی](CHANGELOG.fa.md)

## Unreleased - the first release

Everything [the contract](docs/contract.md) says, built.

* **The envelope** - `success`, `status_code`, `message` and `data` on every
  answer; `pagination` on a paged list; `error_code` on a failure. Built in
  one place, which refuses to build it wrong.
* **A success says what happened** - Created, Saved, Deleted or Done, read off
  the request, and replaced per answer, per view or for the project.
* **`EnvelopeMixin`** wraps a view's successes once. A delete answers 200 with
  the envelope. What is not JSON, and a view that opts out, is left alone.
* **Pagination** by page number or by cursor, chosen per view. A client
  chooses the page size only where a view allows it, always under a ceiling.
  DRF's own `PAGE_SIZE` is kept when the library is not told one.
* **The exception handler** answers every failure in the envelope:
  validation errors with every field's problem and its code at a flat path;
  DRF's and Django's failures with a standard code and their headers; a
  project's own `APIException` unchanged; a constraint the database refuses
  by its kind, when turned on; and a bug with a generic 500 whose text never
  leaves the server - logged, reported, and raised under `DEBUG`. Every
  failure undoes the request's write.
* **`DomainError`** - DRF's `APIException` with `data` - and the common errors.
* **The schema** with drf-spectacular: every success, page and failure as the
  client receives it.
* **The `DRF_PARCEL` setting** refuses a key it does not know, and
  `manage.py check` reports a value that cannot work.
* **Persian**, for every sentence the library says.

Python 3.11 to 3.14; Django 5.2, 6.0 and 6.1; Django REST framework 3.16 and
later; drf-spectacular 0.28 and later.
