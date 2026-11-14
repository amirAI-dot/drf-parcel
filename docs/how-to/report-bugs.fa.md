# گزارش باگ‌ها به Sentry

یک exception پیش‌بینی‌نشده با یک 500 عمومی جواب داده می‌شود، روی logger
`drf_parcel` با traceback لاگ می‌شود - و به reporter پروژه داده می‌شود:

```python
DRF_PARCEL = {'REPORTER': 'config.reporting.report'}
```

```python
# config/reporting.py
import sentry_sdk


def report(exc, context):
    sentry_sdk.capture_exception(exc)
```

`context` همان context خود DRF است - `view` و `request`. reporter با هر 500
صدا زده می‌شود و هرگز با خطایی که کسی طراحی کرده: یک 404، یک شماره‌ی تلفن
اشتباه یا یک `DomainError` باگ نیست، و گزارش نمی‌شود. reporterی که خراب باشد
فقط یک خط لاگ هزینه دارد، نه پاسخ را.

!!! tip "یکپارچگی لاگ Sentry - یکی یا دیگری"

    Django هرگز exception را نمی‌بیند: کتابخانه 500 را جواب داده. ولی کتابخانه
    آن را در سطح `ERROR` با traceback لاگ می‌کند، و یکپارچگی لاگ Sentry - که
    به‌طور پیش‌فرض روشن است - همان خط را به یک event تبدیل می‌کند. از آن
    استفاده کنید، یا از `REPORTER`، نه هر دو: با هر دو، هر باگ دو بار گزارش
    می‌شود. `REPORTER` برای ابزاری است که لاگ را نمی‌خواند، یا برای وقتی که
    می‌خواهید جزئیات درخواست را خودتان اضافه کنید.

## DEBUG

در `DEBUG = True` به جای جواب، exception بالا می‌رود تا صفحه‌ی خطای Django
traceback را نشان بدهد. برای دیدن قالب در محیط توسعه:

```python
DRF_PARCEL = {'RAISE_UNHANDLED_IN_DEBUG': False}
```
