import pytest

from dundie.core import add
from dundie.database import add_person, commit, connect
from dundie.models import Balance, Person


@pytest.mark.unit
def test_add_movement():
    pk = "joe@doe.com"
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}

    db = connect()

    _, created = add_person(db, Person(pk=pk, **data))
    assert created is True

    pk = "jim@doe.com"
    data = {"name": "Jim Doe", "role": "Manager", "dept": "Management"}

    _, created = add_person(db, Person(pk=pk, **data))
    assert created is True

    commit(db)

    add(-30, email="joe@doe.com")
    add(90, dept="Management")

    db = connect()

    assert db[Balance].get_by_pk("joe@doe.com").value == 470
    assert db[Balance].get_by_pk("jim@doe.com").value == 190
