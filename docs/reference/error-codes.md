# Error codes

Every code the library sends by itself. A client branches on these, never on
the message. Each can be renamed with [`ERROR_CODES`](settings.md#failures).

| status | `error_code` | raised by | `data` |
|---|---|---|---|
| 400 | `validation_error` | a serializer, Django's `ValidationError`, `InvalidInputError` | `fields`: every problem, by the flat path of its field |
| 400 | `parse_error` | a body that is not valid JSON | `{}` |
| 400 | `invalid_cursor` | a cursor the server cannot read | `{}` |
| 401 | `not_authenticated` | no credentials sent. 403, as DRF answers it, when the view's first authentication class sends no `WWW-Authenticate` - session authentication | `{}` |
| 401 | `authentication_failed` | wrong or expired credentials | `{}` |
| 403 | `permission_denied` | DRF's or Django's `PermissionDenied`, with the sentence it was raised with | `{}` |
| 404 | `not_found` | `NotFound`, Django's `Http404` - saying nothing of what was looked for | `{}` |
| 405 | `method_not_allowed` | a method the view has not got; `Allow` says which it has | `{}` |
| 406 | `not_acceptable` | an `Accept` nothing can answer | `{}` |
| 409 | `already_exists` | a unique constraint, with `HANDLE_INTEGRITY_ERRORS` | `{}` |
| 409 | `conflict` | a foreign-key constraint, with `HANDLE_INTEGRITY_ERRORS`; `ConflictError` | `{}` |
| 415 | `unsupported_media_type` | a body of a type the view does not read | `{}` |
| 429 | `rate_limited` | throttling; `Retry-After` says the same | `retry_after`, in seconds |
| 500 | `internal_error` | anything nobody designed | `{}` |
| 503 | `service_unavailable` | `ServiceUnavailableError` | `{}` |

A project's own error sends its own `default_code`, and the `data` it was
raised with - and is never renamed.

## `data.fields`

```json
{"name": [{"code": "required", "message": "This field is required."}],
 "items.0.quantity": [{"code": "min_value", "message": "Ensure this value is greater than or equal to 1."}],
 "non_field_errors": [{"code": "invalid", "message": "The dates are the wrong way round."}]}
```

Each problem's `code` is DRF's or Django's own: `required`, `blank`, `null`,
`invalid`, `max_length`, `min_length`, `max_value`, `min_value`, `unique`,
`does_not_exist`, `incorrect_type`, `invalid_choice` and the rest - or the
code a project's validator raised with.
