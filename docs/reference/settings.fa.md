# تنظیمات

## `DRF_PARCEL`

یک دیکشنری، همه‌ی کلیدها اختیاری. کلیدی که کتابخانه نمی‌شناسد پروژه را متوقف
می‌کند - `manage.py check` آن را گزارش می‌دهد (E001) - نه اینکه نادیده گرفته
شود: `PAGE_SZIE` اشتباهی که بی‌صدا نادیده گرفته شود، تعداد صفحه‌ای است که
هیچ‌وقت عوض نمی‌شود.

```python
DRF_PARCEL = {
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'CLIENT_PAGE_SIZE': False,
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
    'FIELD_ERRORS': 'detailed',
    'FIELD_PATH_SEPARATOR': '.',
    'ERROR_CODES': {},
    'HANDLE_INTEGRITY_ERRORS': False,
    'RAISE_UNHANDLED_IN_DEBUG': True,
    'REPORTER': None,
    'MESSAGES': {},
}
```

تنظیم در هر بار استفاده خوانده می‌شود، پس `override_settings` در یک تست
بلافاصله اثر می‌کند.

### صفحه‌ها

| کلید | پیش‌فرض | |
|---|---|---|
| `PAGE_SIZE` | `20` | تعداد هر صفحه وقتی view چیزی نگفته. اگر نوشته نشده باشد، `REST_FRAMEWORK['PAGE_SIZE']` خود DRF خوانده می‌شود اگر تنظیم شده باشد، و فقط بعد از آن ۲۰ |
| `MAX_PAGE_SIZE` | `100` | سقف تعدادی که کلاینت انتخاب می‌کند |
| `CLIENT_PAGE_SIZE` | `False` | آیا کلاینت می‌تواند تعداد را انتخاب کند |
| `PAGE_SIZE_QUERY_PARAM` | `'page_size'` | پارامتری که با آن انتخاب می‌کند |

### خطاها { #failures }

| کلید | پیش‌فرض | |
|---|---|---|
| `FIELD_ERRORS` | `'detailed'` | `'detailed'`: برای هر مشکل `{code, message}`؛ `'messages'`: فقط متن، شکل خود DRF |
| `FIELD_PATH_SEPARATOR` | `'.'` | مسیر فیلد تودرتو با چه چیزی وصل شود: `items.0.quantity` |
| `ERROR_CODES` | `{}` | تغییر اسم یک [کد استاندارد](error-codes.md): `{'validation_error': 'validation_failed'}` |
| `HANDLE_INTEGRITY_ERRORS` | `False` | جواب دادن به قید unique یا foreign key با 409 - [راهنما](../how-to/database-constraints.md) |
| `RAISE_UNHANDLED_IN_DEBUG` | `True` | در `DEBUG`، باگ را برای صفحه‌ی خطای Django بالا ببرد به جای جواب دادن با 500 |
| `REPORTER` | `None` | مسیر تابعی که به شکل `report(exc, context)` با هر 500 صدا زده می‌شود |

### پیام‌ها

| کلید | پیش‌فرض | |
|---|---|---|
| `MESSAGES` | `{}` | عوض کردن پیام پیش‌فرض پاسخ موفق، با کلیدش: `created`، `saved`، `deleted`، `done` |

## روی یک view

| attribute | پیش‌فرض | |
|---|---|---|
| `page_size` | مال پروژه | تعداد هر صفحه‌ی این view |
| `max_page_size` | مال پروژه | سقف این view |
| `client_page_size` | مال پروژه | آیا کلاینت این view می‌تواند تعداد را انتخاب کند |
| `ordering` | مال paginator | ترتیب cursor |
| `envelope_messages` | `{}` | پیام خود این view، بر اساس اکشن - `{'create': ...}` - یا در `APIView` ساده، بر اساس متد - `{'post': ...}` |
| `parcel_wrap` | `True` | `False` همه‌ی پاسخ‌های view را همان‌طور که DRF می‌دهد می‌گذارد |

## در `REST_FRAMEWORK`

| کلید | مقدار |
|---|---|
| `EXCEPTION_HANDLER` | `'drf_parcel.handlers.exception_handler'` |
| `DEFAULT_PAGINATION_CLASS` | `'drf_parcel.pagination.PageNumberPagination'` یا `'...CursorPagination'` |
| `DEFAULT_SCHEMA_CLASS` | `'drf_parcel.schema.ParcelAutoSchema'` |
| `NON_FIELD_ERRORS_KEY` | مال خود DRF؛ کلیدی که مشکل بدون فیلد در `data.fields` زیرش می‌آید |
