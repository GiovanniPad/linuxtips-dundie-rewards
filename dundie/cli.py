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


@main.command()
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.option("--output", default=None)
def show(output, **query):
    """Shows information about users."""
    result = core.read(**query)
    if output:
        with open(output, "w") as output_file:
            output_file.write(json.dumps(result))

    if not result:
        print("Nothing to show.")

    table = Table(title="Dunder Mifflin Associates")
    for key in result[0]:
        table.add_column(key.title().replace("_", ""), style="magenta")

    for person in result:
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def add(ctx, value, **query):
    """Add points to the user or dept."""

    core.add(value, **query)
    ctx.invoke(show, **query)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def remove(ctx, value, **query):
    """Add points to the user or dept."""

    core.add(value * -1, **query)
    ctx.invoke(show, **query)
