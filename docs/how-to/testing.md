# Test an API in the envelope

Read an answer as a client does - the JSON on the wire:

```python
from rest_framework.test import APIClient


def test_an_order_beyond_the_stock_says_how_many_there_are(db):
    ring = Product.objects.create(name='Ring', price='120.00', stock=2)

    response = APIClient().post('/api/orders/', {'product': ring.pk, 'quantity': 5},
                                format='json')

    assert response.status_code == 409
    assert response.json()['error_code'] == 'out_of_stock'
    assert response.json()['data'] == {'available': 2}
```

Assert on `error_code` and `data`, not on `message`: the message is
translated, and changes when a sentence is reworded.

## A bug, in a test

Tests run with `DEBUG = False`, so a bug answers the 500 envelope rather than
raising - assert on it:

```python
response = client.get('/api/broken/')
assert response.status_code == 500
assert response.json()['error_code'] == 'internal_error'
```

## Another setting, for one test

```python
from django.test import override_settings


@override_settings(DRF_PARCEL={'ERROR_CODES': {'not_found': 'missing'}})
def test_a_renamed_code(client):
    ...
```

The setting is read on every request, so an override takes effect at once.

## In Persian

```python
from django.utils import translation

answer = client.get('/api/products/1/', HTTP_ACCEPT_LANGUAGE='fa').json()

with translation.override('fa'):
    assert answer['message'] == translation.gettext('Done.')
```

The example shop's tests - `example/shop/tests.py` - test every part this way.
