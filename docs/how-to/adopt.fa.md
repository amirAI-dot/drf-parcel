# به کار گرفتن در یک پروژه‌ی موجود

پروژه‌ای که از قبل در قالب خودش جواب می‌دهد - یک تابع `success_response`،
یک mixin که `list` و `create` را بازنویسی می‌کند، یک exception handler -
بخش به بخش به کتابخانه منتقل می‌شود، و خطاهایش بدون تغییر کار می‌کنند.

## ۱. شکل‌ها را مقایسه کنید

آنچه کلاینتِ یک قالب دست‌ساز رایج می‌خواند، و آنچه بعد از آن می‌خواند:

| | قبل - یک قالب دست‌ساز رایج | بعد |
|---|---|---|
| پاسخ موفق | `success`، `status_code`، `message`، `data` | همان |
| صفحه | `next`، `previous`، `total_pages`، `current_page`، `page_size` | `type`، `count`، `page`، `pages`، `page_size`، `has_next`، `has_previous` |
| اعتبارسنجی | اولین مشکل در `message` | اولین مشکل در `message` **و** همه‌ی مشکل‌ها در `data.fields` |
| کد | `validation_error`، `authentication_error`، ... | [کدهای استاندارد](../reference/error-codes.md)، و اگر بخواهید با اسم‌های خودتان |
| حذف | اغلب 204 با بدنه‌ای که به کسی نمی‌رسد | 200 همراه با قالب |

شکل پاسخ موفق و `message` همان می‌مانند. چیزی که فرانت باید عوض کند صفحه‌بند
است، و فقط اگر `next` و `current_page` را می‌خواند.

## ۲. اول handler را نصب کنید

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
}
```

handler خود پروژه را حذف کنید. زیرکلاس‌های `APIException` آن تغییری لازم
ندارند: هر کدام با `status_code` خودش، `default_code` خودش به‌عنوان
`error_code` و `detail` خودش به‌عنوان `message` جواب می‌دهد - و `data`، اگر
داشته باشد.

اگر کلاینت‌ها بر اساس کدهای قدیمی تصمیم می‌گیرند، نگهشان دارید:

```python
DRF_PARCEL = {
    'ERROR_CODES': {
        'not_authenticated': 'authentication_error',
        'authentication_failed': 'authentication_error',
    },
}
```

کدهای خود پروژه هرگز تغییر اسم نمی‌دهند - فقط کدهای کتابخانه.

## ۳. mixin را جایگزین کنید

هر جا view، mixin پروژه را داشت، به جایش `EnvelopeMixin` بدهید و `list`،
`create`، `retrieve`، `update` و `destroy` بازنویسی‌شده را حذف کنید: mixin
هر چه view جواب بدهد را در یک جا در قالب می‌گذارد.

```python
from drf_parcel.responses import EnvelopeMixin, success_response
```

viewی که `success_response(request, data=...)` پروژه را صدا می‌زد،
`success_response(data)` کتابخانه را صدا می‌زند - بدون `request`، و با
`message` فقط وقتی چیزی برای گفتن دارد.

## ۴. paginator را جایگزین کنید

```python
REST_FRAMEWORK = {
    ...,
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
}
```

پروژه‌ای که `REST_FRAMEWORK['PAGE_SIZE']` را تنظیم کرده، تعدادش را نگه
می‌دارد: کتابخانه وقتی `DRF_PARCEL['PAGE_SIZE']` تنظیم نشده، آن را می‌خواند.
اگر آن تعداد بیشتر از ۱۰۰ است، `DRF_PARCEL['MAX_PAGE_SIZE']` را هم بالا
ببرید - `manage.py check` این را می‌گوید (E003).

## ۵. بررسی، بعد تست

```bash
python manage.py check
python manage.py test
```

تست‌هایی که `response.data['next']` یا یک 204 را می‌خوانند با شکل‌های قدم ۱
عوض می‌شوند؛ بقیه مثل قبل پاس می‌شوند. اگر پروژه بزرگ است، آن را app به app به
کار بگیرید: هر viewی که mixin ندارد مثل قبل جواب می‌دهد.
