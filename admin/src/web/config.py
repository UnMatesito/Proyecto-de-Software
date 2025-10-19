import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "8339d73af563bd9c5a87d19110b1c25997b2c078ad8351bec1aca62c20d74b93")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }
    MINIO_SERVER = os.getenv("MINIO_SERVER", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    MINIO_SECURE = True
    pass


class DevelopmentConfig(Config):
    DEBUG_TB_INTERCEPT_REDIRECTS = (
        False  # Para evitar que el debugbar se detenga en los redirects
    )
    SESSION_COOKIE_SECURE = False
    MINIO_SECURE = False
    pass


class TestingConfig(Config):
    TESTING = True


config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}


def get_current_config(env=None):
    """
    Obtiene la configuración actual de la aplicación Flask según el entorno.

    Si no se especifica un entorno, se toma el valor de la variable de entorno `FLASK_ENV`.
    Si no está definida, se usa la configuración de producción por defecto.

    Args:
        env (str, optional): Nombre del entorno de configuración ("development", "testing", "production").
            Si es None, se intenta obtener de la variable de entorno `FLASK_ENV`.

    Returns:
        Type[Config]: Clase de configuración correspondiente al entorno especificado.
    """
    if env is None:
        env = os.getenv("FLASK_ENV", "production")
    return config.get(env, ProductionConfig)
