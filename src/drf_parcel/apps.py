from django.apps import AppConfig
from django.core import checks
from django.utils.translation import gettext_lazy as _


class DrfParcelConfig(AppConfig):
    """Installed so Django finds the library's catalogue and runs its checks."""

    name = 'drf_parcel'
    verbose_name = _('Response envelope')

    def ready(self) -> None:
        from drf_parcel.checks import check_settings

        checks.register(check_settings)
