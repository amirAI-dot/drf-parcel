# The example shop

[فارسی](README.fa.md)

Products with a stock, and the orders that take from it. Every part of
drf-parcel is in it, each in the file a project would put it in:

| what | where |
|---|---|
| the three `REST_FRAMEWORK` lines, the `DRF_PARCEL` setting, `LocaleMiddleware` | `config/settings.py` |
| the schema and its Swagger page | `config/urls.py` |
| numbered pages, a size the client chooses under a ceiling, a view's own message, an answer written by hand | `ProductViewSet` in `shop/api.py` |
| a feed read by cursor, newest first | `OrderViewSet` in `shop/api.py` |
| a view left out of the envelope | `HealthView` in `shop/api.py` |
| the shop's own errors, with `data` - and one written before the library | `shop/errors.py` |
| the rules that raise them | `shop/services.py` |
| where a bug is reported | `shop/reporting.py` |
| what all of it answers | `shop/tests.py` |

## Running it

From the repository's root, with the library installed in a fresh
environment:

```bash
python -m venv .venv && .venv/bin/pip install -e '.[schema]'
```

```bash
cd example
```

```bash
../.venv/bin/python manage.py migrate
```

```bash
../.venv/bin/python manage.py example_data
```

```bash
../.venv/bin/python manage.py runserver
```

Open <http://127.0.0.1:8000/api/docs/> to see every answer in the schema, or
ask it yourself:

```bash
curl 'http://127.0.0.1:8000/api/products/?page_size=3'
```

```json
{"success": true, "status_code": 200, "message": "Done.",
 "data": [{"id": 3, "name": "Bracelet", "price": "95.50", "stock": 0}, ...],
 "pagination": {"type": "page", "count": 28, "page": 1, "pages": 10, "page_size": 3,
                "has_next": true, "has_previous": false}}
```

```bash
curl -X POST -H 'Content-Type: application/json' -d '{"product": 3, "quantity": 1}' http://127.0.0.1:8000/api/orders/
```

```json
{"success": false, "status_code": 409, "message": "There is not enough of this product in stock.",
 "data": {"available": 0}, "error_code": "out_of_stock"}
```

```bash
curl -H 'Accept-Language: fa' http://127.0.0.1:8000/api/products/1/
```

The same answer, its message in Persian.

| try | to see |
|---|---|
| `GET /api/products/?page=2` | a numbered page |
| `GET /api/products/?page_size=500` | the ceiling: 20, not 500 |
| `POST /api/products/` with a name | the view's own message, "The product was added." |
| `DELETE /api/products/1/` | a product with orders: 409, `still_ordered`, how many |
| `POST /api/products/1/restock/` | an answer written by hand, wrapped once |
| `GET /api/orders/` then `?cursor=` | a feed read on by cursor |
| `POST /api/orders/` with `{}` | every field that is wrong, each with its code |
| `GET /api/orders/2/receipt/` | an error written before the library: 402, `payment_required` |
| `GET /api/health/` | `{"ok": true}` - a view left out |

## Its tests

```bash
../.venv/bin/python manage.py test
```

They are also run against the built package, by `nox -s package` from the
repository's root - so what is published is what the example runs on.
