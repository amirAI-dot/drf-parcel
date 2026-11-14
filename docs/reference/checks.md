# Start-up checks

`manage.py check` - and `runserver`, and `migrate` - reports a setting that
cannot work, before a client finds it.

| id | what is wrong | what to do |
|---|---|---|
| `drf_parcel.E001` | `DRF_PARCEL` is not a dictionary, has a key the library does not know, or `MESSAGES` has one | the message names the key; correct its spelling |
| `drf_parcel.E002` | the page size or `MAX_PAGE_SIZE` is not a whole number above zero | the page size is `DRF_PARCEL['PAGE_SIZE']`, else `REST_FRAMEWORK['PAGE_SIZE']` |
| `drf_parcel.E003` | `MAX_PAGE_SIZE` is below the page size | raise the ceiling - often after adopting the library with a large `REST_FRAMEWORK['PAGE_SIZE']` |
| `drf_parcel.E004` | `CLIENT_PAGE_SIZE` is not `True` or `False` | |
| `drf_parcel.E005` | `PAGE_SIZE_QUERY_PARAM` is not the name of a parameter | |
| `drf_parcel.E006` | `FIELD_ERRORS` is neither `'detailed'` nor `'messages'` | |
| `drf_parcel.E007` | `FIELD_PATH_SEPARATOR` is empty | |
| `drf_parcel.E008` | `ERROR_CODES` is not a dictionary, renames a code the library does not send, or renames one to nothing | the hint lists the codes it sends |
| `drf_parcel.E009` | `HANDLE_INTEGRITY_ERRORS` or `RAISE_UNHANDLED_IN_DEBUG` is not `True` or `False` | |
| `drf_parcel.E010` | `REPORTER` is not the dotted path to a function | |

A check that fails does not stop a failure being answered: a renaming that
cannot work is passed over by the handler, and the failure answered with the
standard code.
