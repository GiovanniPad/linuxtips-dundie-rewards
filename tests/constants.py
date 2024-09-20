import os

# Caminho raiz do projeto.
from dundie.settings import ROOT_PATH

# Coletando o arquivo usado para os testes.
PEOPLE_FILE = os.path.join(ROOT_PATH, "..", "tests", "assets", "people.csv")
