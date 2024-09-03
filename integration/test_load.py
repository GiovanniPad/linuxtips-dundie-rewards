import pytest
# Função da biblioteca subprocess para executar comandos CLI
# do SO e o resultado do comando vem como binário.
from subprocess import check_output

@pytest.mark.integration
@pytest.mark.medium
def test_load():
    """Test command load."""
    out = check_output(
        ["dundie", "load", "tests/assets/people.csv"]
    ).decode("utf-8").split("\n")
    
    assert len(out) == 2

