# drf-parcel

یک شکل پاسخ برای API ساخته‌شده با Django REST framework - برای پاسخ موفق،
صفحه و خطا یکسان - و اسکیمایی که دقیقاً همان شکل را می‌گوید.

[English](https://github.com/amirAI-dot/drf-parcel/blob/main/README.md)

```json
{"success": true,  "status_code": 200, "message": "Done.",    "data": {"id": 7}}
{"success": true,  "status_code": 200, "message": "Done.",    "data": [], "pagination": {"type": "page", "count": 45, "page": 2, "pages": 3, "page_size": 20, "has_next": true, "has_previous": true}}
{"success": false, "status_code": 409, "message": "...",      "data": {"branches": 3}, "error_code": "province_in_use"}
```

کلاینت فقط یک شکل را می‌خواند و هیچ پاسخی را جداگانه مدیریت نمی‌کند: جواب
زیر `data` است، انسان `message` را می‌خواند، و کد بر اساس `error_code` تصمیم
می‌گیرد - هرگز بر اساس پیام، که ترجمه می‌شود.

## در یک پروژه

```bash
pip install 'drf-parcel[schema]'      # the schema extra brings drf-spectacular
```

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'drf_parcel',
]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
}
```

هر خط مستقل است: handler به‌تنهایی فقط قالب خطا را می‌دهد و نه چیز دیگری، و
پروژه بقیه را view به view به کار می‌گیرد.

```python
from drf_parcel.pagination import CursorPagination
from drf_parcel.responses import EnvelopeMixin, success_response


class ProductViewSet(EnvelopeMixin, ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    page_size = 12
    client_page_size = True          # the client may send ?page_size=
    max_page_size = 48               # and never gets more
    envelope_messages = {'create': _('The product was added.')}


class NotificationViewSet(EnvelopeMixin, ModelViewSet):
    pagination_class = CursorPagination
    ordering = '-created_at'


class TotalsView(EnvelopeMixin, APIView):
    def get(self, request):
        return success_response({'total': 12}, message=_('Totals.'))
```

`EnvelopeMixin` پاسخ view را یک بار، در `finalize_response`، در قالب
می‌گذارد، پس هیچ اکشنی - `list`، `create`، یک `@action` سفارشی - لازم نیست
یادش بماند. حذف به جای 204 بدون بدنه، 200 همراه با قالب جواب می‌دهد. فایل،
استریم، ریدایرکت یا CSV دست نمی‌خورد، و viewی هم که `parcel_wrap = False`
دارد.

یک فروشگاه که همه‌ی بخش‌های آن را به کار می‌برد، برای اجرا کردن و خواندن، در
[`example/`](example/README.fa.md) است.

## خطاها

```python
from drf_parcel.exceptions import DomainError


class ProvinceInUse(DomainError):
    status_code = 409
    default_code = 'province_in_use'
    default_detail = _('This province has branches and cannot be deleted.')


raise ProvinceInUse(data={'branches': 3})
```

`DomainError` همان `APIException` خود DRF است با `data` اضافه، پس خطاهای فعلی
پروژه بدون تغییر در قالب جواب می‌دهند. handler این کارها را هم می‌کند:

* در خطای اعتبارسنجی، اولین مشکل را در `message` و همه‌ی مشکل‌ها را در
  `data.fields` می‌گوید، هر کدام با کدش و با یک مسیر تخت - `items.0.quantity`؛
* خطاهای خود DRF و Django را با کد استاندارد جواب می‌دهد - `not_authenticated`،
  `permission_denied`، `not_found`، `rate_limited` با `retry_after` و ... - و
  هدرهایی را که DRF روی آن‌ها می‌گذارد حفظ می‌کند؛
* هر خطای پیش‌بینی‌نشده را با یک 500 عمومی جواب می‌دهد که متنش هرگز از سرور
  بیرون نمی‌رود: با traceback لاگ می‌شود و به `REPORTER` شما داده می‌شود. در
  `DEBUG` خطا بالا می‌رود تا صفحه‌ی Django آن را نشان بدهد؛
* نوشتن درخواست را پشت هر خطایی که جواب می‌دهد برمی‌گرداند.

## صفحه‌بندی

صفحه‌بندی شماره‌ای یا cursor، که هر view خودش انتخاب می‌کند. `pagination.type`
می‌گوید کدام است، تا یک کامپوننت در کلاینت هر دو را بخواند. کلاینت فقط جایی
تعداد هر صفحه را انتخاب می‌کند که view اجازه بدهد، و همیشه زیر سقف.

## اسکیما

با `ParcelAutoSchema` - یا `ParcelSchemaMixin` در `AutoSchema` خودتان - سند
OpenAPI همان چیزی را می‌گوید که واقعاً منتقل می‌شود: هر پاسخ موفق داخل قالب،
هر صفحه به‌عنوان قالب خودش، `page_size` فقط جایی که پذیرفته می‌شود، و قالب خطا
به‌عنوان پاسخ `default` هر عملیات.

## تنظیمات

یک دیکشنری، `DRF_PARCEL`. کلیدی که کتابخانه نمی‌شناسد پروژه را هنگام start
متوقف می‌کند، نه اینکه نادیده گرفته شود، و `manage.py check` مقداری را که کار
نمی‌کند گزارش می‌دهد. همه‌ی کلیدها، همه‌ی شکل‌ها و همه‌ی کدهای خطا در
[قرارداد](docs/contract.fa.md) آمده‌اند.

## زبان‌ها

هر جمله‌ای که کتابخانه می‌گوید به زبان درخواست است. فارسی همراه کتابخانه است؛
پیام‌های خود DRF به زبان‌هایی است که DRF دارد.

## پشتیبانی

Python 3.11 تا 3.14؛ Django 5.2، 6.0 و 6.1؛ Django REST framework 3.16 و
بالاتر؛ drf-spectacular 0.28 و بالاتر، برای اسکیما.

## کار روی پروژه

همه‌ی بررسی‌ها با [nox](https://nox.thea.codes) اجرا می‌شوند؛ همان sessionها
هم روی سیستم خودتان و هم در CI.

```bash
uv tool install nox
```

```bash
nox -s lint types tests
```

`tests` همه‌ی نسخه‌های پشتیبانی‌شده‌ی Python و Django را اجرا می‌کند؛ `oldest`
قدیمی‌ترین نسخه‌ی همه‌ی وابستگی‌ها را؛ و `package` فایل wheel را می‌سازد و
بررسی می‌کند چه چیزی در آن است. تست‌ها به‌طور پیش‌فرض روی SQLite اجرا می‌شوند،
و روی PostgreSQL با `DRF_PARCEL_TEST_DATABASE=postgres` و متغیرهای استاندارد
`PG*`.

بعد از تغییر یک رشته‌ی علامت‌خورده، آن را در
`src/drf_parcel/locale/fa/LC_MESSAGES/django.po` ترجمه و کامپایل کنید:

```bash
nox -s messages
```

## لایسنس

BSD 3-Clause - فایل [`LICENSE`](LICENSE) را ببینید.
