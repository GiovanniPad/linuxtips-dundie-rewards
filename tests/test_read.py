# Biblioteca para testes unitários e de integração
import pytest

# Método para ler dados do banco de dados
from dundie.core import read

# Métodos para utilizar o banco de dados
from dundie.database import add_person, commit, connect

# Modelo de dados que representa uma Pessoa
from dundie.models import Person


# Marca o teste como unitário
@pytest.mark.unit
# Testa as querys de leitura do banco de dados
def test_read_with_query():
    # Dados fictícios
    pk = "joe@doe.com"
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}

    # Conecta no banco de dados
    db = connect()

    # Cria e adiciona uma pessoa no banco de dados
    _, created = add_person(db, Person(pk=pk, **data))
    # Verifica se a pessoa foi criada com sucesso
    assert created is True

    # Dados fictícios
    pk = "jim@doe.com"
    data = {"name": "Jim Doe", "role": "Manager", "dept": "Management"}

    # Cria e adiciona uma pessoa no banco de dados
    _, created = add_person(db, Person(pk=pk, **data))
    # Verifica se a pessoa foi criada com sucesso
    assert created is True

    # Confirma as alterações no banco de dados
    commit(db)

    # Pesquisa todos os usuários do banco de dados
    response = read()

    # Compara com a quantidade adicionada anteriormente neste teste
    assert len(response) == 2

    # Pesquisa os usuários com o departmento = "Management"
    response = read(dept="Management")

    # Compara com a quantia esperada de usuários do departamento buscado
    assert len(response) == 1
    # Compara se é o usuário correto
    assert response[0]["name"] == "Jim Doe"

    # Pesquisa um usuário pelo email = "joe@doe.com"
    response = read(email="joe@doe.com")

    # Compara com a quantia esperada de usuários com este email
    assert len(response) == 1
    # Verifica se o usuário está correto
    assert response[0]["name"] == "Joe Doe"
