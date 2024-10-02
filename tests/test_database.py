import pytest

# Dados do módulo de `database` para realizar os testes.
from dundie.database import (
    DB_SCHEMA,
    add_movement,
    add_person,
    commit,
    connect,
)


# Teste de unidade para verificar se o schema (esquema)
# do banco de dados está correto.
@pytest.mark.unit
def test_database_schema():
    db = connect()
    assert db.keys() == DB_SCHEMA.keys()


# Teste de unidade para verificar se a função `commit` está
# atualizando os dados.
@pytest.mark.unit
def test_commit_to_database():

    # Coleta o banco de dados.
    db = connect()

    # Cria uma pessoa fictícia para teste.
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}

    # Insere os dados da pessoa fictícia na tabela.
    db["people"]["joe@doe.com"] = data

    # Confirma as modificações.
    commit(db)

    # Coleta novamente o banco de dados e verifica se
    # a mudança foi feita com sucesso com base nos dados fictícios.
    db = connect()
    assert db["people"]["joe@doe.com"] == data


# Teste de unidade para verificar se a pessoa está sendo adicionada
# ao banco de dados corretamente.
@pytest.mark.unit
def test_add_person_for_the_first_time():
    # Dados fictícios para teste.
    pk = "joe@doe.com"
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}

    # Conecta no banco de dados.
    db = connect()

    # Adiciona o usuário fictício no banco de dados e coleta a informação
    # se ele foi criado pela primeira vez ou não.
    _, created = add_person(db, pk, data)

    # Verifica se o usuário foi criado.
    assert created is True

    # Confirma as mudanças no banco de dados.
    commit(db)

    # Conecta novamente no banco de dados.
    db = connect()

    # Verifica se os dados inseridos no banco de dados batem com os
    # dados fictícios.
    assert db["people"][pk] == data
    # Verifica se o balanço inicial do usuário foi definido corretamente.
    assert db["balance"][pk] == 500
    # Verifica se o usuário possui alguma movimentação, é para possuir 1,
    # a de adicionar o balanço inicial dele.
    assert len(db["movement"][pk]) > 0
    # Verifica se o valor dessa movimentação é de 500, que é o valor correto.
    assert db["movement"][pk][0]["value"] == 500


# Teste unitário para verificar se o email inserido é inválido.
@pytest.mark.unit
def test_negative_add_person_invalid_email():
    # Abre um gerenciador de contexto para verificar se o erro `ValueError`
    # vai ocorrer no bloco de código.
    with pytest.raises(ValueError):
        # Testa a inserção de dados que vai gerar um erro `ValueError`.
        add_person({}, ".@bla", {})


@pytest.mark.unit
def test_add_or_remove_points_for_person():
    pk = "joe@doe.com"
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}
    db = connect()
    _, created = add_person(db, pk, data)
    assert created is True
    commit(db)

    db = connect()
    before = db["balance"][pk]

    add_movement(db, pk, -100, "manager")
    commit(db)

    db = connect()
    after = db["balance"][pk]

    assert after == before - 100
    assert after == 400
    assert before == 500
