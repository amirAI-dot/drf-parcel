"""
Everything but the schema works without drf-spectacular installed.

If this fails, ``pip install drf-parcel`` - without the ``schema`` extra -
gives a project a library that cannot be imported.
"""

import pkgutil
import subprocess
import sys

import drf_parcel

#: Imports every module of the library but the schema, with drf-spectacular made unimportable.
_SCRIPT = """
import importlib, sys
sys.modules['drf_spectacular'] = None
import django
django.setup()
for name in sys.argv[1:]:
    importlib.import_module(name)
"""


def test_no_module_but_the_schema_needs_drf_spectacular() -> None:
    modules = [
        f'drf_parcel.{found.name}'
        for found in pkgutil.iter_modules(drf_parcel.__path__)
        if found.name != 'schema'
    ]

    finished = subprocess.run(
        [sys.executable, '-c', _SCRIPT, *modules],
        capture_output=True,
        text=True,
        env={'DJANGO_SETTINGS_MODULE': 'tests.project.settings', 'PYTHONPATH': '.'},
        check=False,
    )

    assert finished.returncode == 0, finished.stderr
    assert 'drf_parcel.handlers' in modules
