# نصب

## بسته

```bash
pip install 'drf-parcel[schema]'      # with drf-spectacular, for the schema
pip install drf-parcel                # without it
```

Python 3.11 یا بالاتر، Django 5.2 یا بالاتر و Django REST framework 3.16 یا
بالاتر لازم است. بخش اختیاری `schema`، drf-spectacular 0.28 یا بالاتر را
نصب می‌کند؛ اگر پروژه سند OpenAPI نمی‌سازد آن را کنار بگذارید - هیچ چیز دیگری
در کتابخانه به آن نیاز ندارد.

## تنظیمات

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'drf_parcel',          # for its Persian catalogue and its start-up checks
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
}
```

**هر کدام از این سه خط مستقل است.** handler به‌تنهایی فقط قالب خطا را
می‌دهد؛ paginator به‌تنهایی لیست‌های صفحه‌بندی‌شده را در قالب می‌دهد؛ کلاس
اسکیما به‌تنهایی آنچه آن دو جواب می‌دهند را توصیف می‌کند. هر کدام را که پروژه
آماده‌اش است بردارید.

پاسخ‌های موفق یک view را `EnvelopeMixin` روی خود view در قالب می‌گذارد -
[شروع سریع](quickstart.md) را ببینید.

## زبان‌ها

پیام‌ها به زبان درخواست گفته می‌شوند. با `LocaleMiddleware` خود Django،
درخواستی با `Accept-Language: fa` به فارسی جواب داده می‌شود:

```python
MIDDLEWARE = [
    ...,
    'django.middleware.locale.LocaleMiddleware',
    ...,
]
```

## بررسی

```bash
python manage.py check
```

کلیدی در `DRF_PARCEL` که کتابخانه نمی‌شناسد، یا مقداری که کار نمی‌کند - سقفی
کمتر از تعداد صفحه، reporterی که import نمی‌شود - همین‌جا گزارش می‌شود، پیش از
اینکه کلاینتی به آن برخورد کند. همه‌ی بررسی‌ها در [مرجع](../reference/checks.md)
آمده‌اند.
