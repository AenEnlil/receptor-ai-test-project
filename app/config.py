from functools import lru_cache

from .settings.base import BaseAppSettings


@lru_cache
def get_settings() -> BaseAppSettings:
    return BaseAppSettings()
