# Biblioteca Pydantic para realizar a serialização
# e desserialização e validações
# Biblioteca para representar datas e horas
from datetime import datetime

# Biblioteca para representar o tipo de dado `Decimal`
from decimal import Decimal
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import Annotated

# Função para validar emails do módulo `email`
from dundie.utils.email import check_valid_email
from dundie.utils.user import generate_simple_password


# Classe personalizada de erro
class InvalidEmailError(Exception):
    pass


# Classe para representar a entidade Person do banco de dados
# Ela extende de `SQLModel` do Pydantic com o objetivo de acessar
# os métodos responsáveis por validações, serializações e desserializações
class Person(SQLModel, table=True):
    # Atributos e seus tipo de dados
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

    # Decorator para indicar que o atributo `pk` vai ser validado,
    # a sua validação ocorre depois da criação da instância da classe
    @field_validator("email")
    # Método usado para realizar a validação do email
    # Recebe dois parâmetros por injeção de dependência
    def validate_email(cls, v: str) -> str:
        # Valida o email
        if not check_valid_email(v):
            # Estoura um erro se o email não for válido
            # `!r` coloca aspas simples em volta do valor a ser exibido
            raise InvalidEmailError(f"Invalid email for {v!r}")
        # Retorna o valor, caso for válido
        return v


# Classe para representar a entidade Balance do banco de dados
# Também herda de `SQLModel` para usar as funcionalidades do Pydantic
class Balance(SQLModel, table=True):
    # Atributos e seus tipos de dados
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(
        foreign_key="person.id", sa_column_kwargs={"unique": True}
    )
    value: Annotated[Decimal, Field(decimal_places=3, default=0)]

    person: Person = Relationship(back_populates="balance")

    # Decorator para validar o atributo `value`,
    # porém essa validação ocorre antes de instanciar a classe
    @field_validator("value", mode="after")
    def value_logic(cls, v):
        return Decimal(v)


# Classe para representar a entidade `Movement` do banco de dados
# Também herda de `SQLModel` para usar as funcionalidades do Pydantic
class Movement(SQLModel, table=True):
    # Atributos e seus tipos de dados
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(foreign_key="person.id")
    actor: str = Field(nullable=False, index=True)
    value: Annotated[Decimal, Field(decimal_places=3, default=0)]
    date: datetime = Field(default_factory=lambda: datetime.now())

    person: Person = Relationship(back_populates="movement")


# Classe para representar a entidade `User` do banco de dados
# Também herda de `SQLModel` para usar as funcionalidades do Pydantic
class User(SQLModel, table=True):
    # Atributos e seus tipos de dados
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    # Permite configurável o atributo, neste caso `default_factory` executa
    # por padrão a função `generate_simple_password` para toda instância
    person_id: int = Field(
        foreign_key="person.id", sa_column_kwargs={"unique": True}
    )
    password: str = Field(default_factory=generate_simple_password)

    person: Person = Relationship(back_populates="user")
