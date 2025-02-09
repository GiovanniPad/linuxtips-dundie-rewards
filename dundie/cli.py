# Biblioteca para manipular arquivos json.
import json

# Biblioteca para acessar as informações do pacote de distribuição do app,
# substitui o pkg_resources.
from importlib.metadata import metadata

# Biblioteca do pacote `rich` para a biblioteca `click`, que
# estiliza a linha de comando (CLI).
import rich_click as click

# Módulo da biblioteca `rich` para definir um Console e
# coletar suas características
from rich.console import Console

# Módulo da biblioteca `rich` para criar tabelas no terminal.
from rich.table import Table

# Import relativo, procura na mesma pasta do módulo atual.
from dundie import core

# Configurações extras do `rich_click`

# Tipo de marcação de texto `rich`
click.rich_click.USE_RICH_MARKUP = True
# Habilita o uso de Markdown
click.rich_click.USE_MARKDOWN = True
# Exibe argumentos posicionais
click.rich_click.SHOW_ARGUMENTS = True
# Exibe os argumentos com as próprias opções
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
# Não exibe uma oluna com as opções da metavar (ex: Integer)
click.rich_click.SHOW_METAVARS_COLUMN = False
# Atribui após o texto de ajuda dados de metavar (ex: [TEXT])
click.rich_click.APPEND_METAVARS_HELP = True


# Decorator `@click.group()` indica que a função `main` como grupo principal
# de comandos
@click.group()
# Adiciona o subcomando `--version` para verificar a versão do app.
# `metadata` coleta a versão do arquivo `setup.py`.
@click.version_option(metadata("giovannipad-dundie").get("version"))
# Principal função do aplicativo
def main():
    """Dunder Mifflin Rewards System

    This cli application controls DM rewards.

    """


# Decorator que indica que a função `load` é
# um subcomando do grupo/função `main`
@main.command()
# Indica um argumento de nome "filepath", com seu tipo
# sendo do tipo `Path` (um arquivo), realiza verificações para
# garantir que o tpo foi inserido corretamente
@click.argument("filepath", type=click.Path())
# Função `load` que faz analogia ao subcomando `load` de `dundie`
def load(filepath):
    """Loads the file to the database.

    - Validates data
    - Parses the file
    - Loads to database
    """

    # Cria um objeto do tipo `Table` para criar uma tabela no CLI
    # atribui um nome a tabela utilizando `title`
    table = Table(title="Dunder Mifflin Associates")
    # Colunas da tabela
    headers = ["name", "dept", "role", "created", "e-mail"]

    # Adiciona coluna por coluna na tabela
    for header in headers:
        # Atribui um estilo para cada coluna com a cor "magenta"
        table.add_column(header, style="magenta")

    # Executa a função `load` e armazena seu resultado
    result = core.load(filepath)
    # Adiciona para cada pessoa, uma linha contendo seus dados
    # Cada campo terá sua respectiva coluna
    for person in result:
        # List comprehension para coletar do dicionário `person`
        # os campos e convertê-los em string.
        table.add_row(*[str(value) for value in person.values()])

    # Cria um objeto do tipo `Console` para coletar as informações do terminal
    console = Console()
    # Imprime a tabela no terminal usando o objeto `Console`
    console.print(table)


