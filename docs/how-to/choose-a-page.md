# Choose how a list is paged

## By number or by cursor, per view

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

| choose | when |
|---|---|
| `PageNumberPagination` | a list a person pages through, with a count and numbered pages |
| `CursorPagination` | a feed read on and on - a table too large to count on every request, or rows added while it is read |

A cursor needs an ordering that does not change and is unique or nearly so -
a creation time, an id. Name it on the view (`ordering`), on a subclass of the
paginator, or with an `OrderingFilter`, which decides as DRF's does.

## The size

The size is read from the view, then the paginator, then
`DRF_PARCEL['PAGE_SIZE']`, then DRF's own `REST_FRAMEWORK['PAGE_SIZE']`, then
20:

```python
class ProductViewSet(EnvelopeMixin, ModelViewSet):
    page_size = 12
```

## Let the client choose it

```python
class ProductViewSet(EnvelopeMixin, ModelViewSet):
    page_size = 12
    client_page_size = True      # ?page_size= is read
    max_page_size = 48           # and never exceeded
```

or for every view, in `DRF_PARCEL`: `CLIENT_PAGE_SIZE`, `MAX_PAGE_SIZE` and
`PAGE_SIZE_QUERY_PARAM` (`page_size` by default). A size above the ceiling is
the ceiling; nothing, zero, a negative number or a word is the default - never
an error.

!!! warning "Always a ceiling"

    Without one, `?page_size=1000000` is a request to read a whole table, open
    to anybody. The library has no way to switch the ceiling off.

## No pages at all

```python
class CountryViewSet(EnvelopeMixin, ModelViewSet):
    pagination_class = None      # a short list read whole, on purpose
```

The list is under `data`, and there is no `pagination` key.
