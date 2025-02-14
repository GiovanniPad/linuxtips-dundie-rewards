from unittest.mock import patch
import pytest
from sqlmodel import create_engine
from dundie import models
from dundie.models import Person


@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    tmpdir = request.getfixturevalue("tmpdir")

    with tmpdir.as_cwd():
        yield


@pytest.fixture(autouse=True, scope="function")
def setup_testing_database():
    """For each test, create a database file on tmpdir
    force database.py to use that filepath.
    """
    engine = create_engine("sqlite:///:memory:")
    models.SQLModel.metadata.create_all(bind=engine)

    with patch("dundie.database.engine", engine):
        yield


@pytest.fixture(scope="function")
def fictional_person_data():
    data = [
        Person(
            name="Joe Doe", dept="Sales", role="Manager", email="joe@doe.com"
        ),
        Person(
            name="Jim Doe", dept="Security", role="Guard", email="jim@doe.com"
        ),
    ]

    return data
