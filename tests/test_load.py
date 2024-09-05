import pytest
from dundie.core import load
from .constants import PEOPLE_FILE

# Aplica os marcadores `unit` e `high` para o teste abaixo.
@pytest.mark.unit
@pytest.mark.high
def test_load_positive_has_2_people():
    """Test load function."""
    assert len(load(PEOPLE_FILE)) == 2
    
# Aplica os marcadores `unit` e `high` para o teste
@pytest.mark.unit
@pytest.mark.high
def test_load_positive_has_first_name_starts_with_j():
    """Test load function."""
    assert load(PEOPLE_FILE)[0][0] == "J"