import pytest

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

# Define uma fixture para criar um diretório temporário para side effects dos testes.
# `autouse` define que todos os testes desse projeto vão utilizar essa fixture.
@pytest.fixture(autouse=True)
def go_to_tmpdir(request): # injeção de dependências
    # Cria um diretório temporário para cada teste do projeto.
    tmpdir = request.getfixturevalue("tmpdir")
    # cwd = change working directory
    with tmpdir.as_cwd():
        yield # protocolo de generators