import pytest

# Importando módulos(funções) a serem testados
from dundie.utils.email import check_valid_email
from dundie.utils.user import generate_simple_password


# Marcando o teste como do tipo `unit` (unidade).
@pytest.mark.unit
# Passa uma lista como parâmetro por meio de injeção de dependência,
# com isso é possível executar o mesmo teste para todos os valores dessa lista,
# economizando código.
@pytest.mark.parametrize(
    "address", ["bruno@rocha.com", "joe@doe.com", "a@b.pt"]
)
def test_positive_check_valid_email(address):
    """Ensure email is valid."""
    assert check_valid_email(address) is True


# Marca o teste como do tipo `unit` (unidade).
@pytest.mark.unit
# Lista de valores que vão ser usados para executar os testes.
@pytest.mark.parametrize("address", ["bruno@.com", "@doe.com", "a@b"])
def test_negative_check_valid_email(address):
    """Ensure email is valid."""
    assert check_valid_email(address) is False


# Marca o teste como do tipo `unit` (unidade).
@pytest.mark.unit
# Testa a geração de senhas simples
def test_generate_simple_password():
    """Test generation of random simple passwords.
    TODO: Generate hashed complex passwords, encrypit it
    """
    # Lista para armazenar as senhas criadas
    passwords = []

    # Cria 100 senhas distintas e armazena na lista criada anteriormente
    for _ in range(100):
        passwords.append(generate_simple_password(8))

    # Imprime todas as senhas
    print(passwords)

    # Verifica se a quantidade certa de senhas foi gerada
    assert len(set(passwords)) == 100
