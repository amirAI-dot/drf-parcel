# Versions

## What it runs on

| | |
|---|---|
| Python | 3.11, 3.12, 3.13, 3.14 |
| Django | 5.2, 6.0, 6.1 |
| Django REST framework | 3.16 and later |
| drf-spectacular | 0.28 and later, with the `schema` extra |
| a database | any Django supports; tested on PostgreSQL and SQLite |

Every combination is tested in CI, and the oldest release of everything
together.

## Version numbers

[Semantic versioning](https://semver.org/). Before 1.0, a minor release -
0.2 - may change what leaves the server, and its changelog marks each such
change. From 1.0, the shape of the envelope, the error codes and the settings
change only in a major release.

A Django or Python release leaves the table when its own support ends.
