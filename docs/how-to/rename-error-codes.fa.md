# تغییر اسم کدهای خطا

کلاینتی که از قبل بر اساس کلمه‌های دیگری تصمیم می‌گیرد آن‌ها را نگه می‌دارد:

```python
DRF_PARCEL = {
    'ERROR_CODES': {
        'validation_error': 'validation_failed',
        'not_found': 'missing',
    },
}
```

فقط کدهای خود کتابخانه تغییر اسم می‌دهند - [فهرستشان](../reference/error-codes.md).
کدهای خود پروژه، مثل `province_in_use`، از قبل مال خود پروژه‌اند. کلیدی که
کتابخانه نمی‌فرستد با `manage.py check` گزارش می‌شود (E008).

## شکل مشکل‌های یک فیلد

```python
DRF_PARCEL = {'FIELD_ERRORS': 'messages'}
```

| `FIELD_ERRORS` | `data.fields.name` |
|---|---|
| `'detailed'` (پیش‌فرض) | `[{"code": "required", "message": "This field is required."}]` |
| `'messages'` | `["This field is required."]` - شکل خود DRF |

## مسیر یک فیلد تودرتو

```python
DRF_PARCEL = {'FIELD_PATH_SEPARATOR': '/'}       # items/0/quantity
```
