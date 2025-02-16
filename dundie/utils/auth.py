from functools import wraps
from getpass import getpass

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person, User
from dundie.utils.email import check_valid_email
from dundie.utils.errors import (
    AuthenticationError,
    InvalidEmailError,
    UserNotFoundError,
)


def authenticate_require(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
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

        return func(*args, from_person=user[0], **kwargs)

    return wrapper
