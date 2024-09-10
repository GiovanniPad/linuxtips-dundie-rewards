# Função da biblioteca subprocess para executar comandos CLI
# do SO e o resultado do comando vem como binário.
from subprocess import CalledProcessError, check_output

import pytest


# Adicionando os markers `integration` e `medium` para o testea abaixo.
@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """Test command load."""
    out = (
        check_output(["dundie", "load", "tests/assets/people.csv"])
        .decode("utf-8")
        .split("\n")
    )

    assert len(out) == 2


# Adicionando os markers `integration` e `medium` para o testea abaixo.
@pytest.mark.integration
@pytest.mark.medium
# Adicionando por meio de injeção de dependências
# uma lista de opções do comando `load`,
# que o teste vai executar.
@pytest.mark.parametrize("wrong_command", ["loady", "carrega", "start"])
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """Test command load."""
    with pytest.raises(CalledProcessError) as error:
        (
            check_output(["dundie", wrong_command, "tests/assets/people.csv"])
            .decode("utf-8")
            .split("\n")
        )

    assert "status 2" in str(error.getrepr())
