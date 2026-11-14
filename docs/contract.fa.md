# قرارداد

> **وضعیت: پیش‌نویس، برای تصمیم مالک پروژه.** هر شکلی که از سرور بیرون
> می‌رود، هر کد خطا، و هر تنظیم. کد از این سند پیروی می‌کند؛ هر تغییری در
> آنچه به کلاینت می‌رسد، اول اینجا تغییر می‌کند. سؤال‌هایی که هنوز باز
> هستند در انتها آمده‌اند.
>
> English: [`contract.md`](contract.md).

پیام‌های نمونه‌ی زیر به انگلیسی نوشته شده‌اند؛ در عمل هر پیام به زبان
درخواست (`Accept-Language`) گفته می‌شود.

---

## ۱. قالب پاسخ

همه‌ی پاسخ‌ها - موفق و ناموفق - یک سطح بالای یکسان دارند، تا کلاینت فقط
یک شکل را بخواند و هیچ پاسخی را جداگانه مدیریت نکند.

| کلید | نوع | کِی هست | معنی |
|---|---|---|---|
| `success` | بولی | همیشه | آیا درخواست کاری را که خواسته بود انجام داد |
| `status_code` | عدد | همیشه | کد HTTP، تکرار شده در بدنه |
| `message` | متن | همیشه | یک جمله برای انسان، به زبان درخواست |
| `data` | شیء یا آرایه | همیشه | جواب: یک شیء، یک لیست، یا `{}` |
| `pagination` | شیء | فقط در لیست صفحه‌بندی‌شده | چطور صفحه‌ی بعد را بخواهیم |
| `error_code` | متن | فقط در خطا | چیزی که کد کلاینت بر اساسش تصمیم می‌گیرد |

قانون‌ها:

* **یک کلید یا همیشه هست، یا به دلیلی هست.** `pagination` روی لیستی که
  صفحه‌بندی ندارد قولی توخالی است؛ `error_code` روی پاسخ موفق کدی برای
  هیچ چیز. هیچ‌کدام هرگز خالی فرستاده نمی‌شوند.
* **`data` هیچ‌وقت `null` نیست.** چیزی برای گفتن نبودن یعنی `{}`.
* **`message` برای انسان است، `error_code` برای کد.** پیام ترجمه می‌شود و
  عوض خواهد شد؛ کلاینتی که آن را مقایسه کند، روزی که جمله‌ای بازنویسی شود
  خراب می‌شود.
* **`status_code` همیشه با کد HTTP همان پاسخ برابر است.**

### یک شیء

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": {"id": 7, "name": "Ring"}
}
```

### ساخته شد

```json
{
  "success": true,
  "status_code": 201,
  "message": "Created.",
  "data": {"id": 8, "name": "Necklace"}
}
```

### حذف شد

پاسخ `204 No Content` طبق تعریف بدنه ندارد، پس قالب دور ریخته می‌شد. حذف
به جای آن **200** همراه با قالب برمی‌گرداند:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Deleted.",
  "data": {}
}
```

### لیستی که صفحه‌بندی ندارد

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": [{"id": 1}, {"id": 2}]
}
```

### چیزهایی که هرگز قالب‌بندی نمی‌شوند

* پاسخی که JSON نیست - فایل، PDF، استریم، ریدایرکت؛
* viewی که خودش بیرون می‌ماند (`parcel_wrap = False`)، برای webhook یا
  health check که فراخواننده‌اش شکل خودش را انتظار دارد؛
* پاسخی که از قبل در قالب است - `success_response` یکی برمی‌گرداند، و دو
  بار قالب‌بندی نمی‌شود.

---

## ۲. صفحه‌بندی

دو نوع، و **هر view خودش انتخاب می‌کند** - در یکی لیست شماره‌دار، در دیگری
فید بی‌پایان. `pagination.type` می‌گوید کدام است، تا یک کامپوننت در کلاینت
هر دو را بدون حدس زدن بخواند.

### با شماره‌ی صفحه

`GET /products/?page=2&page_size=20`

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": [{"id": 21}, {"id": 22}],
  "pagination": {
    "type": "page",
    "count": 45,
    "page": 2,
    "pages": 3,
    "page_size": 20,
    "has_next": true,
    "has_previous": true
  }
}
```

