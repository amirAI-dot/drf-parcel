# Contributing

## The checks

Every check runs through [nox](https://nox.thea.codes), the same sessions
locally and in CI. With [uv](https://docs.astral.sh/uv/) installed, a Python
that is not installed is fetched.

```bash
uv tool install nox
nox -s lint types tests
```

| session | |
|---|---|
| `lint` | ruff, lint and format |
| `types` | mypy, strict |
| `tests` | every supported Python and Django, at full branch coverage |
| `oldest` | the oldest release of everything supported |
| `package` | the built wheel, installed alone; the example shop's tests run on it |
| `messages` | the Persian catalogue compiled |
| `docs` | this site, built with no broken link - `nox -s docs -- serve` while writing |

The suite runs on SQLite by default, and on PostgreSQL with
`DRF_PARCEL_TEST_DATABASE=postgres` and the standard `PG*` variables.

## The rules

* **The contract first.** A change to what leaves the server is a change to
  [the contract](../contract.md) before it is code.
* **Tests are named after what they hold** -
  `test_a_page_never_holds_more_than_the_ceiling.py` - and a test's name says
  what would go wrong in the world if it failed. Every line is run by a test.
* **Every sentence a person reads is marked** with `gettext_lazy`, and
  translated in `src/drf_parcel/locale/fa/LC_MESSAGES/django.po`
  (`nox -s messages` compiles it). The suite fails on a sentence the catalogue
  lacks.
* **English and Persian.** A page of these documents is `name.md`, and its
  Persian `name.fa.md` beside it.
