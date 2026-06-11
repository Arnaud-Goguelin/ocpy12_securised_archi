from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from crm_epic_events.utils.config import Config


async_engine = create_async_engine(
    Config.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    future=True,
    pool_size=3,
    max_overflow=7,
    pool_recycle=900,
    pool_timeout=10,
    pool_use_lifo=True,
    connect_args={"connect_timeout": 5},
)

# async_sessionmaker create instance of AsyncSession, it is a factory function
async_session = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=True,
)


Base = declarative_base()


async def get_db():
    # use with create a context manager with close session automatically
    async with async_session() as db:
        yield db
