
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):

    a: str = 'asd'

    #  JWT_CONFIGURATION
    SECRET_KEY: str = 'b2332538d21bfbc73a622c7be7556d4b6ec08330a2f04742b35a35d28962a797'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_LIFETIME_MINUTES: int = 15

    #  DATABASE_CONFIGURATION
    MONGO_URL: str = 'mongodb://localhost:27017'
    DATABASE_NAME: str = 'local_db'
