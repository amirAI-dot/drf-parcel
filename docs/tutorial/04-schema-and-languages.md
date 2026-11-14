# 4. The schema and languages

## The schema says what arrives

drf-spectacular reads serializers, so on its own it documents what is
*inside* the envelope - and a client generated from it writes `response.id`
where the truth is `response.data.id`. `ParcelAutoSchema` documents the
envelope itself. Open <http://127.0.0.1:8000/api/docs/>:

* every success of a view with the mixin is the envelope, with `data` the
  serializer - and a delete the 200 it answers;
* each page is its own component, named for its kind - `ProductPage`,
  `OrderCursorPage`;
* `page_size` appears on products, with its ceiling as the maximum, and not
  on orders;
* every operation's `default` answer is `ErrorEnvelope`, and an operation
  that takes a body has `ValidationErrorEnvelope` as its 400.

A view left out of the envelope is documented as it answers:

```python title="example/shop/api.py"
--8<-- "example/shop/api.py:health"
```

## Answering in Persian

With `LocaleMiddleware`, the language is the request's:

```bash
curl -H 'Accept-Language: fa' http://127.0.0.1:8000/api/products/1/
```

The same envelope, its `message` - "Done." - said in Persian. The keys, the
codes and the data do not change: only what a person reads does.

Every sentence the library says comes in Persian. DRF's own - "This field
is required." - comes in DRF's languages. Your own messages, marked with
`gettext_lazy`, are translated in your project's catalogue.

## Where to go from here

* [How-to guides](../how-to/index.md) - adopting it in an existing project,
  reading the envelope from a frontend, testing.
* [The contract](../contract.md) - every shape and code.
