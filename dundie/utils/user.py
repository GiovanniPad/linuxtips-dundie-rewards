# Módulo para gerar conjuntos aleatórios de um tamanho x
# a partir de um conjunto maior.
from random import sample

# `ascii_letters` é um módulo que contém
# todas as letras (maiúsculas e minúsculas) da tabela ASCII.
# `digits` contém todos os dígitos da tabela ASCII.
from string import ascii_letters, digits


# Função para criar uma senha aleatória, usando letras e dígitos
def generate_simple_password(size=8):
    """Generate a simple random password.
    regex: [A-Z][a-z][0-9]
    """
    password = sample(ascii_letters + digits, size)
    return "".join(password)
