"""
Every check the project runs, defined once - locally and in CI alike.

    nox -l                                   list the sessions
    nox -s lint                              lint and formatting
    nox -s types                             mypy
    nox -s tests                             every supported Python and Django
    nox -s "tests(3.13-django6.1)"           one combination
    nox -s oldest                            the oldest release of everything supported
    nox -s messages                          the catalogues compiled, .po to .mo
    nox -s package                           the built wheel installs, its catalogue in it

CI runs these same sessions, built from the same table, so a check that
passes here passes there and a supported version cannot be left out of one.
Pythons that are not installed are fetched by uv.
"""

import os

import nox

nox.needs_version = '>=2025.2.9'
nox.options.default_venv_backend = 'uv|virtualenv'
nox.options.sessions = ['lint', 'types', 'tests']

#: Every supported Django release, and the Pythons that release supports.
#: Adding a release, or dropping one, is a change to this table only.
SUPPORTED: dict[str, tuple[str, ...]] = {
    '5.2': ('3.11', '3.12', '3.13', '3.14'),
    '6.0': ('3.12', '3.13', '3.14'),
    '6.1': ('3.12', '3.13', '3.14'),
}

NEWEST_DJANGO = max(SUPPORTED, key=lambda release: tuple(map(int, release.split('.'))))
NEWEST_PYTHON = SUPPORTED[NEWEST_DJANGO][-1]

MATRIX = [(python, django) for django, pythons in SUPPORTED.items() for python in pythons]


def django_release(release: str) -> str:
    """The requirement that installs the newest patch of one Django release."""
    return f'django~={release}.0'


@nox.session(python=NEWEST_PYTHON)
def lint(session: nox.Session) -> None:
    """Lint and formatting."""
    session.install('--group', 'lint')
    session.run('ruff', 'check', '.')
    session.run('ruff', 'format', '--check', '.')


@nox.session(python=NEWEST_PYTHON)
def types(session: nox.Session) -> None:
    """mypy, strict, over the library's source."""
    session.install('-e', '.[schema]', '--group', 'types', django_release(NEWEST_DJANGO))
    session.run('mypy')


@nox.session
@nox.parametrize(
    'python,django',
    MATRIX,
    ids=[f'{python}-django{django}' for python, django in MATRIX],
)
def tests(session: nox.Session, django: str) -> None:
    """The suite, against one Python and one Django release."""
    session.install('-e', '.[schema]', '--group', 'test', django_release(django))
    session.run('pytest', '--cov', '--cov-report=term', *session.posargs)


#: The oldest release of each dependency the library supports, on the oldest Python.
OLDEST = (
    'django==5.2.*',
    'djangorestframework==3.16.0',
    'drf-spectacular==0.28.0',
)


@nox.session(python=MATRIX[0][0])
def oldest(session: nox.Session) -> None:
    """The suite against the oldest release of everything the library says it supports."""
    session.install('-e', '.[schema]', '--group', 'test', *OLDEST)
    session.run('pytest', '--cov', '--cov-report=term', *session.posargs)


#: Every catalogue the library ships.
CATALOGUES = ('src/drf_parcel/locale/fa/LC_MESSAGES/django.po',)


@nox.session(python=NEWEST_PYTHON)
def messages(session: nox.Session) -> None:
    """
    Compile each catalogue's .po into the .mo Django reads.

    By polib rather than gettext's msgfmt, so no system package is needed.
    The .mo is committed beside its .po; the suite fails when they disagree.
    """
    session.install('polib>=1.2')
    for catalogue in CATALOGUES:
        session.run(
            'python',
            '-c',
            'import polib, sys; polib.pofile(sys.argv[1]).save_as_mofile(sys.argv[1][:-3] + ".mo")',
            catalogue,
        )


@nox.session(python=NEWEST_PYTHON)
def package(session: nox.Session) -> None:
    """
    What is published works: the wheel is built and installed alone - not the
    source tree - and its catalogue is in it.
    """
    session.install('build')
    out = session.create_tmp()
    session.run('python', '-m', 'build', '--outdir', out)
    wheel = next(name for name in os.listdir(out) if name.endswith('.whl'))
    session.install(f'{os.path.join(out, wheel)}[schema]', django_release(NEWEST_DJANGO))

    with session.chdir(out):
        session.run(
            'python',
            '-c',
            'import pathlib, sys, drf_parcel; '
            'root = pathlib.Path(drf_parcel.__file__).parent; '
            'sys.exit("site-packages" not in str(root) '
            'or not (root / "locale/fa/LC_MESSAGES/django.mo").is_file() '
            'or not (root / "py.typed").is_file())',
        )
