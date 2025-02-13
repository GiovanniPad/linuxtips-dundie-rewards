import pytest

from dundie.core import load
from dundie.database import EMPTY_DB, ORM, connect

from .constants import PEOPLE_FILE


@pytest.mark.unit
@pytest.mark.high
def test_load_positive_has_2_people():
    """Test load function."""
    assert len(load(PEOPLE_FILE)) == 2


@pytest.mark.unit
@pytest.mark.high
def test_db_schema():
    load(PEOPLE_FILE)

    db = connect()
    db_keys = {ORM.get_table_name(model) for model in db}

    assert db_keys == EMPTY_DB.keys()


@pytest.mark.unit
@pytest.mark.high
def test_load_positive_first_name_is_jim_halpert():
    """Test load function."""
    assert load(PEOPLE_FILE)[0]["name"] == "Jim Halpert"
