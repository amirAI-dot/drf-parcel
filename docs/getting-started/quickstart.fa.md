# شروع سریع

یک ViewSet در قالب، یک صفحه، و یک خطا - در پروژه‌ای که همان‌طور که صفحه‌ی قبل
گفت [نصب شده](installation.md).

## ۱. به view، mixin بدهید

```python
from rest_framework.viewsets import ModelViewSet

from drf_parcel.responses import EnvelopeMixin


class ProductViewSet(EnvelopeMixin, ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

`EnvelopeMixin` اول می‌آید، پیش از کلاس‌های DRF. پاسخ view را یک بار، در
`finalize_response`، در قالب می‌گذارد، پس هیچ اکشنی - `list`، `create`، یک
`@action` خودتان - لازم نیست یادش بماند.

## ۲. بپرسید

=== "یک محصول"

    ```bash
    curl http://127.0.0.1:8000/api/products/1/
    ```

    ```json
    {"success": true, "status_code": 200, "message": "Done.",
     "data": {"id": 1, "name": "Ring", "price": "120.00", "stock": 4}}
    ```

=== "یک صفحه"

    ```bash
    curl 'http://127.0.0.1:8000/api/products/?page=2'
    ```

    ```json
    {"success": true, "status_code": 200, "message": "Done.",
     "data": [{"id": 21, "name": "Earring 18", "price": "40.00", "stock": 10}, ...],
     "pagination": {"type": "page", "count": 28, "page": 2, "pages": 3, "page_size": 10,
                    "has_next": true, "has_previous": true}}
    ```

=== "حذف"

    ```bash
    curl -X DELETE http://127.0.0.1:8000/api/products/3/
    ```

    ```json
    {"success": true, "status_code": 200, "message": "Deleted.", "data": {}}
    ```

    200 همراه با قالب، نه 204 - پاسخ 204 بدنه ندارد، پس کلاینت چیزی برای
    خواندن نداشت.

=== "یک اشتباه"

    ```bash
    curl -X POST -H 'Content-Type: application/json' -d '{"price": "x"}' \
         http://127.0.0.1:8000/api/products/
    ```

    ```json
    {"success": false, "status_code": 400, "message": "This field is required.",
     "error_code": "validation_error",
     "data": {"fields": {
       "name": [{"code": "required", "message": "This field is required."}],
       "price": [{"code": "invalid", "message": "A valid number is required."}]}}}
    ```

## ۳. خطای خودتان را raise کنید

```python
from django.utils.translation import gettext_lazy as _
from drf_parcel.exceptions import DomainError


class OutOfStockError(DomainError):
    status_code = 409
    default_code = 'out_of_stock'
    default_detail = _('There is not enough of this product in stock.')


raise OutOfStockError(data={'available': product.stock})
```

```json
{"success": false, "status_code": 409, "message": "There is not enough of this product in stock.",
 "data": {"available": 0}, "error_code": "out_of_stock"}
```

`DomainError` همان `APIException` خود DRF است با `data` اضافه، پس از یک
سرویس، یک تسک یا یک command به یک شکل raise می‌شود.

## قدم بعد

* [آموزش](../tutorial/index.md) فروشگاه نمونه را بخش به بخش می‌سازد.
* [به کار گرفتن در یک پروژه‌ی موجود](../how-to/adopt.md) - پروژه‌ای که از قبل
  قالب خودش را دارد.
* [قرارداد](../contract.md) همه‌ی شکل‌ها و همه‌ی کدهای خطا را دارد.
