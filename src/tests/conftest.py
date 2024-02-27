import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.conf.config import config
from src.database.db import get_db
from src.entity.models import Base

SQLALCHEMY_DATABASE_URL = config.SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    """
    The session function is a fixture that will ensure that a new database session is created for each test and
        closed after the test runs. This allows us to run tests in parallel without worrying about them interfering with
        one another.

    :return: A session object
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    """
    The client function is a fixture that creates an application test client.
    It also handles setting up the database and closing it when the tests are done.
    The function takes a session as an argument, which allows you to pass in different sessions for different tests.

    :param session: Override the get_db function in app
    :return: A test client object
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    """
    The user function returns a dictionary with the following keys:
        username, email, password.

    :return: A dictionary with the user information
    """
    return {"username": "test_name", "email": "test@email.com", "password": "12345678"}
