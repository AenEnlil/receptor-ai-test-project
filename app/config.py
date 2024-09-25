from functools import lru_cache

from .settings.base import BaseAppSettings, AppEnvTypes
from .settings.test import TestAppSettings

environments = {
    AppEnvTypes.local: BaseAppSettings,
    AppEnvTypes.test: TestAppSettings
}


@lru_cache
def get_settings() -> BaseAppSettings:
    """
    Using to receive application settings. Checks environment variable to return corresponding Settings
    :return: returns settings
    """
    app_env = BaseAppSettings().ENVIRONMENT
    config = environments[app_env]
    return config()
