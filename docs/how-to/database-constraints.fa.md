# جواب دادن به قید دیتابیس

دو نفر در یک لحظه یک اسم را می‌گیرند. هر دو از بررسی یکتایی serializer رد
می‌شوند، و دیتابیس دومی را رد می‌کند: یک `IntegrityError`، که 500 است مگر
اینکه پروژه تور ایمنی را روشن کند:

```python
DRF_PARCEL = {'HANDLE_INTEGRITY_ERRORS': True}
```

| قید | جواب |
|---|---|
| unique | 409 `already_exists` - ورودی درست بود، و در این فاصله ردیف گرفته شد |
| foreign key | 409 `conflict` - ردیفی که به آن اشاره شده در این فاصله عوض شد |
| not null، check | 500 - قانونی که serializer باید می‌گفت جا افتاده |

نوع قید از کدی خوانده می‌شود که درایور دیتابیس گزارش می‌دهد - PostgreSQL،
SQLite، MySQL - هرگز از متن خطا، و نه متن و نه اسم یک ستون از سرور بیرون
نمی‌رود. اینکه کدام فیلد تکراری است را serializer باید بگوید: تور ایمنی برای
رقابتی است که serializer نمی‌تواند ببیند.

!!! note "PostgreSQL، کلید خارجی و `ATOMIC_REQUESTS`"

    Django کلید خارجی را روی PostgreSQL *deferred* می‌سازد: دیتابیس آن را هنگام
    commit تراکنش بررسی می‌کند، نه هنگام نوشتن ردیف. با `ATOMIC_REQUESTS` این
    لحظه بعد از پاسخ view است، پس خطا هرگز به DRF نمی‌رسد - 500 خود Django
    است، [بیرون از کتابخانه](../contract.md#outside-drf). پاسخ 409 `conflict`
    جایی داده می‌شود که نوشتن درون خود view commit شود: بدون `ATOMIC_REQUESTS`،
    یا در یک بلوک `transaction.atomic()` از خود view یا service.