# Decorator que define a função `show` como um subcomando de `main`
@main.command()
# Indica uma opção `--dept` que é opcional ao executar o comando
# Esta opção é o departamento que será feito a busca por funcionários para
# exibir
@click.option("--dept", required=False)
# Indica uma opção `--email` que é opcional ao executar o comando
# Esta opção é o email do funcionário a ser procurado e exibido
@click.option("--email", required=False)
# Indica uma opção `--output` e seu valor padrão é `None`
# Esta opção é o arquivo que será usado para armazenar os dados da busca
@click.option("--output", default=None)
# Função que mostra informações sobre usuários
# `output` indica o arquivo de saída
# `query` indica a consulta que será realizada
def show(output, **query):
    """Shows information about users."""

    # Invoca o método `read` para realizar a busca com base na `query` inserida
    # e armazena o resultado em uma variável
    result = core.read(**query)

    # Verifica se o argumento `output` foi inserido,
    # caso sim, escreve o resultado no arquivo específicado
    if output:
        # Abre o gerenciador de contextos de arquivos no modo escrita `w`
        # `output_file` representa o arquivo no contexto
        with open(output, "w") as output_file:
            # Converte de um objeto para uma string JSON formatada e escreve
            # no arquivo
            output_file.write(json.dumps(result))

    # Verifica se nada foi encontrado
    if not result:
        print("Nothing to show.")

    # Cria uma tabela de console da biblioteca rich
    table = Table(title="Dunder Mifflin Associates")

    # Itera sobre os nomes das chaves do ResultDict
    for key in result[0]:
        # Cria uma coluna para cada chave, com seu nome
        # `title()` define a primeira letra como maiúscula
        # `replace()` substitui a string `_` por uma string vazia.
        # `style` define a cor de estilo da coluna
        table.add_column(key.title().replace("_", ""), style="magenta")

    # Itera sobre cada pessoa no dicionário `result`
    for person in result:
        # Adiciona uma linha para cada pessoa encontrada
        # List Comprehension que percorre cada valor do dicionário `person`
        # `values()` retorna apenas os valores de cada chave do dicionário
        # Por fim desempacota a lista com `*`
        table.add_row(*[str(value) for value in person.values()])

    # Cria uma interface de console do rich de alto nível
    console = Console()
    # Imprime a tabela no console do rich
    console.print(table)


# Define a função `add` como subcomando da `main`
@main.command()
# Indica um argumento `value` necessário para o subcomando,
# esse argumento é do tipo `int` e é obrigatório
@click.argument("value", type=click.INT, required=True)
# Indica uma opção `--dept` opcional do subcomando
# Essa opção permite especificar o departamento que será usado no subcomando
@click.option("--dept", required=False)
# Indica uma opção `--email` opcional do subcomando
# Essa opção permite especificar o email do funcionário que será usado
@click.option("--email", required=False)
# Passa por injeção de dependência o contexto do script atual, isso permite
# ter acesso a outros subcomandos dentro dessa função
@click.pass_context
# Função para adicionar pontos para um usuário ou departamento
# `ctx` indica o contexto passado por `pass_context`
# `value` indica a quantia de pontos a serem adicionados
# `query` indica quais usuários vão receber os pontos
def add(ctx, value, **query):
    """Add points to the user or dept."""

    # Executa a função de adicionar pontos no banco de dados
    # A `query` é desempacotada com `**`, pois ela é um dicionário
    core.add(value, **query)
    # Invoca através do contexto o subcomando `show` passando a mesma `query`
    # para mostrar o(s) usuário(s) que foram alterados
    ctx.invoke(show, **query)


# Indica que `remove` é um subcomando de `main`
@main.command()
# Indica um argumento `value` necessário para o subcomando,
# esse argumento é do tipo `int` e é obrigatório
@click.argument("value", type=click.INT, required=True)
# Indica uma opção `--dept` opcional do subcomando
# Essa opção permite especificar o departamento que será usado no subcomando
@click.option("--dept", required=False)
# Indica uma opção `--email` opcional do subcomando
# Essa opção permite especificar o email do funcionário que será usado
@click.option("--email", required=False)
# Passa por injeção de dependência o contexto do script atual, isso permite
# ter acesso a outros subcomandos dentro dessa função
@click.pass_context
# Função que remove pontos do usuário ou departamento
# `ctx` indica o contexto passado por `pass_context`
# `value` indica a quantia de pontos a serem deduzidos
# `query` indica quais usuários vão ter os pontos deduzidos
def remove(ctx, value, **query):
    """Remove points from the user or dept."""

    # Usa a mesma função para adicionar pontos do banco de dados, porém
    # o valor é multiplicado por `-1` para ser negativo e deduzir do total
    # A `query` é desempacotada com `**`, pois ela é um dicionário
    core.add(value * -1, **query)

    # Invoca através do contexto o subcomando `show` passando a mesma `query`
    # para mostrar o(s) usuário(s) que foram alterados
    ctx.invoke(show, **query)
