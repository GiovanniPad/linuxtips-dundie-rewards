"""Core module of dundie"""

import os
from csv import reader
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, cast

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Balance, Movement, Person
from dundie.settings import DATEFMT
from dundie.utils.auth import authenticate_require, get_permission
from dundie.utils.db import add_movement, add_person
from dundie.utils.errors import InsufficientBalanceError
from dundie.utils.exchange import get_rates
from dundie.utils.log import get_logger

log = get_logger()

Query = Dict[str, Any]
ResultDict = List[Dict[str, Any]]


@authenticate_require
def load(filepath: str, from_person: Person, command: str) -> ResultDict:
    """Loads data from filepath to the database"""

    permission = get_permission(from_person, {}, command)
    if not permission:
        raise PermissionError(
            "You don't have permission to execute this action"
        )

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


@authenticate_require
def read(from_person: Person, command: str, **query: Query) -> ResultDict:
    """Read data from db and filters using query"""
    query = {key: value for key, value in query.items() if value is not None}

    permission = get_permission(from_person, query, command)
    if not permission:
        raise PermissionError(
            "You don't have permission to execute this action"
        )

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


@authenticate_require
def add(value: Decimal, from_person: Person, command: str, **query: Query):
    """Add value to each record on query."""
    query = {key: value for key, value in query.items() if value is not None}

    permission = get_permission(from_person, query, command)
    if not permission:
        raise PermissionError(
            "You don't have permission to execute this action"
        )

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


@authenticate_require
def transfer(value: int, to_email: str, from_person: Person, command: str):
    """Transfer points between users"""
    permission = get_permission(from_person=from_person, command=command)
    if not permission:
        raise PermissionError(
            "You don't have permission to execute this action"
        )

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


@authenticate_require
def movements(from_person: Person, command: str, **query: Query):
    """Show the movements from users."""
    query = {key: value for key, value in query.items() if value is not None}
    permission = get_permission(from_person, query, command)
    if not permission:
        raise PermissionError(
            "You don't have permission to execute this action"
        )

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
