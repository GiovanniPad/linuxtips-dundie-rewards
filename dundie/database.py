# Biblioteca para trabalhar com datas e horas
import datetime

# Biblioteca usada pelo sistema de imports do Python
import importlib

# Biblioteca para tratar arquivos do tipo JSON.
import json

# Módulo que fornece estruturas de dados especializadas
# A classe `UserList` funciona como uma lista Python, mas permite
# personalização ao ser herdada
# `defaultdict` é um dicionário que cria valores padrão automaticamente
# caso uma chave não exista
from collections import UserList, defaultdict

# Módulo usado para anotações de tipo
# Any, Dict e Option são tipos genéricos do módulo
# `TYPE_CHECKING` é uma constante usada para evitar importar módulos
# em tempo de execução, melhorando a performance
from typing import TYPE_CHECKING, Any, Dict, Optional

# `TYPE_CHECKING` é sempre false em tempo de execução, mas true durante
# a análise de tipo (como no `mypy`)
# Isso faz com que `BaseModel` seja importado apenas para checagem estática e
# não em tempo de execução, melhorando a performance
if TYPE_CHECKING:
    from pydantic import BaseModel

# Importanto informações e funções necessárias.
from dundie.settings import DATABASE_PATH, EMAIL_FROM
from dundie.utils.email import send_email

# Criando o schema (esquema) do "banco de dados".
EMPTY_DB: Dict[str, Dict[str, Any]] = {
    "people": {},
    "balance": {},
    "movement": {},
    "user": {},
}

# Anotação de tipo composta
DB = Dict["BaseModel", "ResultList"]


# Classe que estende `UserList`, permite que se comporte como uma lista,
# mas com métodos adicionais
class ResultList(UserList):
    # Retorna o primeiro elemento da lista
    # `self` é a referência da lista
    def first(self) -> Any:
        return self[0]

    # Retorna o último elemento da lista
    def last(self) -> Any:
        return self[-1]

    # Busca por um item na lista pelo `pk` (chave primária)
    def get_by_pk(self, pk: str) -> Any:
        # Verifica se a lista está vazia,
        # se a lista estiver vazia, levanta um eror `NotFoundError`
        if len(self) == 0:
            raise NotFoundError(f"{pk} not found")

        # Bloco try para capturar erros
        try:
            # Verifica se o primeiro elemento da lista tem um atributo `pk`
            if hasattr(self[0], "pk"):
                # Caso tenha, retorna uma `ResultList` que contém apenas os
                # itens que possuem `pk` igual ao valor passado e retorna o
                # primeiro item encontrado
                return ResultList(
                    item for item in self if item.pk == pk
                ).first()
            # Caso os itens da lista não tem a `pk` diretamente, assume que o
            # `pk` está dentro de `item.person.pk` e aplica o mesmo filtro
            return ResultList(
                item for item in self if item.person.pk == pk
            ).first()
        # Captura um possível erro `KeyError`
        except KeyError:
            # Levanta uma excenção `NotFoundError`
            raise NotFoundError(f"{pk} not found")

    # Função para filtrar itens da lista com base na query de consulta `query`
    # `self` representa a lista
    # `query` representa um dicionário para consulta
    # A função retorna uma `ResultList`
    def filter(self, **query: Dict[str, Any]) -> "ResultList":

        # Se nenhuma `query` de consulta for passado, retorna a lista inteira
        if not query:
            return self

        # Cria um objeto `ResultList` para armazenar os itens filtrados
        return_data = ResultList()

        # Itera sobre todos os itens da lista
        for item in self:

            # Lista temporário para armazenar os itens filtrados
            add_item = []

            # Itera sobre cada filtro passados na `query`
            # `items()` retorna um set com o campo a ser filtrado
            # e o seu valor desejado
            for q, v in query.items():
                # Se a query tiver `__`, quer dizer que se está filtrando
                # dentro de um atributo relacionado,
                # que é um objeto como um atributo
                if "__" in q:
                    # Divide o atributo relacionado entre o
                    # nome da classe como atributo e o campo dessa classe
                    sub_model, sub_field = q.split("__")

                    # Coleta o objeto que está armazenado no atributo
                    related = getattr(item, sub_model)
                    # Compara se o valor do atributo `sub_field` do objeto
                    # aninhado `related` é igual ao valor desejado `value`
                    if getattr(related, sub_field) == v:
                        # Caso for o valor desejado adiciona True
                        add_item.append(True)
                # Caso não tiver `__` na query de consulta realiza a consulta
                # direto, sem objetos como atributos
                else:
                    # Verifica se o valor do atributo `query` do objeto `item`
                    # é igual ao valor desejado `value`
                    if getattr(item, q) == v:
                        # Caso for o valor desejado, adiciona True
                        add_item.append(True)
                    else:
                        # Caso não for o valor desejado, adiciona False
                        add_item.append(False)

            # Verifica se há algum valor filtrado e se todos os critérios
            # foram atendidos, caso tudo for True, adiciona o item à lista
            # final, que vai ser retornada
            if add_item and all(add_item):
                # Adiciona o item filtrado no final da lista `return_data`
                return_data.append(item)

        # Retorna a lista com todos os itens encontrados no filtro
        return return_data


