# drf-parcel

یک شکل پاسخ برای API ساخته‌شده با Django REST framework - برای پاسخ موفق،
صفحه و خطا یکسان - و اسکیمایی که دقیقاً همان شکل را می‌گوید.

```json
{"success": true,  "status_code": 200, "message": "Done.", "data": {"id": 7, "name": "Ring"}}
```

```json
{"success": false, "status_code": 409, "message": "There is not enough of this product in stock.",
 "data": {"available": 0}, "error_code": "out_of_stock"}
```

کلاینت فقط یک شکل را می‌خواند و هیچ پاسخی را جداگانه مدیریت نمی‌کند: جواب
زیر `data` است، انسان `message` را می‌خواند، و کد بر اساس `error_code` تصمیم
می‌گیرد - هرگز بر اساس پیام، که ترجمه می‌شود.

<div class="grid cards" markdown>

- **همه‌ی پاسخ‌ها در یک قالب** - ViewSet، `APIView` ساده، `@action` سفارشی،
  صفحه و خطا یکسان، با پیامی که می‌گوید چه شد.
- **صفحه‌بندی شماره‌ای یا با cursor**، که هر view خودش انتخاب می‌کند؛ کلاینت
  جایی که شما اجازه بدهید تعداد هر صفحه را انتخاب می‌کند، و هرگز بیشتر از
  سقف نمی‌گیرد.
- **همه‌ی خطاها در همان قالب** - مشکل هر فیلد با کدش، خطاهای DRF و Django با
  کد استاندارد، خطاهای خودتان با `data`ای که کلاینت بر اساسش کاری می‌کند، و
  باگی که هرگز اسرارش را نمی‌گوید.
- **اسکیما همان چیزی را می‌گوید که می‌رسد** - drf-spectacular خود قالب را
  مستند می‌کند، نه فقط داخلش را، پس کلاینت ساخته‌شده `response.data.id`
  می‌خواند.

</div>

`APIException`های فعلی شما بدون تغییر کار می‌کنند. هر بخش جدا قابل استفاده
است، پس پروژه آن را view به view به کار می‌گیرد. هر جمله به انگلیسی و فارسی
است.

## نصب

```bash
pip install 'drf-parcel[schema]'
```

```python
INSTALLED_APPS = [..., 'rest_framework', 'drf_parcel']

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
}
```

## قدم بعد

| | |
|---|---|
| [شروع سریع](getting-started/quickstart.md) | اولین view در قالب، در پنج دقیقه |
| [آموزش](tutorial/index.md) | فروشگاه نمونه، بخش به بخش ساخته می‌شود |
| [راهنماهای کاربردی](how-to/index.md) | یک سؤال که پروژه با آن روبه‌رو می‌شود، در چند قدم - اول از همه به کار گرفتن در یک پروژه‌ی موجود |
| [قرارداد](contract.md) | هر شکل، هر کد خطا، هر تنظیم - آنچه کد قول می‌دهد |
| [مرجع](reference/index.md) | تنظیمات، کدهای خطا، بررسی‌های هنگام start، و API پایتون |
| [توضیح‌ها](explanation/index.md) | چرا این‌طور ساخته شده، و چه فرقی با بقیه دارد |
| [پرسش‌ها](faq.md) | آنچه اول از همه پرسیده می‌شود |
| [فروشگاه نمونه](https://github.com/amirAI-dot/drf-parcel/tree/main/example) | پروژه‌ای که همه‌ی آن را به کار می‌برد، برای اجرا |

Python 3.11 تا 3.14؛ Django 5.2، 6.0 و 6.1؛ Django REST framework 3.16 و
بالاتر؛ drf-spectacular 0.28 و بالاتر، برای اسکیما.
