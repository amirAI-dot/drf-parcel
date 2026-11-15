# Changelog

[فارسی](CHANGELOG.fa.md)

## Unreleased

## 0.2.0 - 2026-11-15

Changed - what leaves the server is not what it was:

* **A cursor is signed** with the project's `SECRET_KEY`, and carries the
  order it was made for. One changed by hand, made for another order, or
  signed with another key is `400 invalid_cursor` before the database is
  asked. The cursors given by 0.1.0 are refused: a client reads the feed again
  from the start. `SECRET_KEY_FALLBACKS` keeps cursors working across a key
  change. A cursor is signed, not encrypted - the documents now say so.
* **Every 5xx is logged and reported** - a designed one too: an
  `APIException` raised with a status of 500 or more, `ServiceUnavailableError`.
  It still says the message it was raised with.
* **A 205 is left as the view gave it**: it has no body to put the envelope
  in. `success_response(status_code=205)` is refused.

Fixed:

* **A bug while a feed is read is a bug again.** Telling a cursor the server
  cannot use from a broken row had meant answering every `ValueError`,
  `TypeError` or database error while a page was read as `invalid_cursor` -
  which hid the project's own bugs, unlogged, on every page after the first.
  A signed cursor is refused before the query, so nothing is caught around it.

* **A cursor that decodes and still cannot be used is a 400
  `invalid_cursor`**, as the contract says of every cursor the server cannot
  read. One written by hand, or kept while the list was re-sorted by another
  column, was a 500 - logged and reported as a bug - or a `validation_error`.
* **A view cached with `cache_page` on its method is cached again.** Wrapping
  the answer left the cache waiting for a response that was never rendered,
  so every request reached the view.
* **`error_response` marks the request's transaction for rollback**, as a
  raised failure does. Under `ATOMIC_REQUESTS`, what a view wrote before it
  returned a failure was kept.
* **What a model's `clean()` refuses is under `non_field_errors`**, not under
  Django's own key, `__all__`.
* **A failure raised with the code `invalid` keeps it.** Only a validation
  error is a `validation_error`; a refusal that carried `invalid` was sent as
  one, with no `data.fields`.
* **A failure whose class names no code answers in the envelope**, with DRF's
  own code, `error`, rather than as Django's 500.
* **A ceiling that is not above zero is no ceiling to choose under.** A view
  with `max_page_size = 0` answered the whole list, unpaged, to a client that
  sent a `page_size`; it now answers its own page size.
* **A type a view names with `Response(content_type=...)` is kept** when the
  answer is wrapped.
* **`PAGE_SIZE_QUERY_PARAM` set to `page` or `cursor` is reported at
  start-up** (`drf_parcel.E011`): the paginators read those themselves.
* The example's `restock` validates the quantity it is sent, and the guide to
  database constraints says when PostgreSQL checks a foreign key.
* The contract says that `OPTIONS` is in the envelope, that a view's own
  `page_size` has no ceiling, and that a `DictField` key holding the path
  separator makes an ambiguous path.

## 0.1.0 - 2026-11-14 - the first release

Everything [the contract](https://github.com/amirAI-dot/drf-parcel/blob/main/docs/contract.md) says, built.

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

Found by a review before the release, and fixed:

* `success_response(status_code=204)` answers 200 with its body, as every
  other 204 does - a 204 carries none, and the client read nothing.
* Django's `PermissionDenied` keeps the sentence it was raised with, as DRF's
  own handler does.
* A view with `parcel_wrap = False` is answered as DRF answers - its pages
  too, which were still in the envelope.
* An `ERROR_CODES` that cannot work never breaks the answer to a failure.
* The schema recognises a project's own handler built on the library's, and
  no longer fails when drf-spectacular names a page outside an operation.

Python 3.11 to 3.14; Django 5.2, 6.0 and 6.1; Django REST framework 3.16 and
later; drf-spectacular 0.28 and later.
