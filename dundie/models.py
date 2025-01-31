# Biblioteca Pydantic para realizar a serialização
# e desserialização e validações
# Biblioteca para representar datas e horas
from datetime import datetime

# Biblioteca para representar o tipo de dado `Decimal`
from decimal import Decimal

from pydantic import BaseModel, field_validator

# Função para validar emails do módulo `email`
from dundie.utils.email import check_valid_email


# Classe personalizada de erro
class InvalidEmailError(Exception):
    pass


# Classe para representar a entidade Person do banco de dados
# Ela extende de `BaseModel` do Pydantic com o objetivo de acessar
# os métodos responsáveis por validações, serializações e desserializações
class Person(BaseModel):
    # Atributos e seus tipo de dados
    pk: str
    name: str
    dept: str
    role: str

    # Decorator para indicar que o atributo `pk` vai ser validado,
    # a sua validação ocorre depois da criação da instância da classe
    @field_validator("pk")
    # Método usado para realizar a validação do email
    # Recebe dois parâmetros por injeção de dependência
    def validate_email(cls, v):
        # Valida o email
        if not check_valid_email(v):
            # Estoura um erro se o email não for válido
            # `!r` coloca aspas simples em volta do valor a ser exibido
            raise InvalidEmailError(f"Invalid email for {v!r}")
        # Retorna o valor, caso for válido
        return v

    # Sobrescrevendo o método interno para mudar a forma
    # como a classe é exibido ao utilizar `print`
    def __str__(self):
        return f"{self.name} - {self.role}"


# Classe para representar a entidade Balance do banco de dados
# Também herda de `BaseModel` para usar as funcionalidades do Pydantic
class Balance(BaseModel):
    # Atributos e seus tipos de dados
    person: Person
    value: Decimal

    # Decorator para validar o atributo `value`,
    # porém essa validação ocorre antes de instanciar a classe
    @field_validator("value", mode="after")
    def value_logic(cls, v):
        return Decimal(v) * 2

    # Classe interna para configurar como é a representação do JSON
    # dos atributos da classe principal
    class Config:
        # Define que o atributi `person` será um objeto que exibirá apenas
        # o atributo `nome`, para isso é necessário passar uma função
        json_encoders = {Person: lambda p: p.name}


# Classe para representar a entidade `Movement` do banco de dados
# Também herda de `BaseModel` para usar as funcionalidades do Pydantic
class Movement(BaseModel):
    # Atributos e seus tipos de dados
    person: Person
    date: datetime
    actor: str
    value: Decimal
