# قرارداد

> **وضعیت: تصمیم گرفته شده.** هر شکلی که از سرور بیرون می‌رود، هر کد خطا،
> و هر تنظیم. کد از این سند پیروی می‌کند؛ هر تغییری در آنچه به کلاینت
> می‌رسد، اول اینجا تغییر می‌کند. سؤال‌هایی که بر اساسشان تصمیم گرفته شد،
> و تصمیم هر کدام، در انتها آمده‌اند.
>
> English: [`contract.md`](https://github.com/amirAI-dot/drf-parcel/blob/main/docs/contract.md).

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

### پیامی که پاسخ موفق می‌گوید

وقتی کسی پیامی ننوشته، از روی خود درخواست تعیین می‌شود - پس ViewSet،
`APIView` ساده و `@action` سفارشی همه چیز معقولی می‌گویند، و هیچ‌کدام لازم
نیست چیزی یادشان بماند:

| درخواست | پیام | کلیدش در `MESSAGES` |
|---|---|---|
| پاسخ `201` | «Created.» - ساخته شد. | `created` |
| `PUT` یا `PATCH` | «Saved.» - ذخیره شد. | `saved` |
| `DELETE` | «Deleted.» - حذف شد. | `deleted` |
| هر چیز دیگر | «Done.» - انجام شد. | `done` |

کلاینت بیشتر پیام نوشتن را نشان می‌دهد - یک toast که می‌گوید «ذخیره شد» - و
به‌ندرت پیام خواندن را. هر کدام در سه سطح عوض می‌شود، و نزدیک‌ترین برنده است:

```python
return success_response(data=order, message=_('The order was paid.'))   # one answer

class ProductViewSet(EnvelopeMixin, ModelViewSet):                        # one view
    envelope_messages = {'create': _('The product was added.')}

DRF_PARCEL = {'MESSAGES': {'created': _('Saved successfully.')}}          # the project
```

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
به جای آن **200** همراه با قالب برمی‌گرداند - و همین‌طور هر 204ی که
کتابخانه جواب می‌دهد، چه 204 بدون قالب یک view و چه
`success_response(status_code=204)`:

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
  health check که فراخواننده‌اش شکل خودش را انتظار دارد - صفحه‌هایش هم، که
  همان `count`، `next`، `previous` و `results` خود DRF هستند؛
* پاسخی که از قبل در قالب است - `success_response` یکی برمی‌گرداند، و دو
  بار قالب‌بندی نمی‌شود؛
* پاسخ `205 Reset Content` - به کلاینت می‌گوید فرمش را خالی کند، و طبق تعریف
  بدنه ندارد، پس همان‌طور که view داده می‌ماند. `success_response(status_code=205)`
  رد می‌شود: بدنه‌ای نیست که قالب در آن گذاشته شود.

پاسخ `OPTIONS` - توصیفی که DRF از view می‌دهد - مثل هر پاسخ موفق دیگری است، و
در قالب است.

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

کلاینت همان چیزی را که گرفته پس می‌فرستد و هرگز خودش یکی نمی‌سازد. `count`
و `page` ندارد - نشمردن، روی جدولی که بزرگ‌تر از آن است که در هر درخواست
شمرده شود، کل فایده‌ی cursor است. `has_next` در هر دو نوع هست، پس دکمه‌ی
«بیشتر» با هر دو کار می‌کند.

**cursor امضا شده است**، با `SECRET_KEY` پروژه، و ترتیبی را که برایش ساخته
شده با خودش دارد. cursorی که دستی عوض شده، cursorی که برای ترتیب دیگری ساخته
شده - لیستی که با `?ordering=` دوباره مرتب شده - یا cursorی که با کلید دیگری
امضا شده، پیش از اینکه از دیتابیس چیزی پرسیده شود رد می‌شود: **400**
(`invalid_cursor`). cursorی هم که سرور اصلاً نتواند بخواند همین‌طور. عوض کردن
کلید با `SECRET_KEY_FALLBACKS` خود Django، cursorهایی را که داده شده‌اند نگه
می‌دارد.

**cursor امضا شده است، نه محرمانه.** می‌شود آن را رمزگشایی کرد، و مقدار ستونی
را که فید بر اساسش مرتب شده، برای ردیفی که صفحه با آن تمام می‌شود، در خود
دارد. فید را فقط بر اساس مقداری مرتب کنید که خواننده‌هایش اجازه‌ی دیدنش را
دارند - زمان ساخت، یک id.

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
  "error_code": "validation_error",
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
| 400 | `validation_error` | serializer، یا `ValidationError` خود Django | `fields` |
| 400 | `parse_error` | بدنه‌ای که JSON معتبر نیست | `{}` |
| 400 | `invalid_cursor` | cursorی که سرور نمی‌تواند بخواند | `{}` |
| 401 | `not_authenticated` | اطلاعات ورود فرستاده نشده - و 403، همان‌طور که DRF جواب می‌دهد، وقتی اولین کلاس احراز هویت view هدر `WWW-Authenticate` نمی‌فرستد (احراز هویت با session) | `{}` |
| 401 | `authentication_failed` | اطلاعات ورود اشتباه یا منقضی | `{}` |
| 403 | `permission_denied` | `PermissionDenied` در DRF یا Django - با جمله‌ای که با آن raise شده، اگر داشته باشد | `{}` |
| 404 | `not_found` | `NotFound`، یا `Http404` خود Django | `{}` |
| 405 | `method_not_allowed` | متدی که view ندارد | `{}` |
| 406 | `not_acceptable` | `Accept`ی که کسی جوابش را ندارد | `{}` |
| 409 | `already_exists` | `IntegrityError` از نوع unique، وقتی روشن باشد (۳.۵) | `{}` |
| 409 | `conflict` | `IntegrityError` از نوع foreign key، وقتی روشن باشد (۳.۵) | `{}` |
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
    default_code = 'province_in_use'
    default_detail = _('This province has branches and cannot be deleted.')

raise ProvinceInUse(data={'branches': 3})
raise ProvinceInUse(_('Move its 3 branches first.'), data={'branches': 3})
```

**`DomainError` همان `APIException` خود DRF است**، با یک چیز اضافه: `data`.
اسم‌هایش اسم‌های خود DRF هستند - `status_code`، `default_code` (که به‌عنوان
`error_code` فرستاده می‌شود)، `default_detail` (که به‌عنوان `message`
فرستاده می‌شود) - پس چیز تازه‌ای برای یاد گرفتن نیست، و یک نوع خطا داریم، نه
دو نوع.

```python
class DomainError(APIException):
    status_code = 400
    default_code = 'error'
    default_detail = _('The request could not be completed.')

    def __init__(self, detail=None, code=None, *, data=None):
        super().__init__(detail, code)
        self.data = data or {}
```

* **بدون handler این کتابخانه هم کار می‌کند.** پروژه‌ای که mixin را نصب
  کرده و handler خود DRF را نگه داشته، باز هم کد وضعیت درست، `set_rollback`
  و یک جواب معقول می‌گیرد - نه 500.
* **یک exception معمولی هم هست.** سرویس آن را raise می‌کند، و تسک Celery یا
  management command آن را مثل هر exception دیگری catch می‌کند.
* **rollback کار handler است، نه کار کلاس.** handler خود DRF تابع
  `set_rollback` را صدا می‌زند؛ این کتابخانه آن handler را جایگزین می‌کند،
  پس handler خودش آن را صدا می‌زند، در همه‌ی مسیرها (۳.۶).
* **پیام همان لحظه‌ی raise شدن به متن تبدیل می‌شود**، همان‌طور که DRF
  می‌کند - داخل یک درخواست، به زبان همان درخواست. خطایی که بیرون از درخواست
  raise شود به زبان پیش‌فرض است.

کتابخانه خطاهای رایج را همراه خودش دارد - `InvalidInputError`،
`InvalidCursorError`، `AuthenticationFailedError`، `PermissionDeniedError`، `NotFoundError`،
`ConflictError`، `RateLimitedError`، `ServiceUnavailableError`.

**خطاهای فعلی پروژه همچنان کار می‌کنند.** هر زیرکلاس `APIException` در DRF،
چه از `DomainError` باشد چه نه، بدون هیچ تغییری در قالب جواب می‌دهد:
`status_code` خودش، `default_code` خودش به‌عنوان `error_code`، `detail` خودش
به‌عنوان `message`، و `data` اگر داشته باشد.

### ۳.۴ چیزی که هرگز گفته نمی‌شود

خطای پیش‌بینی‌نشده با **500** و یک جمله‌ی عمومی جواب داده می‌شود. متن آن
هرگز از سرور بیرون نمی‌رود - ممکن است یک کوئری، مسیر یک فایل یا اسم یک نفر
در آن باشد. یک 404 یا یک شماره‌ی تلفن اشتباه اصلاً به‌عنوان error لاگ نمی‌شود.

**هر 5xxی که جواب داده می‌شود به‌عنوان error لاگ و گزارش می‌شود** - خطای
پیش‌بینی‌نشده، و خطای طراحی‌شده هم: `APIException`ی که با وضعیت 500 یا
بالاتر raise شده، `ServiceUnavailableError`. یک 5xx طراحی‌شده پیامی را می‌گوید
که با آن raise شده، پس آن پیام هرگز نباید متن یک exception باشد.

* با `DEBUG = True` به جای جواب، خطا بالا می‌رود تا صفحه‌ی خطای Django
  traceback را نشان بدهد (`RAISE_UNHANDLED_IN_DEBUG`).
* `REPORTER` تابعی است که با هر 5xx صدا زده می‌شود - برای Sentry یا هر
  ابزار مشابه.

### ۳.۵ یکپارچگی دیتابیس

به‌طور پیش‌فرض خاموش. قیدی که دیتابیس رد می‌کند معمولاً زودتر، در serializer
یا سرویس، گرفته شده است؛ این یک تور ایمنی است که با `HANDLE_INTEGRITY_ERRORS`
روشن می‌شود.

نوع قید از کدی خوانده می‌شود که درایور دیتابیس گزارش می‌دهد - هرگز از متن
خطا، که با دیتابیس، نسخه و زبانش عوض می‌شود:

| قید | PostgreSQL `sqlstate` | SQLite `sqlite_errorcode` | MySQL `errno` |
|---|---|---|---|
| unique | `23505` | `2067`، `1555` | `1062` |
| foreign key | `23503` | `787` | `1451`، `1452` |
| not null | `23502` | `1299` | `1048` |
| check | `23514` | `275` | `3819` |

| قید | جواب | چرا |
|---|---|---|
| unique | 409 `already_exists` | دو درخواست همزمان: ورودی درست بود، و بین بررسی و نوشتن، ردیف گرفته شد |
| foreign key | 409 `conflict` | ردیفی که به آن اشاره شده در همین فاصله حذف یا عوض شده |
| not null | 500 `internal_error` | قانونی که serializer باید می‌گفت جا افتاده - باگ است، و کاربر نمی‌تواند درستش کند |
| check | 500 `internal_error` | همان |
| کدی که شناخته نیست | 500 `internal_error` | ناشناخته یعنی رد |

500 اینجا مثل هر 500 دیگری است (۳.۴): با traceback لاگ می‌شود، گزارش می‌شود،
و در `DEBUG` بالا می‌رود - باگی پیدا شده است. پیام همیشه یک جمله‌ی عمومی و
ترجمه‌شده است: نه متن دیتابیس، نه اسم قید و نه اسم ستون از سرور بیرون
نمی‌رود. اینکه کدام فیلد تکراری است را serializer باید بگوید.

### ۳.۶ تراکنش

هر خطایی که جواب داده می‌شود، تراکنش درخواست را برای rollback علامت می‌زند
(`set_rollback`)، تا پروژه‌ای که `ATOMIC_REQUESTS` دارد هرگز نیمی از یک
نوشتن را پشت یک خطا نگه ندارد.

### ۳.۷ بیرون از DRF { #outside-drf }

کتابخانه به پاسخی که DRF می‌دهد شکل می‌دهد، و نه به چیز دیگری. درخواستی که
هیچ‌وقت به یک view در DRF نمی‌رسد - آدرسی که با هیچ URLی جور نیست، خطایی در
یک middleware پیش از view - را Django جواب می‌دهد، با `handler404` و
`handler500` خود پروژه، و بیرون از این کتابخانه است.

این عمدی است: آن handlerها مال کل پروژه‌اند - پنل ادمین و صفحه‌های وب هم -
نه مال API، و کتابخانه‌ای برای DRF به آن‌ها دست نمی‌زند.
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
    'MESSAGES': {},
}
```

| کلید | پیش‌فرض | چه چیزی را تعیین می‌کند |
|---|---|---|
| `PAGE_SIZE` | `20` | اندازه‌ی صفحه وقتی view چیزی نگفته. اگر نوشته نشده باشد، `REST_FRAMEWORK['PAGE_SIZE']` خود DRF خوانده می‌شود اگر تنظیم شده باشد - پروژه‌ای که آن را آنجا گذاشته اندازه‌اش را نگه می‌دارد - و فقط بعد از آن `20` |
| `MAX_PAGE_SIZE` | `100` | سقف اندازه‌ای که کلاینت انتخاب می‌کند |
| `CLIENT_PAGE_SIZE` | `False` | آیا کلاینت می‌تواند اندازه را انتخاب کند |
| `PAGE_SIZE_QUERY_PARAM` | `'page_size'` | اسم پارامتری که با آن انتخاب می‌کند |
| `FIELD_ERRORS` | `'detailed'` | `'detailed'`: برای هر مشکل `{code, message}`؛ `'messages'`: فقط متن، شکل خود DRF |
| `FIELD_PATH_SEPARATOR` | `'.'` | مسیر فیلد تودرتو با چه چیزی وصل شود |
| `ERROR_CODES` | `{}` | تغییر اسم یک کد استاندارد: `{'validation_error': 'validation_failed'}` |
| `HANDLE_INTEGRITY_ERRORS` | `False` | بخش ۳.۵ |
| `RAISE_UNHANDLED_IN_DEBUG` | `True` | بخش ۳.۴ |
| `REPORTER` | `None` | مسیر تابعی که با هر 500 صدا زده می‌شود |
| `MESSAGES` | `{}` | عوض کردن پیام پیش‌فرض موفقیت، با کلیدش: `created`، `saved`، `deleted`، `done` (۱) |

هر view تنظیمات صفحه‌بندی را با attributeهایی به همان اسم و با حروف کوچک
عوض می‌کند: `page_size`، `max_page_size`، `client_page_size`.

هنگام start بررسی می‌شود: `MAX_PAGE_SIZE` کمتر از `PAGE_SIZE`، `REPORTER`ی
که import نمی‌شود، کدی در `ERROR_CODES` که کتابخانه ندارد.

---

## ۶. اسکیما

با بخش اختیاری `schema` (`pip install 'drf-parcel[schema]'`)، سند OpenAPI
ساخته‌شده همان چیزی را می‌گوید که واقعاً منتقل می‌شود:

* هر پاسخ 2xx یک view با `EnvelopeMixin` داخل قالب - `data` همان serializer
  است، و حذف همان 200ی است که واقعاً جواب می‌دهد؛
* لیست صفحه‌بندی‌شده به‌عنوان قالب خودش، با `pagination` از همان نوعی که view
  استفاده می‌کند، با اسمی که نوعش را می‌گوید - `ItemPage`، `ItemCursorPage` -
  تا هیچ‌وقت با `PaginatedItemList` خود DRF اشتباه گرفته نشود؛
* `page_size` فقط روی viewی مستند می‌شود که به کلاینت اجازه‌ی انتخاب بدهد،
  با سقفش به‌عنوان maximum؛
* قالب خطا به‌عنوان یک component مشترک، `ErrorEnvelope`، که پاسخ `default`
  همه‌ی عملیات‌هاست، و `ValidationErrorEnvelope`، با `data.fields`، که پاسخ 400
  هر عملیاتی است که بدنه می‌گیرد - خطایی که خود view مستند کرده حفظ می‌شود.
  فقط تا وقتی که `EXCEPTION_HANDLER` پروژه مال این کتابخانه است - یا handler
  خود پروژه که آن را صدا می‌زند و با `functools.wraps(exception_handler)` این را
  می‌گوید: در غیر این صورت خطاها شکل خود DRF را دارند، و اسکیما شکل دیگری را
  قول نمی‌دهد.

viewی که mixin ندارد همان‌طور که جواب می‌دهد مستند می‌شود - پاسخ‌های موفقش
بدون قالب، و صفحه‌هایش در قالب، همان‌طور که paginatorها جواب می‌دهند. viewی که
دستی با `success_response` جواب می‌دهد در عمل در قالب است و در اسکیما نیست:
به آن mixin بدهید.

نصب با `'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema'`، یا با
افزودن `ParcelSchemaMixin` به `AutoSchema` خود پروژه.

فرانتی که تایپ‌هایش را از اسکیما می‌سازد آن وقت `response.data.id`
می‌نویسد، که همان چیزی است که می‌رسد.

---

## ۷. ترجمه

هر پیامی که کتابخانه می‌گوید برای ترجمه علامت خورده و به زبان درخواست گفته
می‌شود. کتابخانه فارسی را همراه خودش دارد؛ پروژه زبان دیگر را در کاتالوگ
خودش اضافه می‌کند.

---

## ۸. تصمیم‌ها

آنچه پیش از مرحله‌ی ۱ پرسیده شد، و تصمیم مالک پروژه.

1. ~~یک کد برای خطای ورود یا دو کد؟~~ **تصمیم: دو کد**، همان کدهای خود
   DRF - `not_authenticated` (فرستاده نشده) و `authentication_failed`
   (اشتباه یا منقضی). کلاینت روی دومی نشست را تمدید می‌کند و فقط روی اولی
   کاربر را به صفحه‌ی ورود می‌برد.
2. ~~`validation_failed` یا `validation_error`؟~~ **تصمیم:
   `validation_error`** - همان چیزی که کلاینت سه پروژه از چهار پروژه همین
   الان می‌خواند، و کتابخانه‌های مشابه هم همین را می‌گویند. کد خود DRF،
   `invalid`، کد فیلدها هم هست، پس استفاده نمی‌شود. اسم کلاس کتابخانه
   `InvalidInputError` است.
3. ~~`IntegrityError`: 409 یا 400؟~~ **تصمیم: بر اساس نوع قید**، که از کد
   درایور خوانده می‌شود (۳.۵).
4. ~~پیام پیش‌فرض موفقیت؟~~ **تصمیم: از روی خود درخواست** - «Created.» روی
   201، «Saved.» روی `PUT` و `PATCH`، «Deleted.» روی `DELETE`، و «Done.» در
   بقیه - که برای یک پاسخ، یک view، یا کل پروژه با `MESSAGES` عوض می‌شود (۱).
5. ~~`handler404` و `handler500`: در اولین نسخه، یا بعداً؟~~ **تصمیم: هیچ‌کدام.**
   چیزی که هیچ‌وقت به DRF نمی‌رسد کار این کتابخانه نیست (۳.۷).

تصمیم‌هایی که بعد از 0.1.0، بر اساس یافته‌های یک بررسی امنیتی، گرفته شد:

6. **cursor امضا می‌شود** (۲): cursorی که دستکاری شده، یا برای ترتیب دیگری
   ساخته شده، پیش از اینکه از دیتابیس چیزی پرسیده شود رد می‌شود، پس یک باگ
   واقعی حین خواندن فید همچنان باگ می‌ماند - لاگ و گزارش می‌شود. امضا، نه
   رمزگذاری: گفته شده که cursor قابل رمزگشایی است.
7. **هر 5xx لاگ و گزارش می‌شود**، خطای طراحی‌شده هم (۳.۴).
8. **پاسخ 205 همان‌طور که view داده می‌ماند** (۱): بدنه‌ای ندارد که در قالب
   برود.
9. **`OPTIONS` در قالب است** (۱)، مثل هر پاسخ موفق دیگری.
10. `page_size` خود view سقف ندارد: سقف روی چیزی است که کلاینت می‌خواهد، و
    تعداد خود view را برنامه‌نویسش تعیین می‌کند. کلید یک `DictField` که جداکننده‌ی
    مسیر را در خود دارد، مسیر مبهمی در `data.fields` می‌سازد؛
    `FIELD_PATH_SEPARATOR` جداکننده را عوض می‌کند.