# Classe `ORM`, sua função é fazer o mapeamento entre
# tableas JSON e modelos python
class ORM:
    """Mapeamento entre "table" no JSON e classes em models"""

    # Dicionário que define o mapeamento entre os nomes das tabelas
    # e os caminhos completos das classes Python
    # Permite associar dados JSON a suas classes correspondentes
    MAPPING: Dict[str, str] = {
        "people": "dundie.models.Person",
        "balance": "dundie.models.Balance",
        "movement": "dundie.models.Movement",
        "user": "dundie.models.User",
    }

    # Decorator para definir que a função é um método da classe
    # Isso permite receber o método receber a classe implicitamente
    # no parâmetro `cls`
    @classmethod
    # Método que recebe o nome da tabela e retorna a classe Python
    # que é correspondente
    # `table_name` é um parâmetro com o tipo de dado string
    # O retorno desse método pode ser qualquer valor Any
    def get_model_class(cls, table_name: str) -> Any:
        # Busca no dicionário `MAPPING` o caminho completo do módulo,
        # após separa o caminho do módulo `module` da classe desejada `obj`
        module, obj = cls.MAPPING[table_name].rsplit(".", 1)

        # Importa o módulo com a funcão `import_module` da `importlib`
        # e usa a função `getattr` para obter a classe desejada do modelo
        # e por fim a retorna
        return getattr(importlib.import_module(module), obj)

    # Define que a função é um método da classe, recebendo a instância
    # da classe `cls` como injeção de dependência
    @classmethod
    # Retorna o nome da tabela JSON com base na classe do modelo,
    # invertendo o mapeamento
    # `model` é um tipo qualquer Any
    # O retorno do método é do tipo string
    def get_table_name(cls, model: Any) -> str:
        # Cria um novo dicionário, onde a chave é o nome da classe e
        # o valor é o nome da tabela
        inverted_orm = {
            # Separa do nome completo do módulo os nomes individuais
            # e coleta o último nome, que é o nome da classe e atribui
            # como chave no novo dicionário
            # A chave `key` vira o valor no novo dicionário
            # Tudo isso é feito para cada valor no dicionário MAPPING
            value.split(".")[-1]: key
            for key, value in cls.MAPPING.items()
        }

        # Retorna o nome da tabela correspondente ao modelo
        return inverted_orm[model.__name__]

    # Define que a função é um método de classe,
    # disponibiliza a instância da classe por injeção de dependência
    # através do parâmetro `cls`
    @classmethod
    # Método usado para converter objetos Python em JSON
    # Recebe um banco de dados em memória `db` e o transforma
    # em um dicionário JSON
    def serialize(cls, db: DB) -> Dict[str, Any]:
        """Turns Model instances back to json compatible dict."""
        # cria um dicionário vazio, a função `defaultdict` faz com que
        # ao acessar uma chave não existente, ela será criada automaticamente
        # como um dicionário vazio
        raw_db: Dict[str, Any] = defaultdict(dict)

        # Itera sobre cada modelo no banco de dados
        for model, instances in db.items():
            # Coleta a classe que representa o modelo (entidade) do banco
            table_name = cls.get_table_name(model)
            # Inicializa a entrada no dicionário vazio
            raw_db[table_name]

            # Itera sobre cada instância
            for instance in instances:
                # Converte a instância para JSON
                raw_instance = json.loads(instance.json())

                # Para a tabela `people`
                if table_name == "people":
                    # Armazena a instância JSON e usa a chave primária `pk`
                    # como chave no dicionário
                    raw_db[table_name][raw_instance.pop("pk")] = raw_instance
                # Para a tabela `balance`
                elif table_name == "balance":
                    # Armazena o valor da instância JSON e usa `person.pk`
                    # como chave
                    raw_db[table_name][instance.person.pk] = raw_instance[
                        "value"
                    ]
                # Para a tabela `movement`
                elif table_name == "movement":
                    # Obtém a referência ao dicionário `table`, que representa
                    # essa tabela dentro do banco `raw_db`
                    table = raw_db[table_name]
                    # Garante que exista uma lista para a instância de Person
                    # Caso já exista, mantém a lista existente
                    # Caso não existir, cria uma lista vazia
                    table.setdefault(instance.person.pk, [])
                    # remove o campo `person`, pois ele já está agrupado
                    # pela chave primária `pk` da pessoa
                    raw_instance.pop("person")
                    # Adiciona a movimentação à lista de movimentos da
                    # instância da pessoa
                    table[instance.person.pk].append(raw_instance)
                else:
                    # Para outras tabelas, remove a instância Person
                    raw_instance.pop("person")
                    # E por fim armazena no dicionário
                    raw_db[table_name][instance.person.pk] = raw_instance
        # Retorna o banco de dados em formato JSON
        return raw_db

    # Define a classe como um método de classe
    @classmethod
    # Converte um arquivo em formato JSON para um objeto Python, no caso
    # um dicionário
    def deserialize(cls, raw_data: Dict[str, Any]) -> Dict[Any, ResultList]:
        """Turns JSON in to model instances"""

        # Armazena uma lista de instâncias dos modelos
        results: Dict[Any, ResultList] = defaultdict(ResultList)
        # Ajuda a restrear pessoas criadas para referência posterior
        indexes = {}

        # Para cada tabela no JSON
        for table_name, data in raw_data.items():
            # Obtém a classe do modelo correspondente
            Model = cls.get_model_class(table_name)
            # Inicializa a entrada em `results`
            results[Model]
            # Para a tabela `people`
            if table_name == "people":
                # Para cada pessoa contida nela
                for pk, person_data in data.items():
                    # Cria uma instância de person com seus dados
                    instance = Model(pk=pk, **person_data)
                    # Armazena essa instância com sua chave em `indexes`
                    indexes[pk] = instance
                    # Atribui essa instância a `results` usando seu tipo
                    # de modelo como chave
                    results[Model].append(instance)
            # Para a tabela `balance`
            elif table_name == "balance":
                # Para cada saldo
                for pk, balance_data in data.items():
                    # Associa o saldo a instância da pessoa e armazena
                    # em uma instância
                    instance = Model(person=indexes[pk], value=balance_data)
                    # Por fim, atribui essa instância em `results` usando
                    # a classe como chave
                    results[Model].append(instance)
            # Para a tabela `user`
            elif table_name == "user":
                # Para cada usuário
                for pk, user_data in data.items():
                    # Através do `indexes` atribui os dados do usuário
                    # para a instância correta de Person
                    instance = Model(person=indexes[pk], **user_data)
                    # Adiciona a instância criada no dicionário, usando
                    # o nome da classe como chave
                    results[Model].append(instance)
            # Para a tabela `movement`
            elif table_name == "movement":
                # Percorre os movimentos de cada pessoa
                for pk, movements in data.items():
                    # Percorre movimento por movimento
                    for movement in movements:
                        # Atribui os movimentos a pessoa correta
                        instance = Model(person=indexes[pk], **movement)
                        # Adiciona ao dicionário final essa instância com os
                        # movimentos, usando o nome da classe como chave
                        results[Model].append(instance)
        # Retorna o dicionário final desserializado
        return results


