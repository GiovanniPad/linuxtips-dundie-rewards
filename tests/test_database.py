import pytest
from sqlmodel import select

from dundie.models import Balance, InvalidEmailError, Person
from dundie.utils.db import add_movement, add_person, get_session


@pytest.mark.unit
def test_commit_to_database(fictional_person_data):
    session = get_session()
    data = fictional_person_data[0]

    add_person(session, data)
    session.commit()

    result = session.exec(
        select(Person).where(Person.email == data.email)
    ).first()

    assert result == data


@pytest.mark.unit
def test_add_person_for_the_first_time(fictional_person_data):
    session = get_session()
    data = fictional_person_data[1]

    _, created = add_person(session, data)
    session.commit()

    result = session.exec(
        select(Person).where(Person.email == data.email)
    ).first()

    assert created is True
    assert result.name == "Jim Doe"
    assert result.dept == "Security"
    assert result.role == "Guard"
    assert result.currency == "USD"


@pytest.mark.unit
def test_negative_add_person_invalid_email(fictional_person_data):
    session = get_session()
    data = fictional_person_data[0]

    data.email = ".@bla"
    with pytest.raises(InvalidEmailError):
        add_person(session, data)
        session.commit()


@pytest.mark.unit
def test_add_or_remove_points_for_person(fictional_person_data):
    session = get_session()
    person = fictional_person_data[1]

    person, *_ = add_person(session, person)
    session.commit()

    before = person.balance.value

    add_movement(session, person, -100, "system")
    session.commit()

    after = (
        session.exec(select(Balance).where(Balance.person == person))
        .first()
        .value
    )

    assert before == 500
    assert after == 400
