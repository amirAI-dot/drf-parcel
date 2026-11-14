# 2. Pages

## Numbered pages, by default

`DEFAULT_PAGINATION_CLASS` is the library's `PageNumberPagination`, so every
list is a page - products among them:

```bash
curl 'http://127.0.0.1:8000/api/products/?page=2'
```

```json
{"success": true, "status_code": 200, "message": "Done.",
 "data": [...],
 "pagination": {"type": "page", "count": 28, "page": 2, "pages": 3, "page_size": 10,
                "has_next": true, "has_previous": true}}
```

There is no `next` link to follow: the client is on another domain and asks
for `?page=3` itself.

## The client chooses the size, under a ceiling

The product viewset in [step 1](01-the-envelope.md) sets two attributes:

```python
client_page_size = True
max_page_size = 20
```

| the client asks | it gets |
|---|---|
| `?page_size=5` | 5 |
| `?page_size=500` | 20 - the ceiling, not an error |
| `?page_size=abc`, `0`, or nothing | 10 - the project's `PAGE_SIZE` |

`pagination.page_size` always says the size used. A view that does not allow
it ignores the parameter, and the schema does not offer it.

## Orders, as a feed

Orders are read newest first, and there are too many to count on every
request - a cursor, not a page number:

```python title="example/shop/api.py"
--8<-- "example/shop/api.py:orders"
```

```bash
curl http://127.0.0.1:8000/api/orders/
```

```json
{"success": true, "status_code": 200, "message": "Done.",
 "data": [{"id": 2, "product": 1, "quantity": 2, "paid": false, "created_at": "..."}, ...],
 "pagination": {"type": "cursor", "next_cursor": "cD0yMDI2...", "previous_cursor": null,
                "page_size": 10, "has_next": true, "has_previous": false}}
```

The client sends back what it was given - `?cursor=cD0yMDI2...` - and never
builds one. `has_next` is in both kinds, so one "load more" button works with
either, and `pagination.type` tells them apart.

## Next

[3. Errors](03-errors.md)
