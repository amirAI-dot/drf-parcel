# ۲. صفحه‌ها

## صفحه‌بندی شماره‌ای، به‌طور پیش‌فرض

`DEFAULT_PAGINATION_CLASS` همان `PageNumberPagination` کتابخانه است، پس هر
لیستی یک صفحه است - محصولات هم:

```bash
curl 'http://127.0.0.1:8000/api/products/?page=2'
```

```json
{"success": true, "status_code": 200, "message": "Done.",
 "data": [...],
 "pagination": {"type": "page", "count": 28, "page": 2, "pages": 3, "page_size": 10,
                "has_next": true, "has_previous": true}}
```

لینک `next`ی برای دنبال کردن نیست: کلاینت روی دامنه‌ی دیگری است و خودش
`?page=3` را می‌خواهد.

## کلاینت تعداد را انتخاب می‌کند، زیر سقف

ViewSet محصولات در [قدم ۱](01-the-envelope.md) دو attribute دارد:

```python
client_page_size = True
max_page_size = 20
```

| کلاینت می‌خواهد | می‌گیرد |
|---|---|
| `?page_size=5` | ۵ |
| `?page_size=500` | ۲۰ - سقف، نه خطا |
| `?page_size=abc`، `0`، یا هیچ | ۱۰ - `PAGE_SIZE` پروژه |

`pagination.page_size` همیشه تعدادی را که اعمال شده می‌گوید. viewی که اجازه
نمی‌دهد پارامتر را نادیده می‌گیرد، و اسکیما هم آن را پیشنهاد نمی‌کند.

## سفارش‌ها، به‌عنوان فید

سفارش‌ها جدیدترین اول خوانده می‌شوند، و آن‌قدر زیادند که در هر درخواست شمرده
نشوند - cursor، نه شماره‌ی صفحه:

```python title="example/shop/api.py"
--8<-- "example/shop/api.py:orders"
```

```bash
curl http://127.0.0.1:8000/api/orders/
```

```json
{"success": true, "status_code": 200, "message": "Done.",
 "data": [{"id": 2, "product": 1, "quantity": 2, "paid": false, "created_at": "..."}, ...],
 "pagination": {"type": "cursor", "next_cursor": "cD0yMDI2...", "previous_cursor": null,
                "page_size": 10, "has_next": true, "has_previous": false}}
```

کلاینت همان چیزی را که گرفته پس می‌فرستد - `?cursor=cD0yMDI2...` - و هرگز
خودش یکی نمی‌سازد. `has_next` در هر دو نوع هست، پس یک دکمه‌ی «بیشتر» با هر دو
کار می‌کند، و `pagination.type` آن‌ها را از هم جدا می‌کند.

## قدم بعد

[۳. خطاها](03-errors.md)
