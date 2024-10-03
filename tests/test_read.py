import pytest

from dundie.core import read
from dundie.database import add_person, commit, connect


@pytest.mark.unit
def test_read_with_query():
    pk = "joe@doe.com"
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}
    db = connect()
    _, created = add_person(db, pk, data)
    assert created is True

    pk = "jim@doe.com"
    data = {"name": "Jim Doe", "role": "Manager", "dept": "Management"}
    _, created = add_person(db, pk, data)
    assert created is True
    commit(db)

    response = read()
    assert len(response) == 2

    response = read(dept="Management")
    assert len(response) == 1
    assert response[0]["name"] == "Jim Doe"

    response = read(email="joe@doe.com")
    assert len(response) == 1
    assert response[0]["name"] == "Joe Doe"
