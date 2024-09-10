"""Core module of dundie"""

from dundie.utils.log import get_logger

log = get_logger()


# Função para carregar dados.
# Chamada ao ser passada para o argumento `subcommand` o valor "load".
def load(filepath):
    """Loads data from filepath to the database

    >>> len(load('assets/people.csv'))
    2
    >>> load('assets/people.csv')[0][0]
    'J'
    """
    try:
        with open(filepath) as file_:
            return [line.strip() for line in file_.readlines()]
    except FileNotFoundError as e:
        log.error(str(e))
        raise e
