"""
The project the test suite runs against.

The smallest project the library can be installed in: Django's
``contenttypes``, DRF and the library. Each stage adds what it tests and
nothing more.

The database is chosen by ``DRF_PARCEL_TEST_DATABASE`` - ``sqlite`` (the
default) or ``postgres``, configured by the standard ``PG*`` variables - so
one suite proves the same things on both.
"""

import os

from django.core.exceptions import ImproperlyConfigured

SECRET_KEY = 'only-for-the-test-suite'
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'drf_parcel',
    'tests.project.shelf',
]

MIDDLEWARE: list[str] = []

ROOT_URLCONF = 'tests.project.urls'

LANGUAGE_CODE = 'en'
LANGUAGES = [('en', 'English'), ('fa', 'Persian')]

REST_FRAMEWORK: dict[str, object] = {
    # Nobody is signed in: what is tested here is the shape, not who may ask.
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
}

_DATABASES = {
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', 'drf_parcel'),
        'USER': os.environ.get('PGUSER', 'postgres'),
        'PASSWORD': os.environ.get('PGPASSWORD', 'postgres'),
        'HOST': os.environ.get('PGHOST', 'localhost'),
        'PORT': os.environ.get('PGPORT', '5432'),
    },
}

TEST_DATABASE = os.environ.get('DRF_PARCEL_TEST_DATABASE', 'sqlite')

if TEST_DATABASE not in _DATABASES:
    raise ImproperlyConfigured(
        f'DRF_PARCEL_TEST_DATABASE must be one of {sorted(_DATABASES)}, not {TEST_DATABASE!r}.'
    )

DATABASES = {'default': _DATABASES[TEST_DATABASE]}
