from app.settings.base import BaseAppSettings


class TestAppSettings(BaseAppSettings):
    DATABASE_NAME: str = 'test_database'
