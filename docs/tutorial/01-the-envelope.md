# 1. The envelope

## The settings

Three lines in `REST_FRAMEWORK`, each independent of the others:

```python title="example/config/settings.py"
--8<-- "example/config/settings.py:rest_framework"
```

## A viewset in the envelope

```python title="example/shop/api.py"
--8<-- "example/shop/api.py:products"
```

Three things to notice:

1. **`EnvelopeMixin` comes first.** It wraps what the view answers in
   `finalize_response`, once - `list`, `create`, `destroy` and the
   `restock` action alike.
2. **`envelope_messages`** gives one action a sentence of its own. Every
   other action says the default, read off the request.
3. **`restock` answers by hand** with `success_response`. An answer already in
   the envelope is never wrapped twice.

## What each answer says

When nobody wrote a message, it is read off the request:

| the request | the message |
|---|---|
| answered `201` | Created. |
| `PUT` or `PATCH` | Saved. |
| `DELETE` | Deleted. |
| anything else | Done. |

```bash
curl -X POST -H 'Content-Type: application/json' \
     -d '{"name": "Brooch", "price": "60.00"}' http://127.0.0.1:8000/api/products/
```

```json
{"success": true, "status_code": 201, "message": "The product was added.",
 "data": {"id": 29, "name": "Brooch", "price": "60.00", "stock": 0}}
```

The view's own sentence, because `create` named one. A message is replaced at
three levels, the nearest winning: one answer (`success_response(...,
message=...)`), one view (`envelope_messages`), or the whole project
(`DRF_PARCEL['MESSAGES']`).

!!! note "A delete is a 200"

    `DELETE /api/products/29/` answers **200** with the envelope and
    "Deleted.", not 204. A 204 carries no body by definition, so the client
    would have nothing to read.

## Next

[2. Pages](02-pages.md)
