# Answer a database constraint

Two people take the same name at the same moment. Both pass the serializer's
uniqueness check, and the database refuses the second: an `IntegrityError`,
which is a 500 unless the project turns the net on:

```python
DRF_PARCEL = {'HANDLE_INTEGRITY_ERRORS': True}
```

| the constraint | the answer |
|---|---|
| unique | 409 `already_exists` - the input was right, and the row was taken in between |
| foreign key | 409 `conflict` - the row it points at changed in between |
| not null, check | 500 - a rule the serializer should have stated is missing |

The kind is read from the code the database driver reports - PostgreSQL,
SQLite, MySQL - never from its text, and neither the text nor a column's name
leaves the server. Which field was taken is the serializer's to say: the net
is for the race the serializer cannot see.
