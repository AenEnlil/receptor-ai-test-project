from functools import lru_cache

from .settings.base import BaseAppSettings


@lru_cache
def get_settings() -> BaseAppSettings:
    """
    Using to receive application settings
    :return: returns settings
    """
    return BaseAppSettings()