| کلید | معنی |
|---|---|
| `count` | تعداد ردیف‌های کل لیست |
| `page` | این صفحه، از ۱ |
| `pages` | تعداد صفحه‌ها |
| `page_size` | اندازه‌ای که واقعاً اعمال شد - بعد از سقف، بخش ۲.۳ |
| `has_next`، `has_previous` | آیا صفحه‌ی بعد و قبل وجود دارد |

لینک `next` و `previous` نداریم: کلاینت روی دامنه‌ی دیگری است و `?page=3`
را خودش می‌سازد، و سرور پشت پروکسی لینک‌ها را با پروتکل یا دامنه‌ی اشتباه
می‌سازد.

صفحه‌ای بعد از آخرین صفحه **404** (`not_found`) است، همان‌طور که DRF می‌کند.

### با cursor

`GET /notifications/?cursor=cD0yMDI2LTExLTE0&page_size=20`

```json
{
  "success": true,
  "status_code": 200,
  "message": "Done.",
  "data": [{"id": 90}, {"id": 89}],
  "pagination": {
    "type": "cursor",
    "next_cursor": "cD0yMDI2LTExLTEz",
    "previous_cursor": "cj0xJnA9MjAyNi0xMS0xNA",
    "page_size": 20,
    "has_next": true,
    "has_previous": true
  }
}
```

cursor مات است: کلاینت همان چیزی را که گرفته پس می‌فرستد و هرگز خودش یکی
نمی‌سازد. `count` و `page` ندارد - نشمردن، روی جدولی که بزرگ‌تر از آن است
که در هر درخواست شمرده شود، کل فایده‌ی cursor است. `has_next` در هر دو نوع
هست، پس دکمه‌ی «بیشتر» با هر دو کار می‌کند.

cursorی که سرور نتواند بخواند **400** (`invalid_cursor`) است.

### ۲.۳ انتخاب تعداد هر صفحه توسط کلاینت

به‌طور پیش‌فرض خاموش. وقتی view اجازه بدهد، کلاینت `?page_size=` می‌فرستد،
و سرور **همیشه** سقف اعمال می‌کند - بدون سقف، `?page_size=1000000` یعنی
خواندن کل جدول، که برای هر کسی باز است.

| کلاینت می‌فرستد | سرور اعمال می‌کند |
|---|---|
| هیچ | `page_size` خود view |
| `24`، زیر سقف | ۲۴ |
| `500`، بالای سقف | سقف - بدون خطا: صفحه‌بندی جای سخت‌گیری نیست |
| `0`، `-3`، `abc` | `page_size` خود view |
| هر چیزی، وقتی view اجازه نمی‌دهد | `page_size` خود view؛ پارامتر نادیده گرفته می‌شود و **در اسکیما نیست** |

`pagination.page_size` همیشه اندازه‌ی اعمال‌شده را می‌گوید، پس کلاینتی که
۵۰۰ خواسته می‌بیند که ۱۰۰ گرفته.

---

## ۳. خطاها

همان قالب، با `success: false` و یک `error_code`.

```json
{
  "success": false,
  "status_code": 409,
  "error_code": "province_in_use",
  "message": "This province has branches and cannot be deleted.",
  "data": {"branches": 3}
}
```

`data` چیزی را دارد که کلاینت می‌تواند بر اساسش کاری بکند - کدام رکورد سر
راه است، چقدر باید صبر کند. وقتی چیزی نیست `{}` است.

### ۳.۱ اعتبارسنجی

اولین مشکل در `message`، همه‌ی مشکل‌ها در `data.fields`:

```json
{
  "success": false,
  "status_code": 400,
  "error_code": "validation_failed",
  "message": "Enter a valid phone number.",
  "data": {
    "fields": {
      "phone": [{"code": "invalid", "message": "Enter a valid phone number."}],
      "items.0.quantity": [{"code": "min_value", "message": "Ensure this value is greater than or equal to 1."}],
      "non_field_errors": [{"code": "invalid", "message": "The dates are the wrong way round."}]
    }
  }
}
```

