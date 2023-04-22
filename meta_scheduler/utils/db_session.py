from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from example import settings


def get_url() -> str:
    return (
        f"postgresql://{settings.db.USER}:{settings.db.PASSWORD}"
        f"@{settings.db.HOST}:{settings.db.PORT}/{settings.db.DATABASE}"
    )


engine = create_engine(
    get_url(),
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_pre_ping=True,
)

DBSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)


class DBContextManager:
    def __init__(self):
        self.conn = DBSession()

    def __enter__(self) -> Session:
        return self.conn

    def __exit__(self, exc_type, exc_value, exc_tb):
        del exc_type
        del exc_value
        del exc_tb
        self.conn.close()


def get_db() -> Session:
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
