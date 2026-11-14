# انتخاب نوع صفحه‌بندی یک لیست

## شماره‌ای یا cursor، برای هر view

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
}
```

```python
from drf_parcel.pagination import CursorPagination


class NotificationViewSet(EnvelopeMixin, ModelViewSet):
    pagination_class = CursorPagination
    ordering = '-created_at'
```

| انتخاب کنید | وقتی |
|---|---|
| `PageNumberPagination` | لیستی که انسان صفحه به صفحه ورق می‌زند، با تعداد کل و صفحه‌های شماره‌دار |
| `CursorPagination` | فیدی که پشت سر هم خوانده می‌شود - جدولی بزرگ‌تر از آن که در هر درخواست شمرده شود، یا ردیف‌هایی که حین خواندن اضافه می‌شوند |

cursor ترتیبی لازم دارد که عوض نشود و یکتا یا تقریباً یکتا باشد - زمان ساخت،
یک id. آن را روی view (`ordering`)، روی زیرکلاس paginator، یا با یک
`OrderingFilter` نام ببرید، که همان‌طور که DRF تصمیم می‌گیرد تصمیم می‌گیرد.

## تعداد

تعداد اول از view خوانده می‌شود، بعد از paginator، بعد `DRF_PARCEL['PAGE_SIZE']`،
بعد `REST_FRAMEWORK['PAGE_SIZE']` خود DRF، و در آخر ۲۰:

```python
class ProductViewSet(EnvelopeMixin, ModelViewSet):
    page_size = 12
```

## بگذارید کلاینت انتخاب کند

```python
class ProductViewSet(EnvelopeMixin, ModelViewSet):
    page_size = 12
    client_page_size = True      # ?page_size= is read
    max_page_size = 48           # and never exceeded
```

یا برای همه‌ی viewها، در `DRF_PARCEL`: `CLIENT_PAGE_SIZE`، `MAX_PAGE_SIZE` و
`PAGE_SIZE_QUERY_PARAM` (به‌طور پیش‌فرض `page_size`). عدد بالای سقف همان سقف
است؛ هیچ، صفر، عدد منفی یا یک کلمه همان تعداد پیش‌فرض است - هرگز خطا نیست.

!!! warning "همیشه یک سقف"

    بدون سقف، `?page_size=1000000` یعنی خواندن کل جدول، که برای هر کسی باز
    است. کتابخانه راهی برای خاموش کردن سقف ندارد.

## بدون صفحه

```python
class CountryViewSet(EnvelopeMixin, ModelViewSet):
    pagination_class = None      # a short list read whole, on purpose
```

لیست زیر `data` است، و کلید `pagination`ی نیست.
