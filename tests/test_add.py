# Biblioteca para realizar testes unitários
import pytest

# Método para adicionar movimentações para o usuário
from dundie.core import add

# Métodos para usar o banco de dados e adicionar uma pessoa
from dundie.database import add_person, commit, connect

# Modelos de dados que representa o saldo e a pessoa
from dundie.models import Balance, Person


# Decorator para marcar como teste unitário
@pytest.mark.unit
# Testar a adição e exclusão de pontos em um usuário
def test_add_movement():
    # Dados fictícios
    pk = "joe@doe.com"
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}

    # Conecta no banco de dados
    db = connect()

    # Cria e adiciona o usuário no banco
    _, created = add_person(db, Person(pk=pk, **data))
    # Verifica se o usuário foi adicionado com sucesso
    assert created is True

    # Dados fictícios
    pk = "jim@doe.com"
    data = {"name": "Jim Doe", "role": "Manager", "dept": "Management"}

    # Cria e insere outro usuário no banco
    _, created = add_person(db, Person(pk=pk, **data))
    # Verifica se o usuário foi adicionado com sucesso
    assert created is True

    # Confirma as atualizações
    commit(db)

    # Adiciona e remove pontos com base no email e no departamento
    add(-30, email="joe@doe.com")
    add(90, dept="Management")

    # Conecta no banco de dados
    db = connect()

    # Verifica se as alterações foram feitas com sucesso
    assert db[Balance].get_by_pk("joe@doe.com").value == 470
    assert db[Balance].get_by_pk("jim@doe.com").value == 190
