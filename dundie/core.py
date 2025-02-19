"""Core module of dundie"""

import os
from csv import reader
from decimal import Decimal
from typing import Any, Dict, List, cast

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Movement, Person
from dundie.settings import DATEFMT
from dundie.utils.auth import authenticate_require, get_permission
from dundie.utils.db import add_movement, add_person
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

    if not people:
        raise RuntimeError("Not Found")

    with get_session() as session:
        user = os.getenv("USER")

        for person in people:
            instance = session.exec(
                select(Person).where(Person.email == person["email"])
            ).first()

            add_movement(session, cast(Person, instance), value, user)

        session.commit()