* صفحه‌ای که یک جمله نشان می‌دهد `message` را می‌خواند؛ فرمی که زیر هر فیلد
  خطا می‌گذارد `fields` را - و کلاینتی که برای شکل قدیمی (فقط یک پیام)
  نوشته شده همچنان کار می‌کند.
* هر مشکل **`code`** خودش را دارد (`required`، `max_length`، `unique`،
  `invalid` و ...) تا کلاینت «خالی» را از «تکراری» تشخیص بدهد بدون اینکه
  متن ترجمه‌شده را بخواند.
* فیلد تودرتو یک **مسیر تخت** است که با `.` به هم وصل می‌شود:
  `items.0.quantity` یعنی تعداد اولین آیتم.
* خطاهایی که مال هیچ فیلدی نیستند زیر کلید خود DRF هستند،
  `non_field_errors` (تنظیم `NON_FIELD_ERRORS_KEY` آن).
* `ValidationError` خود Django - `clean()` یک مدل، یک سرویس - دقیقاً به
  همین شکل برمی‌گردد.

### ۳.۲ کدهای خطای استاندارد

| وضعیت | `error_code` | از کجا | `data` |
|---|---|---|---|
| 400 | `validation_failed` | serializer، یا `ValidationError` خود Django | `fields` |
| 400 | `parse_error` | بدنه‌ای که JSON معتبر نیست | `{}` |
| 400 | `invalid_cursor` | cursorی که سرور نمی‌تواند بخواند | `{}` |
| 401 | `not_authenticated` | اطلاعات ورود فرستاده نشده | `{}` |
| 401 | `authentication_failed` | اطلاعات ورود اشتباه یا منقضی | `{}` |
| 403 | `permission_denied` | `PermissionDenied` در DRF یا Django | `{}` |
| 404 | `not_found` | `NotFound`، یا `Http404` خود Django | `{}` |
| 405 | `method_not_allowed` | متدی که view ندارد | `{}` |
| 406 | `not_acceptable` | `Accept`ی که کسی جوابش را ندارد | `{}` |
| 409 | `conflict` | `IntegrityError`، وقتی روشن باشد (۳.۵) | `{}` |
| 415 | `unsupported_media_type` | نوع بدنه‌ای که view نمی‌خواند | `{}` |
| 429 | `rate_limited` | محدودیت تعداد درخواست | `retry_after`، به ثانیه |
| 500 | `internal_error` | هر چیزی که کسی طراحی‌اش نکرده | `{}` |
| 503 | `service_unavailable` | `ServiceUnavailableError` | `{}` |

اسم هر کد در تنظیمات (`ERROR_CODES`) قابل تغییر است، برای پروژه‌ای که
کلاینت‌هایش از قبل بر اساس کلمه‌های دیگری تصمیم می‌گیرند.

**هدرها حفظ می‌شوند.** DRF روی 429 هدر `Retry-After`، روی 405 هدر `Allow`
و روی 401 هدر `WWW-Authenticate` می‌گذارد؛ همه روی پاسخ می‌مانند.

### ۳.۳ خطاهای خود پروژه

```python
from drf_parcel.exceptions import DomainError

class ProvinceInUse(DomainError):
    status_code = 409
    error_code = 'province_in_use'
    default_message = _('This province has branches and cannot be deleted.')

raise ProvinceInUse(data={'branches': 3})
raise ProvinceInUse(_('Move its 3 branches first.'), data={'branches': 3})
```

`DomainError` از DRF نمی‌آید: سرویس آن را raise می‌کند، و قانون برقرار
می‌ماند چه از view برسد، چه از تسک Celery، چه از management command.
کتابخانه خطاهای رایج را همراه خودش دارد - `ValidationFailedError`،
`AuthenticationFailedError`، `PermissionDeniedError`، `NotFoundError`،
`ConflictError`، `RateLimitedError`، `ServiceUnavailableError`.

