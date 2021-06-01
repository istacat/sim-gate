from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from config import config
from .models import Base


engine = create_engine(
    config.db_url,
    connect_args={"check_same_thread": False}
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False
)

def get_session() -> Session:
    session = Session()
    try:
        yield session
    finally:
        session.close()

def create_db(engine) -> None:
    Base.metadata.create_all(engine)

def drop_db(engine) -> None:
    Base.metadata.drop_all(engine)


