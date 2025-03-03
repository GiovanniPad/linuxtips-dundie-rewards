from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import Annotated

from dundie.utils.email import check_valid_email
from dundie.utils.errors import InvalidEmailError
from dundie.utils.user import generate_simple_password


class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(
        nullable=False, index=True, sa_column_kwargs={"unique": True}
    )
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False, index=True)
    role: str = Field(nullable=False)
    currency: str = Field(default="USD", nullable=True)

    balance: "Balance" = Relationship(back_populates="person")
    movement: "Movement" = Relationship(back_populates="person")
    user: "User" = Relationship(back_populates="person")

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        if not check_valid_email(v):
            raise InvalidEmailError(f"Invalid email for {v!r}")

        return v


class Balance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(
        foreign_key="person.id", sa_column_kwargs={"unique": True}
    )
    value: Annotated[Decimal, Field(decimal_places=3, default=0)]

    person: Person = Relationship(back_populates="balance")

    @field_validator("value", mode="after")
    def value_logic(cls, v):
        return Decimal(v)


class Movement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(foreign_key="person.id")
    actor: str = Field(nullable=False, index=True)
    value: Annotated[Decimal, Field(decimal_places=3, default=0)]
    date: datetime = Field(default_factory=lambda: datetime.now())

    person: Person = Relationship(back_populates="movement")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    person_id: int = Field(
        foreign_key="person.id", sa_column_kwargs={"unique": True}
    )
    password: str = Field(default_factory=generate_simple_password)

    person: Person = Relationship(back_populates="user")
