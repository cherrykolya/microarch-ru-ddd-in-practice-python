from typing import AsyncContextManager, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.config.settings import get_settings

settings = get_settings()
db_settings = settings.database

engine = create_async_engine(
    db_settings.DSN.render_as_string(hide_password=False),
    **db_settings.get_sqlalchemy_config(),
)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)


def get_db_session() -> Callable[[], AsyncContextManager[AsyncSession]]:
    """Возвращает фабрику сессий."""
    return async_session_maker
