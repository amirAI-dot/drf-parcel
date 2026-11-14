from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DrfParcelConfig(AppConfig):
    """Installed so Django finds the library's catalogue and its checks."""

    name = 'drf_parcel'
    verbose_name = _('Response envelope')
