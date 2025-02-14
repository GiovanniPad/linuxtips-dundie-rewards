import pytest

from dundie.core import load

from .constants import TEST_PEOPLE_FILE


@pytest.mark.unit
@pytest.mark.high
def test_load_positive_insert_three_people():
    """
    Test if load function insert three people to the database
    """

    people = load(TEST_PEOPLE_FILE)
    assert len(people) == 3


@pytest.mark.unit
@pytest.mark.high
def test_load_positive_created_first_person():
    """
    Test if load function created the first person in people file.
    """
    test_person = {
        "name": "Jim Halpert",
        "dept": "Sales",
        "role": "Salesman",
        "email": "jim@dundlermifflin.com",
        "currency": "USD",
        "created": True,
    }

    first_person = load(TEST_PEOPLE_FILE)[0]
    assert test_person == first_person
