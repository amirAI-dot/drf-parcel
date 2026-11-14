# نوشتن خطاهای خودتان

## یک DomainError

```python
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from drf_parcel.exceptions import DomainError


class ProvinceInUseError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'province_in_use'
    default_detail = _('This province has branches and cannot be deleted.')
```

اسم‌های خود DRF: `default_code` به‌عنوان `error_code` فرستاده می‌شود و
`default_detail` به‌عنوان `message`. جمله را با `gettext_lazy` علامت بزنید تا
به زبان درخواست گفته شود.

## با چیزی که کلاینت بر اساسش کاری می‌کند raise کنید

```python
raise ProvinceInUseError(data={'branches': 3})
raise ProvinceInUseError(_('Move its 3 branches first.'), data={'branches': 3})
raise ProvinceInUseError(code='province_locked')
```

`data` چیزی است که کلاینت بر اساسش کاری می‌کند - کدام رکورد سر راه است، چقدر
صبر کند. هرگز چیزی که شخص نباید جای دیگری بخواند: همان‌طور که هست از سرور
بیرون می‌رود.

## از سرویس، تسک، command

`DomainError` یک exception معمولی هم هست. سرویس آن را raise می‌کند، و قانون
از هر جا که برسد برقرار می‌ماند:

```python
def delete_province(province):
    branches = province.branches.count()
    if branches:
        raise ProvinceInUseError(data={'branches': branches})
    province.delete()
```

یک تسک Celery یا یک management command آن را مثل هر exception دیگری catch
می‌کند.

## خطاهایی که همراه کتابخانه است

| کلاس | وضعیت | `error_code` |
|---|---|---|
| `InvalidInputError` | 400 | `validation_error` |
| `InvalidCursorError` | 400 | `invalid_cursor` |
| `AuthenticationFailedError` | 401 | `authentication_failed` |
| `PermissionDeniedError` | 403 | `permission_denied` |
| `NotFoundError` | 404 | `not_found` |
| `ConflictError` | 409 | `conflict` |
| `RateLimitedError` | 429 | `rate_limited` |
| `ServiceUnavailableError` | 503 | `service_unavailable` |

هر جا DRF خطایی با همین معنی دارد، خطای کتابخانه همان خطای DRF هم هست -
`NotFoundError` یک `NotFound` است - پس کدی که خطای DRF را catch می‌کند همچنان
کار می‌کند.

## خطاهای پیش از کتابخانه

هر زیرکلاس `APIException` خود DRF بدون تغییر در قالب جواب می‌دهد. یک attribute
به اسم `data` به آن بدهید تا آن هم فرستاده شود. `ValidationError` خود Django -
`clean()` یک مدل - به‌عنوان خطای اعتبارسنجی، فیلد به فیلد، برمی‌گردد.
