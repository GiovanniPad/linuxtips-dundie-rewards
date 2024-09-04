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