from decimal import Decimal
from typing import Optional, cast

from sqlmodel import Session, select

from dundie.database import get_session
from dundie.models import Balance, Movement, Person, User
from dundie.settings import EMAIL_FROM
from dundie.utils.email import send_email

session = get_session()


def add_person(session: Session, instance: Person):
    """Saves person data to database.

    - Email is unique (resolved by dictionary hash table)
    - If exists, update, else create
    - Set initial balance (managers = 100, others = 500)
    - Generate a password if user is new and send email
    """
    existing = session.exec(
        select(Person).where(Person.email == instance.email)
    ).first()

    created = existing is None

    if created:
        session.add(instance)
        set_initial_balance(session, instance)

        password = set_initial_password(session, instance)

        # TODO: encrypt and send only link not raw password
        # TODO: Usar sistema de filas (conteúdo extra)
        send_email(
            EMAIL_FROM, instance.email, "Your dundie password", password
        )

        return instance, created
    else:
        instance = cast(Person, instance)
        existing = cast(Person, existing)

        existing.dept = instance.dept
        existing.role = instance.role
        session.add(existing)

        return instance, created


# Função para criar uma senha inicial para um novo usuário.
def set_initial_password(session: Session, instance: Person) -> str:
    """Generated and saves password."""
    user = User(person=instance)
    session.add(user)
    return user.password


# Função para definir o balanço de pontos inicial.
def set_initial_balance(session: Session, person: Person):
    """Add movement and set initial balance"""
    # Adiciona 100 pontos se a pessoa tiver o cargo `Manager`
    # e adiciona 500 pontos para os outros cargos
    value = 100 if person.role == "Manager" else 500

    # Adiciona essa transação de pontos a seu histórico de transações
    add_movement(session, person, Decimal(value))


# Função para criar uma movimentação de saldo
def add_movement(
    session: Session,
    person: Person,
    value: Decimal,
    actor: Optional[str] = "system",
):
    """Adds movement to user account."""

    if not person.id:
        movement = Movement(person=person, actor=actor, value=value)
    else:
        movement = Movement(person_id=person.id, actor=actor, value=value)

    session.add(movement)

    movements = session.exec(select(Movement).where(Movement.person == person))

    total = Decimal(sum([mov.value for mov in movements]))

    existing_balance = session.exec(
        select(Balance).where(Balance.person == person)
    ).first()
    if existing_balance:
        existing_balance.value = total
        session.add(existing_balance)
    else:
        session.add(Balance(person=person, value=total))