# Classe para representar um erro de arquivo não encontrado
class NotFoundError(Exception):
    pass


# Função para conectar com o banco de dados e
# cria um objeto contendo os dados.
def connect() -> Dict[Any, ResultList]:
    """Connects to the database, returns dict data"""
    try:
        # Abre e lê o arquivo JSON (banco de dados).
        with open(DATABASE_PATH, "r") as database_file:
            raw_data = json.loads(database_file.read())

    # Captura as possíveis exceções.
    # `JSONDecodeError` ocorre caso o arquivo esteja vazio.
    except (json.JSONDecodeError, FileNotFoundError):
        raw_data = EMPTY_DB

    # Desserializa o banco de dados JSON para um dicionário
    results = ORM.deserialize(raw_data)
    # Retorna o dicionário para exibir os dados
    return results


# Função para salvar as mudanças no banco de dados (JSON).
def commit(db: DB):
    """Save db back to the database file."""
    # Serializa as instâncias de classes Python em JSON para armazenar no banco
    raw_db = ORM.serialize(db)

    # Verifica se o esquema do banco está correto
    if raw_db.keys() != EMPTY_DB.keys():
        # Estoura um erro caso não estiver
        raise RuntimeError(f"Database Schema is invalid. {raw_db.keys()}")

    # Converte o banco formatado para JSON
    final_data = json.dumps(raw_db, indent=4)

    # Abre o arquivo JSON (Banco de dados) no modo de escrita e
    # salva as modificações.
    with open(DATABASE_PATH, "w") as database_file:
        database_file.write(final_data)


