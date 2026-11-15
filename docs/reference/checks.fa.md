# بررسی‌های هنگام start

`manage.py check` - و `runserver` و `migrate` - تنظیمی را که کار نمی‌کند گزارش
می‌دهد، پیش از اینکه کلاینتی به آن برخورد کند.

| شناسه | چه اشکالی | چه باید کرد |
|---|---|---|
| `drf_parcel.E001` | `DRF_PARCEL` دیکشنری نیست، کلیدی دارد که کتابخانه نمی‌شناسد، یا `MESSAGES` چنین کلیدی دارد | پیام کلید را نام می‌برد؛ املایش را درست کنید |
| `drf_parcel.E002` | تعداد صفحه یا `MAX_PAGE_SIZE` عدد صحیح بالای صفر نیست | تعداد صفحه `DRF_PARCEL['PAGE_SIZE']` است، و اگر نباشد `REST_FRAMEWORK['PAGE_SIZE']` |
| `drf_parcel.E003` | `MAX_PAGE_SIZE` کمتر از تعداد صفحه است | سقف را بالا ببرید - اغلب بعد از به کار گرفتن کتابخانه با یک `REST_FRAMEWORK['PAGE_SIZE']` بزرگ |
| `drf_parcel.E004` | `CLIENT_PAGE_SIZE` نه `True` است نه `False` | |
| `drf_parcel.E005` | `PAGE_SIZE_QUERY_PARAM` اسم یک پارامتر نیست | |
| `drf_parcel.E006` | `FIELD_ERRORS` نه `'detailed'` است نه `'messages'` | |
| `drf_parcel.E007` | `FIELD_PATH_SEPARATOR` خالی است | |
| `drf_parcel.E008` | `ERROR_CODES` دیکشنری نیست، کدی را تغییر اسم می‌دهد که کتابخانه نمی‌فرستد، یا کدی را به هیچ تغییر می‌دهد | hint کدهایی را که می‌فرستد فهرست می‌کند |
| `drf_parcel.E009` | `HANDLE_INTEGRITY_ERRORS` یا `RAISE_UNHANDLED_IN_DEBUG` نه `True` است نه `False` | |
| `drf_parcel.E010` | `REPORTER` مسیر یک تابع نیست | |
| `drf_parcel.E011` | `PAGE_SIZE_QUERY_PARAM` برابر `page` یا `cursor` است، که خود paginator آن را می‌خواند | اسم دیگری انتخاب کنید |

بررسی‌ای که شکست بخورد جلوی جواب دادن به یک خطا را نمی‌گیرد: تغییر اسمی که کار
نمی‌کند توسط handler نادیده گرفته می‌شود، و خطا با کد استاندارد جواب داده
می‌شود.
