# Contributing

Thank you for wanting to help. Issues and pull requests are welcome.

* **A bug** - open an issue with the smallest view that shows it, what it
  answered, and what you expected. The [questions](https://amirai-dot.github.io/drf-parcel/faq/)
  may already answer it.
* **A change to what leaves the server** - a key, a code, a shape - starts
  as an issue: [the contract](docs/contract.md) changes first, the code after.
* **A pull request** - against `main`, with a test that fails without it.

## Working on it

```bash
uv tool install nox
nox -s lint types tests
```

Every check, the rules for tests and translations, and how to build the
documentation are in
[Contributing](https://amirai-dot.github.io/drf-parcel/project/contributing/).

Every sentence a person reads is in English and Persian: a new one is marked
with `gettext_lazy` and translated in `src/drf_parcel/locale/fa/LC_MESSAGES/django.po`.
A documentation page `name.md` has its Persian `name.fa.md` beside it.
