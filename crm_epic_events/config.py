import os

import sentry_sdk

from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


class Config:
    APP_ENV = os.getenv("APP_ENV")

    # database configs
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # auth config
    SECRET_KEY = os.getenv("SECRET_KEY")
    AUTH_ALGORITHM = os.getenv("AUTH_ALGORITHM")
    ACCESS_TOKEN_LIFETIME = int(os.getenv("ACCESS_TOKEN_LIFETIME"))
    REFRESH_TOKEN_LIFETIME = int(os.getenv("REFRESH_TOKEN_LIFETIME"))

    # sentry config
    SENTRY_DSN = os.getenv("SENTRY_DSN")


def init_sentry():
    dsn = Config.SENTRY_DSN

    if not dsn:
        print("[Warning] SENTRY_DSN not set. Sentry is disabled.")
        return

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=0.0,  # No performance monitoring needed for CLI
        environment=Config.APP_ENV,
        sample_rate=1.0,
        send_default_pii=False,
        max_breadcrumbs=50,
        attach_stacktrace=True,
    )
