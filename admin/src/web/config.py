import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "123456")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    pass


class DevelopmentConfig(Config):
    DEBUG_TB_INTERCEPT_REDIRECTS = (
        False  # Para evitar que el debugbar se detenga en los redirects
    )
    pass

class TestingConfig(Config):
    TESTING = True


config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}


def get_current_config(env=None):
    if env is None:
        env = os.getenv("FLASK_ENV", "production")
    return config.get(env, ProductionConfig)
