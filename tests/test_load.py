import os
from uuid import uuid4
import pytest
from dundie.core import load
from .constants import PEOPLE_FILE

#def setup_module():
    #print("roda antes dos testes desse módulo")
#def teardown_module():
    #print("roda após os testes desse módulo")

# Cria uma fixture para todas as funções desse arquivo.
# `scope` determina o escopo para que essa fixture vai ser usada.
@pytest.fixture(scope="function")
def create_new_file(tmpdir):
    file_ = tmpdir.join("new_file.txt")
    file_.write("isso é sujeira...")
    yield
    file_.remove()


@pytest.mark.unit
@pytest.mark.high
def test_load(create_new_file, request):
    """Test load function."""
    
    filepath = f"arquivo_indesejado-{uuid4()}.txt"

    # Executa uma função qualquer após o término do teste.
    request.addfinalizer(lambda: os.unlink(filepath))

    with open(filepath, "w") as file_:
        file_.write("dados de teste")

    assert len(load(PEOPLE_FILE)) == 2
    assert load(PEOPLE_FILE)[0][0] == "J"