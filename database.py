from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# when we switch to postgres, changing this should be one of the changes that we need to make and the rest of the code stays the same
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},  # sqlite only allows one thread, fastapi handles multiple requests, so we disable that restriction
)

# a session is a transaction with database, each requests gets its own session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    pass


# a dependency function that provides sessions to our routes, fastapi dependency injection calls this function for each requst and handles
# that clean up automatically
# dependency injection: hey, this route needs a database session to work, so go ahead and give it one
# instead of creating the session inside the route, we declare that we need one and fastapi provides it
def get_db():
    with SessionLocal() as db:
        yield db
