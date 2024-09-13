import re

# `r` indica uma "raw string", não é formato usando a tabela de caracteres
# UTF-8, será salvo e passado da exata maneira que foi escrito.
regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


def check_valid_email(address):
    """Return True if email is valid."""
    return bool(re.fullmatch(regex, address))
