"""
Which constraint the database refused, read from the driver's code.

Never from the error's text, which changes with the database, its version
and its language - and which can carry a table's, a column's or a
constraint's name. Django keeps the driver's own exception as the
``IntegrityError``'s cause, and each driver says the kind in a number:

=============  ====================  ========================  ============
constraint     PostgreSQL sqlstate   SQLite sqlite_errorcode   MySQL errno
=============  ====================  ========================  ============
unique         23505                 2067, 1555                1062
foreign key    23503                 787                       1451, 1452
not null       23502                 1299                      1048
check          23514                 275                       3819
=============  ====================  ========================  ============

A code not in the table is ``None``: the kind is not known, and what is not
known is refused.
"""

from typing import Final, Literal

Kind = Literal['unique', 'foreign_key', 'not_null', 'check']

#: PostgreSQL's SQLSTATE, as psycopg (``sqlstate``) and psycopg2 (``pgcode``) report it.
_POSTGRESQL: Final[dict[str, Kind]] = {
    '23505': 'unique',
    '23503': 'foreign_key',
    '23502': 'not_null',
    '23514': 'check',
}

#: SQLite's extended result codes, as ``sqlite3`` reports them from Python 3.11.
_SQLITE: Final[dict[int, Kind]] = {
    2067: 'unique',
    1555: 'unique',  # a primary key
    787: 'foreign_key',
    1299: 'not_null',
    275: 'check',
}

#: MySQL's and MariaDB's error numbers, the first argument of the driver's error.
_MYSQL: Final[dict[int, Kind]] = {
    1062: 'unique',
    1451: 'foreign_key',  # a row still referred to
    1452: 'foreign_key',  # a reference to a row that is not there
    1048: 'not_null',
    3819: 'check',
}


def kind_of(error: BaseException) -> Kind | None:
    """The kind of constraint an ``IntegrityError`` broke, or None when it cannot be told."""
    cause = error.__cause__

    if cause is None:
        return None

    state = getattr(cause, 'sqlstate', None) or getattr(cause, 'pgcode', None)

    if isinstance(state, str):
        return _POSTGRESQL.get(state)

    sqlite_code = getattr(cause, 'sqlite_errorcode', None)

    if isinstance(sqlite_code, int):
        return _SQLITE.get(sqlite_code)

    arguments = getattr(cause, 'args', ())

    if arguments and isinstance(arguments[0], int):
        return _MYSQL.get(arguments[0])

    return None
