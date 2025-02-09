"""Core module of dundie"""

# Biblioteca usada para acessar funções do SO
import os

# Função da biblioteca `stdlib` para ler arquivos `csv`
from csv import reader

# Biblioteca que permite adicionar anotações de tipo para variáveis e funções
# Cada variável importada representa um tipo de dado
from typing import Any, Dict, List

# Funções do módulo para manipulação do banco de dados
from dundie.database import add_movement, add_person, commit, connect

# Modelo de dados que representa o saldo, movimentações e pessoas
from dundie.models import Balance, Movement, Person

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

        # Cria uma instância de Person para cada funcionário no arquivo csv
        # `person_data` é um dicionário e será desempacotado, por isso `**`
        # `pk` é a chave primária, para isso o email será usado e ao mesmo
        # tempo, o email será deletado dos dados da pessoa
        instance = Person(pk=person_data.pop("email"), **person_data)

        # Adiciona a instância da pessoa no banco de dados e retorna se foi
        # preciso criá-la ou não
        person, created = add_person(db, instance)

        # Converte a instância da classe Person para um dicionário,
        # no processo ele exclui desse dicionário a chave `pk`
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


# Função para ler dados do banco de dados com a possibilita de filtragem
# através do parâmetro `query`
# `query` é do tipo personalizado `Query`
# O retorno da função é do tipo personalizado `ResultDict`
def read(**query: Query) -> ResultDict:
    """Read data from db and filters using query"""

    # Filtra os valores vazios de cada par chave-valor
    # do dicionário de consulta
    query = {key: value for key, value in query.items() if value is not None}

    # Conecta no banco de dados
    db = connect()

    # Lista para armazenar os dados retornados
    return_data = []

    # Verifica se a chave email está dentro do dicionário `query`
    if "email" in query:
        # Atribui o email como chave primária e o remove do dicionário
        query["pk"] = query.pop("email")

    # Itera sobre a entidade Person do banco de dados,
    # filtrando os resultados com base na consulta `query`
    for person in db[Person].filter(**query):
        # Para cada pessoa retornada adiciona na lista `return_data` seus dados
        return_data.append(
            {
                # Indica a chave primária
                "email": person.pk,
                # Coleta o saldo do usuário através da `pk`
                # com a função `get_by_pk`
                "balance": db[Balance].get_by_pk(person.pk).value,
                # Coleta a última movimentação do usuário
                # Realiza o filtro pela `pk` coletando apenas a data com `date`
                "last_movement": db[Movement]
                .filter(person__pk=person.pk)[-1]
                .date,
                # Converte o modelo Person para um dicionário e exclui
                # a chave `pk` dele e então atribui no dicionário final
                **person.model_dump(exclude={"pk"}),
            }
        )

    # Retorna a lista com os usuários (dicionário)
    return return_data


# Função para adicionar pontos ao usuário no banco de dados
# `value` é do tipo int
# `query` é do tipo personalizado `Query`
def add(value: int, **query: Query):
    """Add value to each record on query."""

    # Filtrando os campos que são vazios da `query`
    query = {key: value for key, value in query.items() if value is not None}

    # Realiza a consulta no banco de dados usando a `query` como filtro
    people = read(**query)

    # Verifica se nenhum usuário foi encontrado
    if not people:
        raise RuntimeError("Not Found")

    # Conecta no banco de dados
    db = connect()
    # Coleta o nome do usuário do computador que está executando o script
    user = os.getenv("USER")

    # Itera sobre o dicionário `person`
    for person in people:
        # Para cada pessoa, cria uma instância pesquisando na entidade
        # Person do banco de dados atavés da `pk` usando o email
        instance = db[Person].get_by_pk(person["email"])

        # Com a instância adiciona a transação no banco de dados
        # Indicando o banco de dados `db`, o usuário a receber os pontos
        # `instance`, o valor que será adicionado `value` e o usuário que
        # está realizando a movimentação `user`
        add_movement(db, instance, value, user)

    # Confirma as alterações no banco de dados
    commit(db)
