# Tutorial

The example shop, a part at a time: products with a stock, and the orders that
take from it. At the end every answer it gives is in one envelope, its lists
come a page at a time, its failures say what a client can do about them, and
its schema says all of it.

| | you will |
|---|---|
| [1. The envelope](01-the-envelope.md) | put a viewset's answers in the envelope, and choose what each one says |
| [2. Pages](02-pages.md) | page products by number and orders by cursor, and let the client choose a size |
| [3. Errors](03-errors.md) | answer every failure in the envelope - validation, your own errors, a bug |
| [4. The schema and languages](04-schema-and-languages.md) | see the envelope in Swagger, and answer in Persian |

The code on these pages is the example project's own, included from it - so
every line shown here is a line its tests run. To follow along, run the shop:

```bash
git clone https://github.com/amirAI-dot/drf-parcel
cd drf-parcel
python -m venv .venv && .venv/bin/pip install -e '.[schema]'
cd example
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py example_data
../.venv/bin/python manage.py runserver
```

It needs nothing but SQLite, and nobody signs in: it shows the shape of the
answers, not who may ask.
