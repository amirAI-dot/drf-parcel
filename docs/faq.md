# Questions

## A wrong address answers an HTML page, not the envelope

An address that matches no URL never reaches a DRF view, so it is Django's to
answer, with the project's `handler404`. That handler is the whole project's -
its admin site and web pages too - and the library does not reach into it.
See [the contract, 3.7](contract.md#outside-drf).

## I get 403 with `not_authenticated`, not 401

DRF answers 403 when the view's first authentication class sends no
`WWW-Authenticate` header - session authentication sends none. The code is
`not_authenticated` either way; branch on it, not on the status.

## `?page_size=` is ignored

The view does not let the client choose. Set `client_page_size = True` on the
view, or `DRF_PARCEL['CLIENT_PAGE_SIZE'] = True` for every view - and a size
above the ceiling is the ceiling.

## My generated client reads `response.id`, and it is undefined

The schema was generated without the library's schema class. Set
`DEFAULT_SCHEMA_CLASS` to `drf_parcel.schema.ParcelAutoSchema`, or mix
`ParcelSchemaMixin` into your own - then every success is the envelope in the
schema too, and the client reads `response.data.id`.

## The schema has no error envelope

It is documented only while failures are answered by the library's handler.
A project handler that calls it must say so with `functools.wraps` - see
[your own handler](how-to/own-schema-or-handler.md).

## The message is in English, though I sent `Accept-Language: fa`

Django's `LocaleMiddleware` is not installed, or `fa` is not in `LANGUAGES`.
The language is activated by the middleware; the library only says its
sentences in whatever is active.

## A view answers `success_response(...)` and the schema shows it bare

The view has no mixin. At runtime the answer is in the envelope - it was
built as one - but the schema can only tell from the view. Give it
`EnvelopeMixin`.

## A bug is raised in development instead of answered

Under `DEBUG`, so Django's error page shows the traceback. Set
`DRF_PARCEL['RAISE_UNHANDLED_IN_DEBUG'] = False` to see the envelope instead.

## Every cursor my clients hold became `invalid_cursor`

A cursor is signed with `SECRET_KEY` since 0.2.0, so the cursors given by
0.1.0 - unsigned - and those signed with a key since replaced are refused.
A client that gets `invalid_cursor` reads the feed again from the start,
without a cursor. To replace the key without this, put the old one in
Django's `SECRET_KEY_FALLBACKS` until the cursors given with it are spent.

## Can I keep my old error codes?

Yes - `ERROR_CODES` renames the library's own. See
[rename the error codes](how-to/rename-error-codes.md).

## Does it work with `async` views?

It works with whatever DRF supports. DRF's views are synchronous, and so is
everything here.
