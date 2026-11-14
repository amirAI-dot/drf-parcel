# جایگزین‌ها

چند کتابخانه بخشی از این کار را می‌کنند. هیچ‌کدام، تا زمان نوشتن این صفحه،
همه‌اش را نمی‌کند - هر دو نوع صفحه در یک قالب، تعداد صفحه‌ای که کلاینت زیر
سقف انتخاب می‌کند، همه‌ی خطاها به شکل پاسخ موفق، و اسکیمایی که قالب را بگوید.

| کتابخانه | چه می‌کند | چه فرقی دارد |
|---|---|---|
| [drf-standardized-errors](https://pypi.org/project/drf-standardized-errors/) | فقط خطاها، به شکل `{type, errors: [...]}`؛ یکپارچگی OpenAPI جاافتاده | خطاهایش شکلی متفاوت از پاسخ‌های موفق دارند، که دست نمی‌زند |
| [drf-exceptions-hog](https://pypi.org/project/drf-exceptions-hog/) | فقط خطاها، `{type, code, detail, attr}` | فقط خطاها؛ دیگر نگهداری نمی‌شود |
| [drf-simple-api-errors](https://pypi.org/project/drf-simple-api-errors/) | فقط خطاها، بر پایه‌ی RFC 7807 | فقط خطاها |
| [drf-standardized-response](https://pypi.org/project/drf-standardized-response/) | پاسخ‌های موفق، با یک renderer؛ پشتیبانی از drf-spectacular | renderer باید حدس بزند چه چیزی از قبل در قالب است؛ صفحه‌ها به‌طور پیش‌فرض در قالب نیستند؛ بدون خطا |
| [dj-response-formatter](https://pypi.org/project/dj-response-formatter/) | پاسخ موفق و خطا، با یک renderer | صفحه را از روی کلیدها تشخیص می‌دهد، پس فیلدی به اسم `count` صفحه حساب می‌شود؛ بدون cursor؛ بدون اسکیما |
| [api-response-shaper](https://pypi.org/project/api-response-shaper/) | پاسخ موفق و خطا، با یک middleware | JSON رندرشده را دوباره باز می‌کند؛ بدون cursor؛ بدون اسکیما |
| [api-response-toolkit](https://pypi.org/project/api-response-toolkit/) | تابع‌های کمکی و یک handler | بدون cursor؛ بدون اسکیما |

## چرا mixin، و نه renderer یا middleware

renderer بعد از view اجرا می‌شود، روی داده‌ای که خودش نساخته، پس باید حدس بزند
که داده از قبل قالب است یا نه، و اسکیما هرگز نمی‌فهمد که چیزی در قالب گذاشته
می‌شود. middleware حتی دیرتر است، و بایت‌های رندرشده را دوباره می‌خواند.
mixin در `finalize_response` در قالب می‌گذارد، جایی که view شناخته شده است:
اکشنش، پیامش، اینکه بیرون مانده یا نه - و اسکیما همان سؤال را از همان view
می‌پرسد.

## و جواب خود drf-spectacular

پرسش‌های متداول drf-spectacular به «پاسخ‌هایم را چطور در قالب بگذارم؟» با یک
تابع کمکی جواب می‌دهد که هر پروژه خودش می‌نویسد و روی هر عملیات اعمال می‌کند.
drf-parcel همان تابع است، یک بار نوشته شده - برای هر view، هر صفحه و هر خطا.