# Função para adicionar uma pessoa ao banco de dados (arquivo JSON).
# Se ela já existir, atualiza seus dados
# Se não existir, é criada e recebe um saldo inicial e uma senha gerada
def add_person(db: DB, instance: Any):
    """Saves person data to database.

    - Email is unique (resolved by dictionary hash table)
    - If exists, update, else create
    - Set initial balance (managers = 100, others = 500)
    - Generate a password if user is new and send email
    """

    # Obtêm uma instância da classe Person
    Person = ORM.get_model_class("people")
    # Coleta uma lista de instâncias de todas as pessoas armazenadas no banco
    table = db[Person]

    # Usa o filtro para encontrar essa pessoa no banco de dados
    existing = table.filter(pk=instance.pk)
    # Verifica se já está criada
    created = len(existing) == 0

    # Caso for a primeira vez que a pessoa estiver sendo registrada.
    if created:
        # Atribui a instância dessa pessoa a lista de instâncias
        table.append(instance)
        # Define um balanço inicial de pontos para ela
        set_initial_balance(db, instance)
        # Gera uma senha inicial aleatória
        password = set_initial_password(db, instance)
        # Envia por email a senha gerada
        send_email(EMAIL_FROM, instance.pk, "Your dundie password", password)
        # TODO: encrypt and send only link not raw password
    # Caso a pessoa já existir
    else:
        # Coleta os dados atuais dela
        existing_data = existing.first().dict()
        # Coleta os dados novos dela
        new_data = instance.dict()
        # Substitui os dados atuais pelos dados novos
        existing_data.update(new_data)
        # Remove da tabela os dados antigos
        table.remove(existing[0])
        # Adiciona uma instância de pessoa a lista de instância
        # com os dados atualizados
        table.append(Person(**existing_data))
    # Retorna a instância da pessoa criada e se foi seu primeiro cadastro
    return instance, created


# Função para criar uma senha inicial para um novo usuário.
def set_initial_password(db: DB, instance: Any) -> str:
    """Generated and saves password."""
    User = ORM.get_model_class("user")
    user = User(person=instance)  # password generated by model
    db[User].append(user)
    return user.password


# Função para definir o balanço de pontos inicial.
def set_initial_balance(db: DB, person: Any):
    """Add movement and set initial balance"""
    # Adiciona 100 pontos se a pessoa tiver o cargo `Manager`
    # e adiciona 500 pontos para os outros cargos
    value = 100 if person.role == "Manager" else 500
    # Adiciona essa transação de pontos a seu histórico de transações
    add_movement(db, person, value)


# Função para criar uma movimentação de saldo
def add_movement(
    db: DB, person: Any, value: int, actor: Optional[str] = "system"
):
    """Adds movement to user account."""
    # Cria uma instância da classe `Movement`
    Movement = ORM.get_model_class("movement")

    # Coleta a data e o horário atual da transação
    # `isoformat()` converte para um formato que possa ser armazenado
    # em um banco de dados
    date = datetime.datetime.now().isoformat()

    # Adiciona a transação no banco de dados
    db[Movement].append(
        # Indica a pessoa que fez a transação, a data e o valor e o ator
        # o ator é quem emitiu a transação
        Movement(person=person, date=date, value=value, actor=actor)
    )

    # Pega todos os movimentos do usuário em questão
    movements = [item for item in db[Movement] if item.person.pk == person.pk]

    # Coleta a classe `Balance` do modelo de classes
    Balance = ORM.get_model_class("balance")

    # Coleta e adiciona ao banco todos os outros saldos dos outros usuários
    db[Balance] = ResultList(
        [item for item in db[Balance] if item.person.pk != person.pk]
    )

    # Atualiza o saldo da pessoa, com base nessa nova transação adicionada
    db[Balance].append(
        Balance(person=person, value=sum([item.value for item in movements]))
    )
