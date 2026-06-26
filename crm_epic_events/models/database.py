from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from crm_epic_events.config import Config


engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    pool_size=3,
    max_overflow=7,
    pool_recycle=900,
    pool_timeout=10,
    pool_use_lifo=True,
    connect_args={"connect_timeout": 5},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=True,
)


Base = declarative_base()


def get_db() -> Session:
    return SessionLocal()
