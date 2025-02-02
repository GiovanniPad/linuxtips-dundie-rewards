"""Core module of dundie"""

import os

# Função da biblioteca stdlib para ler arquivos .csv.
from csv import reader
from typing import Any, Dict, List

# Funções para do módulo para manipulação do banco de dados.
from dundie.database import add_movement, add_person, commit, connect
from dundie.models import Balance, Movement, Person

# Função do módulo de log para definir um logger.
from dundie.utils.log import get_logger

# Definindo um logger personalizado e atribuindo-o a uma variável.
log = get_logger()
Query = Dict[str, Any]
ResultDict = List[Dict[str, Any]]


# Função para carregar dados.
# Chamada ao ser passada para o argumento `subcommand` o valor "load".
def load(filepath: str) -> ResultDict:
    """Loads data from filepath to the database

    >>> len(load('assets/people.csv'))
    2
    >>> load('assets/people.csv')[0][0]
    'J'
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

    # Conecta no banco de dados
    db = connect()
    # Cria uma lista de pessoas vazia que será usada para exibir no console.
    people = []
    # Lista que contêm o cabeçalho/colunas de dados.
    headers = ["name", "dept", "role", "email"]

    # Para cada linha do arquivo de dados (JSON).
    for line in csv_data:
        # Função `zip` vai juntar as colunas com os seus respectivos dados,
        # para isso será usado uma list comprehension que percorre cada item
        # na linha e também retira os espaços em branco.
        # Função `dict` converte o objeto zip para um dicionário e
        # armazena numa variável.
        person_data = dict(zip(headers, [item.strip() for item in line]))

        instance = Person(pk=person_data.pop("email"), **person_data)

        person, created = add_person(db, instance)
        return_data = person.model_dump(exclude={"pk"})

        # Insere na cópia dos dados a informação se ela foi criada ou não.
        return_data["created"] = created
        # Reinsere na cópia dos dados seu email (chave primária).
        return_data["email"] = person.pk
        # Adiciona a cópia dos dados dessa pessoa na lista vazia de exibição.
        people.append(return_data)

    # Confirma as mudanças no banco de dados.
    commit(db)
    # Retorna a lista para exibir os dados das pessoas no console.
    return people


def read(**query: Query) -> ResultDict:
    """Read data from db and filters using query"""
    query = {k: v for k, v in query.items() if v is not None}
    db = connect()
    return_data = []

    if "email" in query:
        query["pk"] = query.pop("email")

    for person in db[Person].filter(**query):
        return_data.append(
            {
                "email": person.pk,
                "balance": db[Balance].get_by_pk(person.pk).value,
                "last_movement": db[Movement]
                .filter(person__pk=person.pk)[-1]
                .date,
                **person.model_dump(exclude={"pk"}),
            }
        )
    return return_data


def add(value: int, **query: Query):
    """Add value to each record on query."""
    query = {k: v for k, v in query.items() if v is not None}
    people = read(**query)

    if not people:
        raise RuntimeError("Not Found")

    db = connect()
    user = os.getenv("USER")

    for person in people:
        instance = db[Person].get_by_pk(person["email"])
        add_movement(db, instance, value, user)

    commit(db)
