# Quickstart

A viewset in the envelope, a page, and a failure - in a project
[installed](installation.md) as the last page says.

## 1. Give the view the mixin

```python
from rest_framework.viewsets import ModelViewSet

from drf_parcel.responses import EnvelopeMixin


class ProductViewSet(EnvelopeMixin, ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

`EnvelopeMixin` comes first, before DRF's classes. It wraps what the view
answers once, in `finalize_response`, so no action - `list`, `create`, an
`@action` of your own - has to remember.

## 2. Ask it

=== "One product"

    ```bash
    curl http://127.0.0.1:8000/api/products/1/
    ```

    ```json
    {"success": true, "status_code": 200, "message": "Done.",
     "data": {"id": 1, "name": "Ring", "price": "120.00", "stock": 4}}
    ```

=== "A page"

    ```bash
    curl 'http://127.0.0.1:8000/api/products/?page=2'
    ```

    ```json
    {"success": true, "status_code": 200, "message": "Done.",
     "data": [{"id": 21, "name": "Earring 18", "price": "40.00", "stock": 10}, ...],
     "pagination": {"type": "page", "count": 28, "page": 2, "pages": 3, "page_size": 10,
                    "has_next": true, "has_previous": true}}
    ```

=== "A delete"

    ```bash
    curl -X DELETE http://127.0.0.1:8000/api/products/3/
    ```

    ```json
    {"success": true, "status_code": 200, "message": "Deleted.", "data": {}}
    ```

    A 200 with the envelope, not a 204 - a 204 carries no body, so the client
    would have nothing to read.

=== "A mistake"

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

## 3. Raise your own error

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

A `DomainError` is DRF's own `APIException` with `data` added, so it is
raised from a service, a task or a command alike.

## Next

* [The tutorial](../tutorial/index.md) builds the example shop a part at a
  time.
* [Adopt it in an existing project](../how-to/adopt.md) - a project with an
  envelope of its own already.
* [The contract](../contract.md) has every shape and every error code.
