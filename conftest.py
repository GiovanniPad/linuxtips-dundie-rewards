from unittest.mock import patch
import pytest
from sqlmodel import create_engine
from dundie import models
from dundie.models import Person
from dundie.utils.db import add_person
from dundie.database import get_session


@pytest.fixture(autouse=True, scope="function")
def setup_testing_database(tmp_path):
    """For each test, create a database file on tmpdir
    force database.py to use that filepath.
    """
    test_db = tmp_path / "database.test.db"
    engine = create_engine(f"sqlite:///{test_db}")
    models.SQLModel.metadata.create_all(bind=engine)
    with patch("dundie.database.engine", engine), get_session() as session, patch("keyring.get_password") as mock_keyring:
        data = {
                "role": "Manager",
                "dept": "Management",
                "name": "Michael Scott",
                "email": "michael@dundermifflin.com",
            }
        password = "1234"
        person, _ = add_person(session, Person(**data), password)
        session.commit()

        mock_keyring.return_value = person.email
        
        yield


@pytest.fixture(scope="function")
def fictional_data():
    data = [
        Person(
            name="Joe Doe", dept="Sales", role="Manager", email="joe@doe.com"
        ),
        Person(
            name="Jim Doe", dept="Security", role="Guard", email="jim@doe.com"
        ),
    ]

    return data
