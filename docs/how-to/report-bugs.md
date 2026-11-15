# Report bugs to Sentry

An unexpected exception answers a generic 500, logged on the `drf_parcel`
logger with its traceback - and handed to the project's reporter:

```python
DRF_PARCEL = {'REPORTER': 'config.reporting.report'}
```

```python
# config/reporting.py
import sentry_sdk


def report(exc, context):
    sentry_sdk.capture_exception(exc)
```

`context` is DRF's - the `view`, the `request`. The reporter is called with
each 5xx: a bug, and a 5xx raised on purpose too - a `ServiceUnavailableError`,
an `APIException` with a status of 500 - because the server failing is
worth hearing about either way. A 4xx is never reported: a 404, a wrong phone
number or a `DomainError` is not the server failing. A reporter that fails
costs a log line, not the answer.

A 5xx raised on purpose says the message it was raised with, so that message
must never be an exception's text: `raise ServiceUnavailableError()`, not
`raise ServiceUnavailableError(str(error))`.

!!! tip "Sentry's logging integration - one or the other"

    Django never sees the exception: the library answered the 500. But the
    library logs it at `ERROR` with its traceback, and Sentry's logging
    integration - on by default - turns that line into an event already. Use
    that, or the `REPORTER`, not both: with both, each bug is reported twice.
    The `REPORTER` is for a tool that does not read the log, or for adding the
    request's details yourself.

## DEBUG

Under `DEBUG = True` the exception is raised instead, so Django's error page
shows the traceback. To see the envelope in development:

```python
DRF_PARCEL = {'RAISE_UNHANDLED_IN_DEBUG': False}
```
