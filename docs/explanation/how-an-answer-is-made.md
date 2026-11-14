# How an answer is made

## A success

1. The view answers - `Response(serializer.data)`, a paginator's page, or
   `success_response(...)`.
2. DRF calls the view's `finalize_response`, and `EnvelopeMixin` looks at
   what came back:
    * already an `EnvelopeResponse` - from `success_response` or the
      paginator - it is not wrapped again; only its default message is
      replaced with the one for this request;
    * a failure, something that is not JSON, or a view with `parcel_wrap =
      False` - it is left alone;
    * any other success - it is put in the envelope, with the view's headers
      and cookies kept, and a 204 answered as a 200.
3. The renderer writes the JSON.

That a response is in the envelope is said by its class, never guessed from
its keys: a payload of a view's own that happens to have a `success` key is
still a payload.

## A failure

The view raises. DRF calls the `EXCEPTION_HANDLER`:

1. Django's own `Http404`, `PermissionDenied` and `ValidationError` become
   DRF's.
2. DRF's own handler runs first, so the headers it adds - `Retry-After`,
   `WWW-Authenticate` - and its rollback stay.
3. A validation error: every problem flattened to a path, each with its
   code, the first said in `message`.
4. Any other `APIException` - DRF's, the library's, the project's: its
   status, its code, its detail, its `data`.
5. An `IntegrityError`, when the project turned the net on: by the kind the
   driver reports.
6. Anything else is a bug: raised under `DEBUG`; otherwise logged, reported,
   and answered with a sentence that says nothing.

Every failure answered marks the request's transaction for rollback, so a
project with `ATOMIC_REQUESTS` never keeps half a write behind an error.

## The shape, in one place

Both paths - and the paginators, and the schema - build the envelope through
one function, `build_envelope`, and describe it through one, `envelope_schema`.
Two places building it would, sooner or later, be two shapes.
