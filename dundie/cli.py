import json
from importlib.metadata import metadata

import rich_click as click
from rich.console import Console
from rich.table import Table

from dundie import core

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True


@click.group()
@click.version_option(metadata("giovannipad-dundie").get("version"))
def main():
    """Dunder Mifflin Rewards System

    This cli application controls DM rewards.
    """


@main.command()
@click.argument("filepath", type=click.Path())
def load(filepath):
    """Loads the file to the database."""

    table = Table(title="Dunder Mifflin Associates")
    headers = ["email", "name", "dept", "role", "currency", "created"]

    for header in headers:
        table.add_column(header, style="magenta")

    result = core.load(filepath)
    for person in result:

        table.add_row(*[str(value) for value in person.values()])

    console = Console()

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
        person["value"] = f"{person["value"]:.2f}"
        person["balance"] = f"{person["balance"]:.2f}"
        table.add_row(*[str(value) for value in person.values()])

    console = Console()

    console.print(table)


@main.command()
@click.option("--dept", required=False)
@click.option("--email", required=False)
def movements(**query):
    """Show the movements of user(s)."""
    result = core.movements(**query)

    table = Table(title="Account Movements")
    headers = ["email", "name", "dept", "role", "date", "value", "actor"]

    for header in headers:
        table.add_column(header.capitalize(), style="magenta")

    for movement in result:
        table.add_row(*[str(value) for value in movement.values()])

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
    """Remove points from the user or dept."""

    core.add(value * -1, **query)

    ctx.invoke(show, **query)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--to", required=True)
def transfer(value: int, to: str):
    """Transfer points to another user."""
    success, user = core.transfer(value, to_email=to)
    if success:
        print(
            f"Sucesso. {value} pontos transferidos da sua conta "
            f"para a conta de {user}."
        )
