# Biblioteca para realizar testes.
import pytest

# Função `load` do módulo core.
from dundie.core import load
from dundie.database import EMPTY_DB, ORM, connect

# Arquivo de teste que contém os dados dos usuários.
from .constants import PEOPLE_FILE


# Teste para verificar se foi lido todos os dados dos usuários do arquivo.
# Aplica os marcadores `unit` e `high` para o teste abaixo.
@pytest.mark.unit
@pytest.mark.high
def test_load_positive_has_2_people():
    """Test load function."""
    # Verifica se todos os usuários (2) foram lidos do arquivo.
    assert len(load(PEOPLE_FILE)) == 2


# Marca o teste como de unidade
@pytest.mark.unit
# Marca o teste como de alta prioridade
@pytest.mark.high
# Testa o esquema do banco de dados
def test_db_schema():
    # Carrega os dados no banco de dados
    load(PEOPLE_FILE)

    # Conecta no banco de dados
    db = connect()

    # Coleta e armazena os nomes das tabelas do banco de dados
    db_keys = {ORM.get_table_name(model) for model in db}

    # Verifica se os nomes das tabelas são iguais os nomes do esquema do banco
    assert db_keys == EMPTY_DB.keys()


# Teste unitário para verificar se o primeiro nome do primeiro usuário
# é "Jim Halpert".
# Aplica os marcadores `unit` e `high` para o teste
@pytest.mark.unit
@pytest.mark.high
def test_load_positive_first_name_is_jim_halpert():
    """Test load function."""
    # Verifica se o nome do primeiro usuário inserido é `Jim Halpert`.
    assert load(PEOPLE_FILE)[0]["name"] == "Jim Halpert"
