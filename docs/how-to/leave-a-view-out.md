# Leave a view out of the envelope

## A view whose caller expects its own shape

A webhook a payment gateway calls, a health check a load balancer reads:

```python
class HealthView(EnvelopeMixin, APIView):
    parcel_wrap = False

    def get(self, request):
        return Response({'ok': True})
```

Every answer of the view is as DRF gives it - its pages too, which are DRF's
own `count`, `next`, `previous` and `results`. Its failures still pass
through the exception handler, which is the project's; leave the handler out
of a project that must not have it.

## What is left alone by itself

Nothing has to be said for these - the mixin only wraps a success rendered as
JSON:

* a file, a PDF, a stream, a redirect;
* a response from another renderer - a CSV, a template;
* a failure a view made by hand, `Response({...}, status=400)`;
* a `205 Reset Content`, which has no body to put an envelope in.

## A view without the mixin

A view that does not inherit `EnvelopeMixin` answers as it always did. Only
what it answers explicitly with `success_response` - and its pages, through
the library's paginator - is in the envelope.
