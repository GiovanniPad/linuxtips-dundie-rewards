"""Core module of dundie"""

# Função da biblioteca stdlib para ler arquivos .csv.
from csv import reader

# Funções para do módulo para manipulação do banco de dados.
from dundie.database import add_person, commit, connect

# Função do módulo de log para definir um logger.
from dundie.utils.log import get_logger

# Definindo um logger personalizado e atribuindo-o a uma variável.
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
    # Tratando erro caso o arquivo de banco de dados (JSON)
    # não for encontrado.
    try:
        # Lê o arquivo .csv (banco de dados) e atribui seu conteúdo
        # em uma variável
        csv_data = reader(open(filepath))

    # Tratando o erro FileNotFoundError
    except FileNotFoundError as e:
        # Imprime uma mensagem de log e invoca um erro.
        log.error(str(e))
        raise e

    # Conecta no banco de dados
    db = connect()
    # Cria uma lista de pessoas vazia que será usada para exibir no console.
    people = []
    # Lista que contêm o cabeçalho/colunas de dados.
    headers = ["name", "dept", "role", "email"]

    # Para cada linha do arquivo de dados (JSON).
    for line in csv_data:
        # Função `zip` vai juntar as colunas com os seus respectivos dados,
        # para isso será usado uma list comprehension que percorre cada item
        # na linha e também retira os espaços em branco.
        # Função `dict` converte o objeto zip para um dicionário e
        # armazena numa variável.
        person_data = dict(zip(headers, [item.strip() for item in line]))
        # Coleta e atribui a uma variável a chave primária (email) e
        # a remove do dicionário.
        pk = person_data.pop("email")
        # Executa a função para adicionar cada uma dessas pessoas
        # no banco de dados, retornando os dados da pessoa e
        # se ela foi criada ou não.
        person, created = add_person(db, pk, person_data)

        # Faz uma cópia dos dados da pessoa e atribui a uma variável.
        return_data = person.copy()
        # Insere na cópia dos dados a informação se ela foi criada ou não.
        return_data["created"] = created
        # Reinsere na cópia dos dados seu email (chave primária).
        return_data["email"] = pk
        # Adiciona a cópia dos dados dessa pessoa na lista vazia de exibição.
        people.append(return_data)

    # Confirma as mudanças no banco de dados.
    commit(db)
    # Retorna a lista para exibir os dados das pessoas no console.
    return people
