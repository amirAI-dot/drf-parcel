# فروشگاه نمونه

[English](README.md)

محصولاتی با موجودی، و سفارش‌هایی که از آن برمی‌دارند. همه‌ی بخش‌های
drf-parcel در آن هست، هر کدام در همان فایلی که یک پروژه آن را می‌گذارد:

| چه چیزی | کجا |
|---|---|
| سه خط `REST_FRAMEWORK`، تنظیم `DRF_PARCEL`، `LocaleMiddleware` | `config/settings.py` |
| اسکیما و صفحه‌ی Swagger آن | `config/urls.py` |
| صفحه‌بندی شماره‌ای، تعداد صفحه‌ای که کلاینت زیر سقف انتخاب می‌کند، پیام خود view، پاسخی که دستی نوشته شده | `ProductViewSet` در `shop/api.py` |
| فیدی که با cursor خوانده می‌شود، جدیدترین اول | `OrderViewSet` در `shop/api.py` |
| viewی که بیرون از قالب می‌ماند | `HealthView` در `shop/api.py` |
| خطاهای خود فروشگاه، با `data` - و یکی که پیش از کتابخانه نوشته شده | `shop/errors.py` |
| قانون‌هایی که آن‌ها را raise می‌کنند | `shop/services.py` |
| جایی که یک باگ گزارش می‌شود | `shop/reporting.py` |
| همه‌ی این‌ها چه جوابی می‌دهند | `shop/tests.py` |

## اجرا

از ریشه‌ی ریپو، با کتابخانه نصب‌شده در یک محیط تازه:

```bash
python -m venv .venv && .venv/bin/pip install -e '.[schema]'
```

```bash
cd example
```

```bash
../.venv/bin/python manage.py migrate
```

```bash
../.venv/bin/python manage.py example_data
```

```bash
../.venv/bin/python manage.py runserver
```

<http://127.0.0.1:8000/api/docs/> را باز کنید تا همه‌ی پاسخ‌ها را در اسکیما
ببینید، یا خودتان بپرسید:

```bash
curl 'http://127.0.0.1:8000/api/products/?page_size=3'
```

```json
{"success": true, "status_code": 200, "message": "Done.",
 "data": [{"id": 3, "name": "Bracelet", "price": "95.50", "stock": 0}, ...],
 "pagination": {"type": "page", "count": 28, "page": 1, "pages": 10, "page_size": 3,
                "has_next": true, "has_previous": false}}
```

```bash
curl -X POST -H 'Content-Type: application/json' -d '{"product": 3, "quantity": 1}' http://127.0.0.1:8000/api/orders/
```

```json
{"success": false, "status_code": 409, "message": "There is not enough of this product in stock.",
 "data": {"available": 0}, "error_code": "out_of_stock"}
```

```bash
curl -H 'Accept-Language: fa' http://127.0.0.1:8000/api/products/1/
```

همان پاسخ، با پیامش به فارسی.

| امتحان کنید | تا ببینید |
|---|---|
| `GET /api/products/?page=2` | یک صفحه‌ی شماره‌دار |
| `GET /api/products/?page_size=500` | سقف: ۲۰، نه ۵۰۰ |
| `POST /api/products/` با یک اسم | پیام خود view، «The product was added.» |
| `DELETE /api/products/1/` | محصولی که سفارش دارد: 409، `still_ordered`، و تعداد سفارش‌ها |
| `POST /api/products/1/restock/` | پاسخی که دستی نوشته شده، یک بار در قالب |
| `GET /api/orders/` و بعد `?cursor=` | فیدی که با cursor خوانده می‌شود |
| `POST /api/orders/` با `{}` | همه‌ی فیلدهای اشتباه، هر کدام با کدش |
| `GET /api/orders/2/receipt/` | خطایی که پیش از کتابخانه نوشته شده: 402، `payment_required` |
| `GET /api/health/` | `{"ok": true}` - viewی که بیرون مانده |

## تست‌هایش

```bash
../.venv/bin/python manage.py test
```

این تست‌ها روی بسته‌ی ساخته‌شده هم اجرا می‌شوند، با `nox -s package` از ریشه‌ی
ریپو - پس چیزی که منتشر می‌شود همان چیزی است که نمونه رویش اجرا می‌شود.
