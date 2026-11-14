# ۱. قالب

## تنظیمات

سه خط در `REST_FRAMEWORK`، هر کدام مستقل از بقیه:

```python title="example/config/settings.py"
--8<-- "example/config/settings.py:rest_framework"
```

## یک ViewSet در قالب

```python title="example/shop/api.py"
--8<-- "example/shop/api.py:products"
```

سه نکته:

1. **`EnvelopeMixin` اول می‌آید.** پاسخ view را در `finalize_response`، یک
   بار، در قالب می‌گذارد - `list`، `create`، `destroy` و اکشن `restock` یکسان.
2. **`envelope_messages`** به یک اکشن جمله‌ی خودش را می‌دهد. هر اکشن دیگر
   پیام پیش‌فرض را می‌گوید، که از روی درخواست تعیین می‌شود.
3. **`restock` دستی جواب می‌دهد**، با `success_response`. پاسخی که از قبل در
   قالب است هرگز دو بار در قالب گذاشته نمی‌شود.

## هر پاسخ چه می‌گوید

وقتی کسی پیامی ننوشته، از روی درخواست تعیین می‌شود:

| درخواست | پیام |
|---|---|
| پاسخ `201` | Created. |
| `PUT` یا `PATCH` | Saved. |
| `DELETE` | Deleted. |
| هر چیز دیگر | Done. |

```bash
curl -X POST -H 'Content-Type: application/json' \
     -d '{"name": "Brooch", "price": "60.00"}' http://127.0.0.1:8000/api/products/
```

```json
{"success": true, "status_code": 201, "message": "The product was added.",
 "data": {"id": 29, "name": "Brooch", "price": "60.00", "stock": 0}}
```

جمله‌ی خود view، چون `create` یکی نام برده بود. پیام در سه سطح عوض می‌شود و
نزدیک‌ترین برنده است: یک پاسخ (`success_response(..., message=...)`)، یک view
(`envelope_messages`)، یا کل پروژه (`DRF_PARCEL['MESSAGES']`).

!!! note "حذف یعنی 200"

    `DELETE /api/products/29/` با **200** همراه با قالب و «Deleted.» جواب
    می‌دهد، نه 204. پاسخ 204 طبق تعریف بدنه ندارد، پس کلاینت چیزی برای خواندن
    نداشت.

## قدم بعد

[۲. صفحه‌ها](02-pages.md)
