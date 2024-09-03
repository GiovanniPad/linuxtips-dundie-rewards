# Biblioteca padrão do Python para coletar argumentos de CLI de uma forma mais amigável.
import argparse

# Import relativo, procura na mesma pasta do módulo atual.
from dundie.core import load

# Principal função do programa.
def main():
    # Definindo um objeto do tipo `parser` para coletar os argumentos CLI.
    parser = argparse.ArgumentParser(
        # Descrição do projeto.
        description="Dunder Mifflin Rewards CLI",
        # Mensagem enviada para o terminal.
        epilog="Enjoy and use with cautious.",
    )

    # Definindo o primeiro argumento da CLI.
    # `subcommand` é o nome do argumento,
    # `type` é o tipo de objeto do argumento,
    # `help` mensagem de ajuda referente ao argumento,
    # `choices` são os possíveis valores para o argumento,
    # `default` valor padrão, caso nenhum valor seja passado.
    parser.add_argument(
        "subcommand",
        type=str,
        help="The subcommand to run",
        choices=("load", "show", "send"),
        default="help"
    )

    # Definindo o segundo argumento da CLI, mesma lógica do anterior.
    parser.add_argument(
        "filepath",
        type=str,
        help="File path to load",
        default=None
    )

    # Coleta os argumentos do objeto `parser`.
    args = parser.parse_args()

    # Invoca a função específica para cada valor de argumento passado.
    # Executa a função através da função `globals()`.
    print(*globals()[args.subcommand](args.filepath))