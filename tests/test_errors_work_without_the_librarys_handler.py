"""
The library's errors answer sensibly under DRF's own handler too.

If this fails, a project that installs the mixin and keeps DRF's handler
turns every ``DomainError`` into a 500.
"""

from django.test import override_settings
from rest_framework.test import APIClient


@override_settings(REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES': []})
def test_a_domain_error_under_drfs_handler(client: APIClient) -> None:
    response = client.get('/fail/domain/')

    assert response.status_code == 409
    assert response.json() == {'detail': 'This province has branches and cannot be deleted.'}
