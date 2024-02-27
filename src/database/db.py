import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
        The session function is a coroutine that returns an async context manager.
        The context manager yields a database session, and then closes it when the
        context ends. The session can be used to execute queries and transactions.

        :param self: Represent the instance of the class
        :return: A context manager
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.SQLALCHEMY_DATABASE_URL)


async def get_db():
    """
    The get_db function is a coroutine that returns an async context manager.
    When the context manager is entered, it yields a database session; when the
    context manager exits, it closes the session. The get_db function itself can be
    used as an async context manager:

    :return: A generator object
    """
    async with sessionmanager.session() as session:
        yield session
