import pytest

from dundie.core import read
from dundie.database import get_session
from dundie.utils.db import add_person


@pytest.mark.unit
def test_read_with_query(fictional_data):
    data = fictional_data
    session = get_session()

    for person in data:
        add_person(session=session, instance=person)
        session.commit()

    result = read()

    assert len(result) == 3

    result = read(dept="Sales")
    assert result[0]["name"] == "Joe Doe"

    result = read(email="jim@doe.com")
    assert result[0]["name"] == "Jim Doe"
