from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvTypes(Enum):
    local: str = 'local'
    test: str = 'test'


class BaseAppSettings(BaseSettings):
    ENVIRONMENT: AppEnvTypes = AppEnvTypes.local

    #  JWT_CONFIGURATION
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_LIFETIME_MINUTES: int = 15

    #  DATABASE_CONFIGURATION
    MONGO_URL: str
    DATABASE_NAME: str = 'project_db'

    model_config = SettingsConfigDict(env_file=".env")