**خطاهای فعلی پروژه همچنان کار می‌کنند.** هر زیرکلاس `APIException` در DRF
بدون هیچ تغییری در قالب جواب می‌دهد: `status_code` خودش، `default_code`
خودش به‌عنوان `error_code`، و `detail` خودش به‌عنوان `message`.

### ۳.۴ چیزی که هرگز گفته نمی‌شود

خطای پیش‌بینی‌نشده با **500** و یک جمله‌ی عمومی جواب داده می‌شود. متن آن
هرگز از سرور بیرون نمی‌رود - ممکن است یک کوئری، مسیر یک فایل یا اسم یک نفر
در آن باشد - و فقط همین خطاست که با traceback به‌عنوان error لاگ می‌شود.
یک 404 یا یک شماره‌ی تلفن اشتباه اصلاً به‌عنوان error لاگ نمی‌شود.

* با `DEBUG = True` به جای جواب، خطا بالا می‌رود تا صفحه‌ی خطای Django
  traceback را نشان بدهد (`RAISE_UNHANDLED_IN_DEBUG`).
* `REPORTER` تابعی است که با هر 500 صدا زده می‌شود - برای Sentry یا هر
  ابزار مشابه.

### ۳.۵ یکپارچگی دیتابیس

به‌طور پیش‌فرض خاموش. رسیدن خطای unique یا not-null به view یعنی قانونی که
serializer یا سرویس باید می‌گفت جا افتاده است. پروژه‌ای که تور ایمنی
می‌خواهد `HANDLE_INTEGRITY_ERRORS` را روشن می‌کند: آن وقت این خطا با 409
`conflict` و یک جمله‌ی عمومی جواب داده می‌شود، و هرگز با متن دیتابیس.

### ۳.۶ تراکنش

هر خطایی که جواب داده می‌شود، تراکنش درخواست را برای rollback علامت می‌زند
(`set_rollback`)، تا پروژه‌ای که `ATOMIC_REQUESTS` دارد هرگز نیمی از یک
نوشتن را پشت یک خطا نگه ندارد.

### ۳.۷ بیرون از DRF

handler فقط چیزی را می‌پوشاند که به یک view در DRF برسد. آدرسی که با هیچ
URLی جور نیست هیچ‌وقت نمی‌رسد. دو view اختیاری آن‌ها را هم در قالب جواب
می‌دهند:

```python
handler404 = 'drf_parcel.views.not_found'
handler500 = 'drf_parcel.views.server_error'
```

---

## ۴. استفاده

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',  # the schema extra
}
```

هر خط مستقل است: handler به‌تنهایی فقط قالب خطا را می‌دهد و نه چیز دیگری.

```python
from drf_parcel.pagination import CursorPagination
from drf_parcel.responses import EnvelopeMixin, success_response

class ProductViewSet(EnvelopeMixin, ModelViewSet):
    page_size = 12
    client_page_size = True
    max_page_size = 48
    envelope_messages = {'create': _('The product was added.')}

class NotificationViewSet(EnvelopeMixin, ModelViewSet):
    pagination_class = CursorPagination
    ordering = '-created_at'

class TotalsView(EnvelopeMixin, APIView):
    def get(self, request):
        return success_response(data={'total': 12}, message=_('Totals.'))
```

`EnvelopeMixin` پاسخ را یک بار، در `finalize_response`، قالب‌بندی می‌کند،
پس هیچ اکشنی - `list`، `create`، یک `@action` سفارشی - لازم نیست یادش بماند.

---

## ۵. تنظیمات

یک دیکشنری. کلیدی که کتابخانه نمی‌شناسد هنگام start رد می‌شود، نه نادیده
گرفته - `PAGE_SZIE` اشتباهی که بی‌صدا نادیده گرفته شود، اندازه‌ی صفحه‌ای
است که هیچ‌وقت عوض نمی‌شود و کسی نمی‌فهمد چرا.

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
}
```

