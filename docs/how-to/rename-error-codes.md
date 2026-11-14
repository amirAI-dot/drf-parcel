# Rename the error codes

A client that already branches on other words keeps them:

```python
DRF_PARCEL = {
    'ERROR_CODES': {
        'validation_error': 'validation_failed',
        'not_found': 'missing',
    },
}
```

Only the library's own codes are renamed - [the list](../reference/error-codes.md).
A project's own codes, `province_in_use`, are its own already. A key the
library does not send is reported by `manage.py check` (E008).

## The shape of a field's problems

```python
DRF_PARCEL = {'FIELD_ERRORS': 'messages'}
```

| `FIELD_ERRORS` | `data.fields.name` |
|---|---|
| `'detailed'` (default) | `[{"code": "required", "message": "This field is required."}]` |
| `'messages'` | `["This field is required."]` - DRF's own shape |

## A nested field's path

```python
DRF_PARCEL = {'FIELD_PATH_SEPARATOR': '/'}       # items/0/quantity
```
