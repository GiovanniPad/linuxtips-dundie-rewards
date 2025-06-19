import keyring
from functools import wraps
from sqlmodel import select
from dundie.database import get_session
from dundie.models import Person
import click
from dundie.settings import ADMIN_EMAIL, KEYRING_USERNAME, KEYRING_SERVICE_NAME


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logged = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
        if logged:
            with get_session() as session:
                sql = select(Person).where(Person.email == logged)
                user = session.exec(sql).first()

                if not user:
                    click.secho(
                        "User doesn't exists! Try login again", fg="red"
                    )
                    exit()

                permission = get_permission(user, kwargs, func.__name__)

                if not permission:
                    click.secho(
                        "You don't have permission to use this command",
                        fg="red",
                    )
                    exit()

                return func(*args, from_person=user, **kwargs)
        else:
            click.secho(
                "You need to be logged in to use this command!", fg="red"
            )
            exit()

    return wrapper


def get_permission(
    from_person: Person, query: dict[str] = {}, command: str = None
):
    person_email = from_person.email
    person_role = from_person.role
    person_dept = from_person.dept

    query_dept = query.get("dept")
    query_email = query.get("email")

    admin_commands = ["load", "add"]

    if person_email == ADMIN_EMAIL or command == "transfer":
        return True

    if (
        query_dept
        and (command not in admin_commands)
        and (person_role == "Manager")
        and (person_dept == query_dept)
    ):
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
