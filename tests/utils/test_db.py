import os
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


test_engine = create_engine(
    f"sqlite:///{os.path.join(BASE_DIR, 'test.database.sqlite3')}",
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> TestingSessionLocal:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
