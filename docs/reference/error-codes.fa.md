# کدهای خطا

هر کدی که کتابخانه خودش می‌فرستد. کلاینت بر اساس این‌ها تصمیم می‌گیرد، هرگز
بر اساس پیام. هر کدام با [`ERROR_CODES`](settings.md#failures) قابل تغییر اسم
است.

| وضعیت | `error_code` | از کجا | `data` |
|---|---|---|---|
| 400 | `validation_error` | serializer، `ValidationError` خود Django، `InvalidInputError` | `fields`: همه‌ی مشکل‌ها، بر اساس مسیر تخت فیلدشان |
| 400 | `parse_error` | بدنه‌ای که JSON معتبر نیست | `{}` |
| 400 | `invalid_cursor` | cursorی که سرور نمی‌تواند بخواند | `{}` |
| 401 | `not_authenticated` | اطلاعات ورود فرستاده نشده. 403، همان‌طور که DRF جواب می‌دهد، وقتی اولین کلاس احراز هویت view هدر `WWW-Authenticate` نمی‌فرستد - احراز هویت با session | `{}` |
| 401 | `authentication_failed` | اطلاعات ورود اشتباه یا منقضی | `{}` |
| 403 | `permission_denied` | `PermissionDenied` در DRF یا Django، با جمله‌ای که با آن raise شده | `{}` |
| 404 | `not_found` | `NotFound`، یا `Http404` خود Django - بدون گفتن اینکه چه چیزی جستجو شده | `{}` |
| 405 | `method_not_allowed` | متدی که view ندارد؛ `Allow` می‌گوید کدام‌ها را دارد | `{}` |
| 406 | `not_acceptable` | `Accept`ی که هیچ چیز نمی‌تواند جوابش را بدهد | `{}` |
| 409 | `already_exists` | قید unique، با `HANDLE_INTEGRITY_ERRORS` | `{}` |
| 409 | `conflict` | قید foreign key، با `HANDLE_INTEGRITY_ERRORS`؛ `ConflictError` | `{}` |
| 415 | `unsupported_media_type` | بدنه‌ای از نوعی که view نمی‌خواند | `{}` |
| 429 | `rate_limited` | محدودیت تعداد درخواست؛ `Retry-After` همان را می‌گوید | `retry_after`، به ثانیه |
| 500 | `internal_error` | هر چیزی که کسی طراحی‌اش نکرده | `{}` |
| 503 | `service_unavailable` | `ServiceUnavailableError` | `{}` |

خطای خود پروژه `default_code` خودش را می‌فرستد، و `data`ای که با آن raise
شده - و هرگز تغییر اسم نمی‌دهد.

## `data.fields`

```json
{"name": [{"code": "required", "message": "This field is required."}],
 "items.0.quantity": [{"code": "min_value", "message": "Ensure this value is greater than or equal to 1."}],
 "non_field_errors": [{"code": "invalid", "message": "The dates are the wrong way round."}]}
```

`code` هر مشکل همان کد خود DRF یا Django است: `required`، `blank`، `null`،
`invalid`، `max_length`، `min_length`، `max_value`، `min_value`، `unique`،
`does_not_exist`، `incorrect_type`، `invalid_choice` و بقیه - یا کدی که
validator پروژه با آن raise کرده.
