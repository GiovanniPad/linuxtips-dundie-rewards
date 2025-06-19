"""Core module of dundie"""

import os
from csv import reader
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, cast
import keyring
from dundie.settings import KEYRING_SERVICE_NAME, KEYRING_USERNAME
from sqlmodel import select
from dundie.database import get_session
from dundie.models import Balance, Movement, Person, User
from dundie.settings import DATEFMT
from dundie.utils.auth import login_required
from dundie.utils.db import add_movement, add_person
from dundie.utils.errors import InsufficientBalanceError
from dundie.utils.exchange import get_rates
from dundie.utils.log import get_logger

log = get_logger()

Query = Dict[str, Any]
ResultDict = List[Dict[str, Any]]


@login_required
def load(filepath: str, from_person: Person) -> ResultDict:
    """Loads data from filepath to the database"""

    try:
        csv_data = reader(open(filepath))
    except FileNotFoundError as e:
        log.error(str(e))
        raise e

    people = []
    headers = ["name", "dept", "role", "email", "currency"]

    with get_session() as session:
        for line in csv_data:
            person_data = dict(zip(headers, [item.strip() for item in line]))
            instance = Person(**person_data)
            person, created = add_person(session, instance)
            return_data = person.model_dump(exclude={"id"})
            return_data["created"] = created
            people.append(return_data)

        session.commit()

    return people


@login_required
def read(from_person: Person, **query: Query) -> ResultDict:
    """Read data from db and filters using query"""
    query = {key: value for key, value in query.items() if value is not None}

    return_data = []
    query_statements = []

    if "dept" in query:
        query_statements.append(Person.dept == query["dept"])
    if "email" in query:
        query_statements.append(Person.email == query["email"])

    sql = select(Person)

    if query_statements:
        sql = sql.where(*query_statements)

    with get_session() as session:
        currencies = session.exec(select(Person.currency).distinct())

        rates = get_rates(list(currencies))
        results = session.exec(sql)

        for person in results:
            total = rates[person.currency].value * person.balance.value

            movements = session.exec(
                select(Movement).where(Movement.person_id == person.id)
            ).all()

            return_data.append(
                {
                    "email": person.email,
                    "balance": person.balance.value,
                    "last_movement": movements[-1].date.strftime(DATEFMT),
                    **person.model_dump(exclude={"id"}),
                    **{"value": total},
                }
            )

    return return_data


@login_required
def add(value: Decimal, from_person: Person, **query: Query):
    """Add value to each record on query."""
    query = {key: value for key, value in query.items() if value is not None}

    people = read(**query)

    if not people:  # prama: no cover
        raise RuntimeError("Not Found")

    with get_session() as session:
        user = os.getenv("USER")

        for person in people:
            instance = session.exec(
                select(Person).where(Person.email == person["email"])
            ).first()

            add_movement(session, cast(Person, instance), value, user)

        session.commit()


@login_required
def transfer(value: int, to_email: str, from_person: Person):
    """Transfer points between users"""

    confirmation = None
    with get_session() as session:
        sql = select(Balance.value).where(Balance.person == from_person)
        from_person_balance = session.exec(sql).first()

        if from_person_balance < value:
            raise InsufficientBalanceError(
                "You don't have sufficient balance to transfer"
            )

        add_movement(session, from_person, Decimal(-value), from_person.name)

        sql = select(Person).where(Person.email == to_email)
        to_person = session.exec(sql).first()

        add_movement(session, to_person, Decimal(value), from_person.name)
        confirmation = [True, to_person.name]
        session.commit()

    return confirmation


@login_required
def movements(from_person: Person, **query: Query):
    """Show the movements from users."""
    query = {key: value for key, value in query.items() if value is not None}

    return_data = []
    query_statements = []

    if "dept" in query:
        query_statements.append(Person.dept == query["dept"])
    if "email" in query:
        query_statements.append(Person.email == query["email"])

    sql = select(Person)

    if query_statements:
        sql = sql.where(*query_statements)
    with get_session() as session:
        persons = session.exec(sql)
        for person in persons:
            sql = select(Movement.date, Movement.value, Movement.actor).where(
                Movement.person == person
            )
            movements: list[tuple[datetime, Decimal, str]] = session.exec(
                sql
            ).all()

            for date, value, actor in movements:
                return_data.append(
                    {
                        "email": person.email,
                        "name": person.name,
                        "dept": person.dept,
                        "role": person.role,
                        "date": date.strftime(DATEFMT),
                        "value": value,
                        "actor": actor,
                    }
                )

    return return_data


def login(email: str, password: str):
    sql = (
        select(Person, User.password)
        .join(User, Person.id == User.person_id)
        .where(Person.email == email)
    )

    with get_session() as session:
        user = session.exec(sql).first()

    if not user or password != user[1]:
        return False

    user = user[0]
    keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, user.email)
    return True


def logout():
    logged = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    if logged:
        keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
        return True
    return False
