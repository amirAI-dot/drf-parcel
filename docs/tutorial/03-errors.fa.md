# ۳. خطاها

`EXCEPTION_HANDLER` مال کتابخانه است، پس هر خطایی در همان قالب جواب داده
می‌شود، با `success: false` و یک `error_code` که کلاینت بر اساسش تصمیم
می‌گیرد.

## ورودی‌ای که اشتباه است

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

اولین مشکل در `message`، برای صفحه‌ای که یک جمله نشان می‌دهد؛ همه‌ی مشکل‌ها در
`data.fields`، برای فرمی که زیر هر فیلد خطا می‌گذارد - هر کدام با یک `code`،
تا کلاینت «خالی» را از «خیلی کوچک» تشخیص بدهد بدون اینکه متن ترجمه‌شده را
بخواند. فیلد تودرتو یک مسیر تخت است: `items.0.quantity`.

## خطاهای خود فروشگاه

```python title="example/shop/errors.py"
--8<-- "example/shop/errors.py:domain"
```

یک سرویس آن‌ها را raise می‌کند، با چیزی که کلاینت بر اساسش کاری می‌کند در
`data`:

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

## خطایی که پیش از کتابخانه نوشته شده

خطاهای پروژه از پیش از کتابخانه - `APIException` خود DRF، بدون `data` - بدون
تغییر در قالب جواب می‌دهند:

```python title="example/shop/errors.py"
--8<-- "example/shop/errors.py:legacy"
```

```json
{"success": false, "status_code": 402, "message": "This order is not paid yet.",
 "data": {}, "error_code": "payment_required"}
```

## یک باگ

هر چیزی که کسی طراحی‌اش نکرده با یک 500 عمومی جواب داده می‌شود. متنش - که
ممکن است یک کوئری، مسیر یک فایل یا اسم یک نفر را داشته باشد - هرگز از سرور
بیرون نمی‌رود. با traceback لاگ می‌شود و به `REPORTER`ی داده می‌شود که
تنظیمات نام می‌برد:

```python title="example/config/settings.py"
--8<-- "example/config/settings.py:drf_parcel"
```

```json
{"success": false, "status_code": 500, "message": "Something went wrong. Please try again.",
 "data": {}, "error_code": "internal_error"}
```

در `DEBUG` به جای جواب، خطا بالا می‌رود تا صفحه‌ی خطای Django آن را نشان بدهد.

همه‌ی کدهایی که کتابخانه می‌فرستد در [مرجع](../reference/error-codes.md) آمده‌اند.

## قدم بعد

[۴. اسکیما و زبان‌ها](04-schema-and-languages.md)
