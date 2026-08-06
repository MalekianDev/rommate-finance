from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings import Settings

settings = Settings()

engine = create_async_engine(settings.db_url, echo=settings.debug_mode)
session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with session_maker() as session:
        yield session
