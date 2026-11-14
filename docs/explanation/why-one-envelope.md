# Why one envelope

DRF answers a list as a bare array, a page as `count`/`next`/`results`, an
object as itself, a validation failure as a dictionary of fields and any
other failure as `{"detail": ...}`. A client handles five shapes, and learns
which one it got by looking at the payload.

One envelope makes it one shape, decided by a key rather than guessed:

```json
{"success": true,  "status_code": 200, "message": "...", "data": ...}
{"success": false, "status_code": 409, "message": "...", "data": {...}, "error_code": "..."}
```

## Each key is for somebody

| key | for | why it is there |
|---|---|---|
| `success` | code | one boolean to branch on, before anything else is read |
| `status_code` | code, and logs | the status survives a proxy, a cache or a client that drops it |
| `message` | a person | one sentence, in the reader's language - a toast, an alert |
| `data` | code | the answer: an object, a list, or `{}` - never `null` |
| `pagination` | a pager | only on a paged list: a key that is absent says something |
| `error_code` | code | only on a failure: what a client branches on, stable when the message is reworded |

**A key is either always there or there for a reason.** An empty
`pagination` on a list that is not paged is a promise of pages that never
come; an `error_code` on a success is a code for nothing.

## A message is not a code

The message is translated and will be reworded. A client that compares it
breaks the day a sentence changes, or the day a person reads the page in
another language. So the message is for people, and every failure has a code
for programs.

## The cost

A client reads `response.data.id`, not `response.id` - one level deeper on
every answer. The schema says so, so a generated client gets it right; a
hand-written one learns it once. In exchange, error handling, pagination and
messages are written once, for every endpoint.
