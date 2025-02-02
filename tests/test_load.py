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


@pytest.mark.unit
@pytest.mark.high
def test_db_schema():
    load(PEOPLE_FILE)
    db = connect()
    db_keys = {ORM.get_table_name(model) for model in db}
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
