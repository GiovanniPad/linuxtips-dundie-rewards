# Biblioteca para tratar arquivos do tipo JSON.
import json

# Biblioteca para data e hora.
from datetime import datetime

# Importanto informações e funções necessárias.
from dundie.settings import DATABASE_PATH, EMAIL_FROM
from dundie.utils.email import check_valid_email, send_email
from dundie.utils.user import generate_simple_password

# Criando o schema (esquema) do "banco de dados".
DB_SCHEMA = {"people": {}, "balance": {}, "movement": {}, "user": {}}


# Função para conectar com o banco de dados e
# cria um objeto contendo os dados.
def connect() -> dict:
    """Connects to the database, returns dict data"""
    try:
        # Abre e lê o arquivo JSON (banco de dados).
        with open(DATABASE_PATH, "r") as database_file:
            # Transforma o objeto JSON em um objeto Python (dict) e o retorna.
            return json.loads(database_file.read())

    # Captura as possíveis exceções.
    # `JSONDecodeError` ocorre caso o arquivo esteja vazio.
    except (json.JSONDecodeError, FileNotFoundError):
        # Retorna o banco vazio caso ocorra um erro.
        return DB_SCHEMA


# Função para salvar as mudanças no banco de dados (JSON).
def commit(db):
    """Save db back to the database file."""
    # Verifica se o esquema (schema) do banco de dados está modificado,
    # caso estiver, retorna um erro.
    if db.keys() != DB_SCHEMA.keys():
        raise RuntimeError("Database Schema is invalid.")

    # Abre o arquivo JSON (Banco de dados) no modo de escrita e
    # salva as modificações.
    with open(DATABASE_PATH, "w") as database_file:
        database_file.write(json.dumps(db, indent=4))


# Função para adicionar uma pessoa ao banco de dados (arquivo JSON).
def add_person(db, pk, data):
    """Saves person data to database.

    - Email is unique (resolved by dictionary hash table)
    - If exists, update, else create
    - Set initial balance (managers = 100, others = 500)
    - Generate a password if user is new and send email
    """

    # Verifica se o e-mail é válido.
    if not check_valid_email(pk):
        raise ValueError(f"{pk} is not a valid email")

    # Coleta a tabela de pessoas.
    table = db["people"]

    # Coleta os dados da pessoa a ser inserida para validação,
    # caso existir essa pessoa, o retorna, senão, retorna um dicionário vazio.
    person = table.get(pk, {})

    # Verifica se a pessoa já existe no banco de dados.
    # Caso exista, False, caso não existe, True.
    created = not bool(person)

    # Atualiza os dados modificados do registro da pessoa.
    person.update(data)

    # Passa o objeto modificado para a tabela.
    table[pk] = person

    # Caso for a primeira vez que a pessoa estiver sendo registrada.
    if created:
        # Atribui um saldo inicial de pontos.
        set_initial_balance(db, pk, person)

        # Atribui a variável a senha inicial gerada do usuário.
        password = set_initial_password(db, pk)

        # Envia um e-mail contendo a senha gerada.
        send_email(EMAIL_FROM, pk, "Your dundie password", password)
        # TODO: encrypt and send only link not raw password

    # Retorna os dados atualizados da pessoa e se foi criado um registro novo.
    return person, created


# Função para criar uma senha inicial para um novo usuário.
def set_initial_password(db, pk):
    """Generated and saves password."""
    # Coleta o email do usuário (chave primária), senão encontrar
    # retorna um dicionário vazio por padrão.
    db["user"].setdefault(pk, {})
    # Gera uma senha para o usuário e atribui aos seus dados no banco de dados.
    db["user"][pk]["password"] = generate_simple_password(8)
    # Retorna a senha criada
    return db["user"][pk]["password"]


# Função para definir o balanço de pontos inicial.
def set_initial_balance(db, pk, person):
    """Add movement and set initial balance"""

    # Para "Manager" = 500 pontos
    # Para "Outros" = 100 pontos
    value = 100 if person["role"] == "Manager" else 500

    # Cria uma movimentação de saldo para aquela pessoa,
    # referente aos pontos adicionados.
    add_movement(db, pk, value)


# Função para criar uma movimentação de saldo
def add_movement(db, pk, value, actor="system"):
    # Coleta todas as movimentações da pessoa em questão,
    # caso não tiver nenhuma movimentação, retorna uma lista vazia.

    # Função `setdefault` procura uma chave no dicionário,
    # senão encontrar nenhuma, retorna uma lista vazia (objeto padrão).
    movements = db["movement"].setdefault(pk, [])

    # Adiciona a nova movimentação para a lista de movimentações da pessoa.
    movements.append(
        {"date": datetime.now().isoformat(), "actor": actor, "value": value}
    )

    # Atualiza o saldo de pontos da pessoa.
    db["balance"][pk] = sum([item["value"] for item in movements])
