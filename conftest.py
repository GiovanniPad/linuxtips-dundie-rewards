from unittest.mock import patch
import pytest
from sqlmodel import create_engine
from dundie import models

MARKER = """\
unit: Mark unit tests
integration: Mark integration tests
high: High Priority
medium: Medium Priority
low: Low Priority
"""


# Função que é executada automaticamente quando o Pytest é executado.
def pytest_configure(config):
    for line in MARKER.split("\n"):
        # Adiciona a configuração do pytest no arquivo de configuração.
        config.addinivalue_line("markers", line)


# Define uma fixture para criar um diretório temporário
# para os side effects dos testes.
# `autouse` define que todos os testes desse projeto vão utilizar essa fixture.
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):  # injeção de dependências

    # Instância a fixture `tmpdir` para criar um
    # diretório temporário para testes.
    tmpdir = request.getfixturevalue("tmpdir")

    # Altera o diretório usado `cwd - Current Working Directory`
    # para o de teste.
    with tmpdir.as_cwd():
        yield  # protocolo de generators


# Fixture para criar um banco de dados temporário para testes,
# é aplicada automaticamente (`autouse`) para cada função de teste (`scope`).
@pytest.fixture(autouse=True, scope="function")
def setup_testing_database(request):
    """For each test, create a database file on tmpdir
    force database.py to use that filepath.
    """

    # Instância a fixture `tmpdir` para criar um
    # diretório temporário para o banco de dados.
    tmpdir = request.getfixturevalue("tmpdir")

    # Coleta o filepath para o arquivo de banco de dados de testes.
    test_db = str(tmpdir.join("database.test.db"))

    engine = create_engine(f"sqlite:///{test_db}")

    models.SQLModel.metadata.create_all(bind=engine)

    # Aplica essa fixture para todas as vezes que a
    # variável `DATABASE_PATH` for utilizada no programa.
    # É utilizado a técnica mocking para substituir temporariamente o filepath
    # principal do banco de dados pelo o filepath de testes.
    with patch("dundie.database.engine", engine):
        yield