| کلید | پیش‌فرض | چه چیزی را تعیین می‌کند |
|---|---|---|
| `PAGE_SIZE` | `20` | اندازه‌ی صفحه وقتی view چیزی نگفته |
| `MAX_PAGE_SIZE` | `100` | سقف اندازه‌ای که کلاینت انتخاب می‌کند |
| `CLIENT_PAGE_SIZE` | `False` | آیا کلاینت می‌تواند اندازه را انتخاب کند |
| `PAGE_SIZE_QUERY_PARAM` | `'page_size'` | اسم پارامتری که با آن انتخاب می‌کند |
| `FIELD_ERRORS` | `'detailed'` | `'detailed'`: برای هر مشکل `{code, message}`؛ `'messages'`: فقط متن، شکل خود DRF |
| `FIELD_PATH_SEPARATOR` | `'.'` | مسیر فیلد تودرتو با چه چیزی وصل شود |
| `ERROR_CODES` | `{}` | تغییر اسم یک کد استاندارد: `{'validation_failed': 'validation_error'}` |
| `HANDLE_INTEGRITY_ERRORS` | `False` | بخش ۳.۵ |
| `RAISE_UNHANDLED_IN_DEBUG` | `True` | بخش ۳.۴ |
| `REPORTER` | `None` | مسیر تابعی که با هر 500 صدا زده می‌شود |

هر view تنظیمات صفحه‌بندی را با attributeهایی به همان اسم و با حروف کوچک
عوض می‌کند: `page_size`، `max_page_size`، `client_page_size`.

هنگام start بررسی می‌شود: `MAX_PAGE_SIZE` کمتر از `PAGE_SIZE`، `REPORTER`ی
که import نمی‌شود، کدی در `ERROR_CODES` که کتابخانه ندارد.

---

## ۶. اسکیما

با بخش اختیاری `schema` (`pip install 'drf-parcel[schema]'`)، سند OpenAPI
ساخته‌شده همان چیزی را می‌گوید که واقعاً منتقل می‌شود:

* هر پاسخ 2xx داخل قالب - `data` همان serializer است، و `pagination` همان
  نوعی که view استفاده می‌کند؛
* `page_size` فقط روی viewی مستند می‌شود که به کلاینت اجازه‌ی انتخاب بدهد؛
* قالب خطا به‌عنوان یک component مشترک، که همه‌ی عملیات‌ها به آن ارجاع
  می‌دهند، با `data.fields` روی آن‌هایی که ورودی را اعتبارسنجی می‌کنند.

فرانتی که تایپ‌هایش را از اسکیما می‌سازد آن وقت `response.data.id`
می‌نویسد، که همان چیزی است که می‌رسد.

---

## ۷. ترجمه

هر پیامی که کتابخانه می‌گوید برای ترجمه علامت خورده و به زبان درخواست گفته
می‌شود. کتابخانه فارسی را همراه خودش دارد؛ پروژه زبان دیگر را در کاتالوگ
خودش اضافه می‌کند.

---

## ۸. سؤال‌های باز

برای تصمیم مالک پروژه، پیش از مرحله‌ی ۱.

1. **`not_authenticated` و `authentication_failed`** اینجا دو کد هستند
   (اطلاعات ورود نیست، اطلاعات ورود اشتباه است). DayarDarman اولی را
   `authentication_required` می‌نامد؛ Elin و Hilacare برای هر دو یک کد
   می‌فرستند، `authentication_error`. کدام؟
2. **`validation_failed`** (DayarDarman) یا **`validation_error`** (Elin،
   Hilacare، Idehsaz)؟
3. **`IntegrityError`**: همین 409 `conflict`، یا 400 همان‌طور که Elin و
   Hilacare امروز جواب می‌دهند؟
4. **پیام‌های پیش‌فرض**: «Done.» برای هر موفقیت (DayarDarman)، یا یکی برای
   هر اکشن - «Created.»، «Deleted.»، «List retrieved.» (Elin، Hilacare)؟
5. **`handler404` و `handler500`** (۳.۷): در اولین نسخه، یا بعداً؟
