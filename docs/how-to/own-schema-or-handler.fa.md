# استفاده از کلاس اسکیما یا handler خودتان

## AutoSchema خود پروژه

```python
from drf_spectacular.openapi import AutoSchema
from drf_parcel.schema import ParcelSchemaMixin


class ProjectSchema(ParcelSchemaMixin, AutoSchema):
    ...                                    # the project's own customisation
```

```python
REST_FRAMEWORK = {'DEFAULT_SCHEMA_CLASS': 'config.schema.ProjectSchema'}
```

## exception handler خود پروژه

handlerی که پیش یا پس از handler کتابخانه کاری می‌کند، آن را صدا می‌زند - و
با `functools.wraps` این را می‌گوید، تا اسکیما همچنان بداند خطاها در قالب‌اند:

```python
import functools

from drf_parcel.handlers import exception_handler


@functools.wraps(exception_handler)
def project_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response['X-Request-Id'] = context['request'].META.get('HTTP_X_REQUEST_ID', '')
    return response
```

بدون `functools.wraps` پاسخ‌ها همان‌اند، ولی اسکیما هیچ قالب خطایی را مستند
نمی‌کند: فقط چیزی را قول می‌دهد که می‌تواند تشخیص بدهد.

## بیرون از DRF

handler به چیزی شکل می‌دهد که به یک view در DRF برسد. آدرسی که با هیچ URLی
جور نیست، یا خطایی در یک middleware، را Django جواب می‌دهد، با `handler404` و
`handler500` خود پروژه - این‌ها مال کل پروژه‌اند، پنل ادمین و صفحه‌های وب هم، و
کتابخانه به آن‌ها دست نمی‌زند.
