# بیرون گذاشتن یک view از قالب

## viewی که فراخواننده‌اش شکل خودش را انتظار دارد

webhookی که درگاه پرداخت صدا می‌زند، health checkی که load balancer
می‌خواند:

```python
class HealthView(EnvelopeMixin, APIView):
    parcel_wrap = False

    def get(self, request):
        return Response({'ok': True})
```

هر پاسخ این view همان‌طور است که DRF می‌دهد - صفحه‌هایش هم، که همان `count`،
`next`، `previous` و `results` خود DRF هستند. خطاهایش همچنان از exception
handler رد می‌شوند، که مال کل پروژه است؛ در پروژه‌ای که نباید آن را داشته
باشد، handler را نصب نکنید.

## چیزهایی که خودبه‌خود دست نمی‌خورند

برای این‌ها لازم نیست چیزی بگویید - mixin فقط پاسخ موفقی را در قالب می‌گذارد
که به‌صورت JSON رندر می‌شود:

* فایل، PDF، استریم، ریدایرکت؛
* پاسخی از یک renderer دیگر - CSV، template؛
* خطایی که view دستی ساخته، `Response({...}, status=400)`؛
* پاسخ `205 Reset Content`، که بدنه‌ای ندارد تا قالب در آن گذاشته شود.

## viewی بدون mixin

viewی که از `EnvelopeMixin` ارث نمی‌برد همان‌طور که همیشه جواب می‌داد جواب
می‌دهد. فقط آنچه صریحاً با `success_response` جواب می‌دهد - و صفحه‌هایش، از
طریق paginator کتابخانه - در قالب است.
