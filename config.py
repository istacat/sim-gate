import os
from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class BaseConfig(BaseSettings):

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP: str = "3600"
    APP_NAME: str = "SIM API"
    APP_DESCRIPTION: str = "API sim manage service for Kryptr"


class DevelopConfig(BaseConfig):
    DEVELOP_DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'dev.database.sqlite3')}"

    @property
    def db_url(self):
        return self.DEVELOP_DATABASE_URL


class TestConfig(BaseConfig):
    TEST_DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'test.database.sqlite3')}"

    @property
    def db_url(self):
        return self.TEST_DATABASE_URL


class ProductionConfig(BaseConfig):
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'database.sqlite3')}"

    @property
    def db_url(self):
        return self.DATABASE_URL


_CONFIG = {
    "develop": DevelopConfig,
    "test": TestConfig,
    "production": ProductionConfig
}

CONFIG_TYPE = os.environ.get("CONFIG_TYPE", "develop")

config = _CONFIG[CONFIG_TYPE](
    _env_file=os.path.join(BASE_DIR, ".env"),
    _env_file_encoding="utf-8"
)
