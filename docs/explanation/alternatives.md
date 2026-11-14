# Alternatives

Several libraries do part of this. None, at the time of writing, does all of
it - both kinds of page in one envelope, a page size the client chooses under
a ceiling, every failure in the success's shape, and a schema that says the
envelope.

| library | what it does | how it differs |
|---|---|---|
| [drf-standardized-errors](https://pypi.org/project/drf-standardized-errors/) | errors only, in a `{type, errors: [...]}` shape; a mature OpenAPI integration | its failures are a different shape from successes, which it leaves alone |
| [drf-exceptions-hog](https://pypi.org/project/drf-exceptions-hog/) | errors only, `{type, code, detail, attr}` | errors only; no longer maintained |
| [drf-simple-api-errors](https://pypi.org/project/drf-simple-api-errors/) | errors only, after RFC 7807 | errors only |
| [drf-standardized-response](https://pypi.org/project/drf-standardized-response/) | successes, by a renderer; drf-spectacular support | a renderer must guess what is already wrapped; pages are not wrapped by default; no errors |
| [dj-response-formatter](https://pypi.org/project/dj-response-formatter/) | successes and failures, by a renderer | finds a page by its keys, so a field called `count` is taken for one; no cursor; no schema |
| [api-response-shaper](https://pypi.org/project/api-response-shaper/) | successes and failures, by a middleware | parses the rendered JSON again; no cursor; no schema |
| [api-response-toolkit](https://pypi.org/project/api-response-toolkit/) | helper functions and a handler | no cursor; no schema |

## Why a mixin, and not a renderer or a middleware

A renderer runs after the view, on data it did not make, so it has to guess
whether the data is already an envelope, and the schema never learns that it
wraps anything. A middleware is later still, and reads the rendered bytes
back. The mixin wraps in `finalize_response`, where the view is known: its
action, its message, whether it opted out - and the schema asks the same view
the same question.

## And drf-spectacular's own answer

drf-spectacular's FAQ answers "How do I wrap my responses?" with a helper
each project writes and applies to each operation. drf-parcel is that helper
written once - for every view, every page and every failure.
