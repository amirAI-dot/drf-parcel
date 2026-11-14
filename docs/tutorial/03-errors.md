# 3. Errors

`EXCEPTION_HANDLER` is the library's, so every failure answers in the same
envelope, with `success: false` and an `error_code` a client branches on.

## Input that is wrong

```bash
curl -X POST -H 'Content-Type: application/json' -d '{"quantity": 0}' \
     http://127.0.0.1:8000/api/orders/
```

```json
{"success": false, "status_code": 400, "error_code": "validation_error",
 "message": "This field is required.",
 "data": {"fields": {
   "product": [{"code": "required", "message": "This field is required."}],
   "quantity": [{"code": "min_value", "message": "Ensure this value is greater than or equal to 1."}]}}}
```

The first problem in `message`, for a screen that shows one sentence; every
problem in `data.fields`, for a form that marks each field - each with a
`code`, so a client tells "empty" from "too small" without reading
translated text. A nested field is one flat path: `items.0.quantity`.

## The shop's own errors

```python title="example/shop/errors.py"
--8<-- "example/shop/errors.py:domain"
```

A service raises them, with what a client can act on in `data`:

```python title="example/shop/services.py"
--8<-- "example/shop/services.py:place_order"
```

```bash
curl -X POST -H 'Content-Type: application/json' -d '{"product": 3, "quantity": 1}' \
     http://127.0.0.1:8000/api/orders/
```

```json
{"success": false, "status_code": 409, "message": "There is not enough of this product in stock.",
 "data": {"available": 0}, "error_code": "out_of_stock"}
```

## An error written before the library

A project's errors from before it - DRF's `APIException`, no `data` - answer
in the envelope unchanged:

```python title="example/shop/errors.py"
--8<-- "example/shop/errors.py:legacy"
```

```json
{"success": false, "status_code": 402, "message": "This order is not paid yet.",
 "data": {}, "error_code": "payment_required"}
```

## A bug

Anything nobody designed answers a generic 500. Its text - which can hold a
query, a file path, a person's name - never leaves the server. It is logged
with its traceback and handed to the `REPORTER` the settings name:

```python title="example/config/settings.py"
--8<-- "example/config/settings.py:drf_parcel"
```

```json
{"success": false, "status_code": 500, "message": "Something went wrong. Please try again.",
 "data": {}, "error_code": "internal_error"}
```

Under `DEBUG` it is raised instead, so Django's error page shows it.

Every code the library sends is in [the reference](../reference/error-codes.md).

## Next

[4. The schema and languages](04-schema-and-languages.md)
