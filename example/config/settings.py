"""
The example shop's settings - the whole of what a project adds for the
library is marked ``drf-parcel``.

For trying it out only: the secret key is in the file and ``DEBUG`` is on.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'only-for-the-example'  # never in a real project
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    # drf-parcel: installed for its Persian catalogue and its start-up checks.
    'drf_parcel',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # drf-parcel: every message is said in the request's language - Accept-Language.
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': ['django.template.context_processors.request']},
    },
]

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_TZ = True
TIME_ZONE = 'UTC'
STATIC_URL = 'static/'

LANGUAGE_CODE = 'en'
LANGUAGES = [('en', 'English'), ('fa', 'Persian')]

REST_FRAMEWORK = {
    # Nobody signs in to the example: it shows the shape of the answers, not who may ask.
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
    # drf-parcel: the three lines - each works without the others.
    'EXCEPTION_HANDLER': 'drf_parcel.handlers.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'drf_parcel.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_parcel.schema.ParcelAutoSchema',
}

# drf-parcel: the library's own setting. Every key is optional.
DRF_PARCEL = {
    'PAGE_SIZE': 10,
    'MAX_PAGE_SIZE': 50,
    # Two orders at once for the last of a name: a 409, not a 500.
    'HANDLE_INTEGRITY_ERRORS': True,
    # Where a bug is reported - Sentry, in a real project.
    'REPORTER': 'shop.reporting.report',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'The example shop',
    'DESCRIPTION': 'Every answer in one envelope - the drf-parcel example.',
    'VERSION': '1.0.0',
}
