from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# when we switch to postgres, changing this should be one of the changes that we need to make and the rest of the code stays the same
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},  # sqlite only allows one thread, fastapi handles multiple requests, so we disable that restriction
)

# a session is a transaction with database, each requests gets its own session
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # we want to keep the data in memory after we commit, otherwise we would have to query the database again to get the data
    class_=AsyncSession,  # we want to use the async version of the session
)


class Base(DeclarativeBase):
    pass


# a dependency function that provides sessions to our routes, fastapi dependency injection calls this function for each requst and handles
# that clean up automatically
# dependency injection: hey, this route needs a database session to work, so go ahead and give it one
# instead of creating the session inside the route, we declare that we need one and fastapi provides it
# def get_db():
#     with SessionLocal() as db:
#         yield db
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session