# تست API در قالب

پاسخ را همان‌طور بخوانید که کلاینت می‌خواند - JSON روی سیم:

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

روی `error_code` و `data` assert کنید، نه روی `message`: پیام ترجمه می‌شود، و
وقتی جمله‌ای بازنویسی شود عوض می‌شود.

## یک باگ، در تست

تست‌ها با `DEBUG = False` اجرا می‌شوند، پس یک باگ به جای بالا رفتن، با قالب 500
جواب داده می‌شود - روی همان assert کنید:

```python
response = client.get('/api/broken/')
assert response.status_code == 500
assert response.json()['error_code'] == 'internal_error'
```

## یک تنظیم دیگر، برای یک تست

```python
from django.test import override_settings


@override_settings(DRF_PARCEL={'ERROR_CODES': {'not_found': 'missing'}})
def test_a_renamed_code(client):
    ...
```

تنظیم در هر درخواست خوانده می‌شود، پس override بلافاصله اثر می‌کند.

## به فارسی

```python
from django.utils import translation

answer = client.get('/api/products/1/', HTTP_ACCEPT_LANGUAGE='fa').json()

with translation.override('fa'):
    assert answer['message'] == translation.gettext('Done.')
```

تست‌های فروشگاه نمونه - `example/shop/tests.py` - هر بخش را همین‌طور تست
می‌کنند.
