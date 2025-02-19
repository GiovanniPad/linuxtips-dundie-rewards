import os
from functools import wraps
from getpass import getpass

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person, User
from dundie.settings import ADMIN_EMAIL
from dundie.utils.email import check_valid_email
from dundie.utils.errors import (
    AuthenticationError,
    InvalidEmailError,
    UserNotFoundError,
)


def authenticate_require(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not os.getenv("AUTHENTICATED"):
            email = input("Email: ").strip()

            if not check_valid_email(email):
                raise InvalidEmailError(
                    f"{email} is not valid. Please insert a valid email."
                )

            sql = (
                select(Person, User.password)
                .join(User, Person.id == User.person_id)
                .where(Person.email == email)
            )

            with get_session() as session:
                user = session.exec(sql).first()

            if not user:
                raise UserNotFoundError("User not found.")

            password = getpass().strip()

            if not password == user[1]:
                raise AuthenticationError("Invalid credentials.")

            user = list(user)
            user.pop()

            os.environ["AUTHENTICATED"] = "yes"
            os.environ["AUTHENTICATED_USER"] = user[0].email
        else:
            email = os.getenv("AUTHENTICATED_USER")
            with get_session() as session:
                user = session.exec(
                    select(Person).where(Person.email == email)
                ).first()
            user = [user]

        command_name = func.__name__

        return func(*args, from_person=user[0], command=command_name, **kwargs)

    return wrapper


def get_permission(from_person: Person, query: dict[str], command):
    person_email = from_person.email
    person_role = from_person.role
    person_dept = from_person.dept

    query_dept = query.get("dept")
    query_email = query.get("email")

    admin_commands = ["load", "add"]

    if person_email == ADMIN_EMAIL:
        return True

    if query_dept and command not in admin_commands:
        if person_role == "Manager" and person_dept == query_dept:
            return True

    if query_email and command not in admin_commands:
        if person_role == "Manager":
            with get_session() as session:
                user_dept = session.exec(
                    select(Person.dept).where(Person.email == query_email)
                ).first()
            if user_dept == person_dept:
                return True
        if query_email == person_email:
            return True

    return False
