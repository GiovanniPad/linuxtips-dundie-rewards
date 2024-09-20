import pytest

from dundie.database import DB_SCHEMA, commit, connect


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
