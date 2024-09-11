import pytest

# Objeto `CliRunner` do módulo `testing` para realizar testes de integração
from click.testing import CliRunner

# Importando as funções que serão testadas
from dundie.cli import load, main

# Importando o caminho do arquivo de pessoas do arquivo de constantes
from .constants import PEOPLE_FILE

# Cria um objeto do tipo `CliRunner`, que permite através de uma interface,
# invocar comandos no terminal em um ambiente isolado para teste
cmd = CliRunner()


# Adicionando os markers `integration` e `medium` para o testea abaixo.
@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """Test command load."""
    # Invocando o comando load, passando seus parâmetros e coletando a saída
    out = cmd.invoke(load, PEOPLE_FILE)

    # Verificando se saída foi correta
    # Coleta a saída através do `output`
    assert "Dunder Mifflin Associates" in out.output


# Adicionando os markers `integration` e `medium` para o testea abaixo.
@pytest.mark.integration
@pytest.mark.medium
# Adicionando por meio de injeção de dependências
# uma lista de opções do comando `load`,
# que o teste vai executar.
@pytest.mark.parametrize("wrong_command", ["loady", "carrega", "start"])
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """Test command load."""
    # Invoca a função main para testar o subcomando `load`
    out = cmd.invoke(main, wrong_command, PEOPLE_FILE)

    # Verifica se a saída foi um erro
    assert out.exit_code != 0
    # Verifica se a saída da mensagem do erro foi correta
    assert f"No such command '{wrong_command}'." in out.output
