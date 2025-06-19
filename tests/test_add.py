from decimal import Decimal

import pytest
from sqlmodel import select
from dundie.core import add
from dundie.database import get_session
from dundie.models import Balance
from dundie.utils.db import add_person


@pytest.mark.unit
def test_add_movement(fictional_data):
    data = fictional_data
    session = get_session()

    for person in data:
        add_person(session, person)
        session.commit()

    add(Decimal(-30), email="joe@doe.com")
    add(Decimal(90), dept="Security")

    with session:
        result = session.exec(
            select(Balance).where(Balance.person == data[0])
        ).fetchall()

        assert result[0].value == Decimal(70)

        result = session.exec(
            select(Balance).where(Balance.person == data[1])
        ).fetchall()

        assert result[0].value == Decimal(590)
