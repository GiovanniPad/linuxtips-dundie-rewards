"""Core module of dundie"""

# Biblioteca usada para acessar funções do SO
import os

# Função da biblioteca `stdlib` para ler arquivos `csv`
from csv import reader
from decimal import Decimal

# Biblioteca que permite adicionar anotações de tipo para variáveis e funções
# Cada variável importada representa um tipo de dado
from typing import Any, Dict, List, cast

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Movement, Person
from dundie.settings import DATEFMT
from dundie.utils.db import add_movement, add_person

# Função do módulo de log para definir um logger
from dundie.utils.log import get_logger

# Definindo um logger personalizado e atribuindo-o a uma variável
log = get_logger()

# Definindo anotações de tipo personalizadas, combinações de outros tipos
Query = Dict[str, Any]
ResultDict = List[Dict[str, Any]]


# Função para carregar dados no banco de dados
# Chamada ao ser passada para o argumento `subcommand` o valor "load"
# `filepath` é do tipo string
# O retorno da função é do tipo ResultDict
def load(filepath: str) -> ResultDict:
    """Loads data from filepath to the database

    >>> len(load('assets/people.csv'))
    2
    """
    # Tratando erro caso o arquivo de banco de dados (JSON)
    # não for encontrado.
    try:
        # Lê o arquivo .csv (banco de dados) e atribui seu conteúdo
        # em uma variável
        csv_data = reader(open(filepath))

    # Tratando o erro FileNotFoundError
    except FileNotFoundError as e:
        # Imprime uma mensagem de log e invoca um erro.
        log.error(str(e))
        raise e

    # Cria uma lista de pessoas vazia que será usada para exibir no console.
    people = []
    # Lista que contêm o cabeçalho/colunas de dados.
    headers = ["name", "dept", "role", "email"]

    # Conecta no banco de dados
    with get_session() as session:
        # Para cada linha do arquivo de dados (JSON).
        for line in csv_data:
            # Função `zip` vai juntar as colunas com os seus respectivos dados,
            # para isso será usado uma list comprehension que percorre cada
            # item na linha e também retira os espaços em branco.
            # Função `dict` converte o objeto zip para um dicionário e
            # armazena numa variável.
            person_data = dict(zip(headers, [item.strip() for item in line]))

            instance = Person(**person_data)

            person, created = add_person(session, instance)

            # Converte a instância da classe Person para um dicionário,
            # no processo ele exclui desse dicionário a chave `pk`
            return_data = person.model_dump(exclude={"id"})

            # Insere na cópia dos dados a informação se ela foi criada ou não.
            return_data["created"] = created
            # Adiciona a cópia dos dados dessa
            # pessoa na lista vazia de exibição.
            people.append(return_data)

        # Confirma as mudanças no banco de dados.
        session.commit()
    # Retorna a lista para exibir os dados das pessoas no console.
    return people


# Função para ler dados do banco de dados com a possibilita de filtragem
# através do parâmetro `query`
# `query` é do tipo personalizado `Query`
# O retorno da função é do tipo personalizado `ResultDict`
def read(**query: Query) -> ResultDict:
    """Read data from db and filters using query"""

    # Filtra os valores vazios de cada par chave-valor
    # do dicionário de consulta
    query = {key: value for key, value in query.items() if value is not None}

    # Lista para armazenar os dados retornados
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

        results = session.exec(sql)

        for person in results:
            # Para cada pessoa retornada adiciona na
            # lista `return_data` seus dados

            movements = session.exec(
                select(Movement).where(Movement.person_id == person.id)
            ).all()

            return_data.append(
                {
                    "email": person.email,
                    "balance": person.balance.value,
                    "last_movement": movements[-1].date.strftime(DATEFMT),
                    **person.model_dump(exclude={"id"}),
                }
            )

    return return_data


# Função para adicionar pontos ao usuário no banco de dados
# `value` é do tipo int
# `query` é do tipo personalizado `Query`
def add(value: Decimal, **query: Query):
    """Add value to each record on query."""

    # Filtrando os campos que são vazios da `query`
    query = {key: value for key, value in query.items() if value is not None}

    # Realiza a consulta no banco de dados usando a `query` como filtro
    people = read(**query)

    # Verifica se nenhum usuário foi encontrado
    if not people:
        raise RuntimeError("Not Found")

    with get_session() as session:
        # Coleta o nome do usuário do computador que está executando o script
        user = os.getenv("USER")

        # Itera sobre o dicionário `person`
        for person in people:
            # Para cada pessoa, cria uma instância pesquisando na entidade
            # Person do banco de dados atavés da `pk` usando o email
            instance = session.exec(
                select(Person).where(Person.email == person["email"])
            ).first()

            # Com a instância adiciona a transação no banco de dados
            # Indicando o banco de dados `db`, o usuário a receber os pontos
            # `instance`, o valor que será adicionado `value` e o usuário que
            # está realizando a movimentação `user`
            add_movement(session, cast(Person, instance), value, user)

        session.commit()
