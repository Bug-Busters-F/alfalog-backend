import click
from flask.cli import with_appcontext
import threading
import time
from functools import wraps
from itertools import cycle


@click.group()
def comex():
    """Comando para extração de dados do site do Comex.
    Visite https://comexstat.mdic.gov.br/pt/home.
    """
    pass


def with_progress_animation(message="Processando"):
    """Decorator to add animated progress dots to any Click command."""

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            done = False
            message_template = f"\r{message} {{frame}}"

            # Animation thread
            def animate():
                for frame in cycle(["   ", ".  ", ".. ", "..."]):
                    if done:
                        break
                    click.echo(message_template.format(frame=frame), nl=False)
                    time.sleep(0.3)

            t = threading.Thread(target=animate)
            t.start()

            try:
                result = func(*args, **kwargs)
            finally:
                done = True
                t.join()
                # Clear line
                click.echo("\r" + " " * (len(message) + 5) + "\r", nl=False)

            return result

        return wrapper

    return decorator


def replace_option(f):
    """Prompt whether the existing db data should be replaced.
    Decorator for `--replace` option.
    """
    return click.option(
        "--replace",
        type=click.Choice(["sim", "nao"], case_sensitive=False),
        default="nao",
        show_default=True,
        help="Substitui registros existentes no Banco de Dados? (sim/nao)",
        prompt="Substituir os registros já existentes no Banco de Dados?",
    )(f)


@click.group(invoke_without_command=True)
@click.pass_context
@replace_option
def update(ctx, replace: str):
    """Import data from Comex and update the database."""
    # Store the replace value in the context
    ctx.ensure_object(dict)
    ctx.obj["replace"] = replace
    if ctx.invoked_subcommand is None:

        def run_command(cmd):
            try:
                ctx.invoke(cmd)
            except Exception as e:
                click.echo(f"❌ Erro ao atualizar {cmd.name}: {str(e)}", err=True)

        main_commands = {"transacoes"}
        all_commands = ctx.command.commands.items()

        commands_main = [cmd for name, cmd in all_commands if name in main_commands]
        commands_second = [
            cmd for name, cmd in all_commands if name not in main_commands
        ]

        for cmd in commands_second:
            run_command(cmd)
        for cmd in commands_main:
            run_command(cmd)
        click.echo("✅ Todos os comandos foram executados!")


comex.add_command(update)


@update.command("ufs")
@click.pass_context
@with_progress_animation()
def ufs(ctx):
    """Import UFs."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando UFs!")
    # click.progressbar

    from .ufs import importar

    try:
        importar(replace == "sim")
        click.echo("✅ UFs atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import UFs: {str(e)}", err=True)


@update.command("ncms")
@click.pass_context
@with_progress_animation()
def ncms(ctx):
    """Import NCMs."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando NCMs!")
    # click.progressbar

    from .ncms import importar

    try:
        importar(replace == "sim")
        click.echo("✅ NCMs atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import NCMs: {str(e)}", err=True)


@update.command("paises")
@click.pass_context
@with_progress_animation()
def paises(ctx):
    """Import Países."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando Países!")
    # click.progressbar

    from .paises import importar

    try:
        importar(replace == "sim")
        click.echo("✅ Países atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import Países: {str(e)}", err=True)


@update.command("sh4")
@click.pass_context
@with_progress_animation()
def sh4(ctx):
    """Import SH4s."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando SH4s!")
    # click.progressbar

    from .sh4 import importar

    try:
        importar(replace == "sim")
    except Exception as e:
        click.echo(f"❌ Erro ao import SH4s: {str(e)}", err=True)
    click.echo("✅ SH4s atualizadas.")


@update.command("sh6")
@click.pass_context
@with_progress_animation()
def sh6(ctx):
    """Import SH6s."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando SH6s!")
    # click.progressbar

    from .sh6 import importar

    try:
        importar(replace == "sim")
    except Exception as e:
        click.echo(f"❌ Erro ao import SH6s: {str(e)}", err=True)
    click.echo("✅ SH6s atualizadas.")


@update.command("ues")
@click.pass_context
@with_progress_animation()
def ues(ctx):
    """Import UEs."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando UEs!")
    # click.progressbar

    from .ues import importar

    try:
        importar(replace == "sim")
        click.echo("✅ UEs atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import UEs: {str(e)}", err=True)


@update.command("urfs")
@click.pass_context
@with_progress_animation()
def urfs(ctx):
    """Import URFs."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando URFs!")
    # click.progressbar

    from .urfs import importar

    try:
        importar(replace == "sim")
        click.echo("✅ URFs atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import URFs: {str(e)}", err=True)


@update.command("vias")
@click.pass_context
@with_progress_animation()
def vias(ctx):
    """Import Vias."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando Vias!")
    # click.progressbar

    from .vias import importar

    try:
        importar(replace == "sim")
        click.echo("✅ Vias atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import Vias: {str(e)}", err=True)


@update.command("exportacoes")
@click.pass_context
@with_appcontext
@with_progress_animation()
def exportacoes(ctx):
    """Import as transações de exportação."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando as transações de exportação!")
    # click.progressbar

    from .exportacoes import importar_dados
    from src.utils.sqlalchemy import SQLAlchemy

    try:
        # importar(replace == "sim")
        db = SQLAlchemy.get_instance()
        # Descomente as linha abaixo caso queira importar dados de EXPORTACOES
        caminho_csv = "./data/dados_comex_EXP_2014_2024.csv"
        importar_dados(db, caminho_csv, "exportacoes")
        click.echo("✅ Transações atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import Transações: {str(e)}", err=True)


@update.command("importacoes")
@click.pass_context
@with_appcontext
@with_progress_animation()
def importacoes(ctx):
    """Import as Transações de Importação."""
    replace = ctx.obj["replace"]
    click.echo(f"Importando as Transações de Importação!")
    # click.progressbar

    from .importacoes import importar_dados
    from src.utils.sqlalchemy import SQLAlchemy

    try:
        # importar(replace == "sim")
        db = SQLAlchemy.get_instance()
        caminho_csv = "./data/dados_comex_IMP_2014_2024.csv"
        importar_dados(db, caminho_csv)
        click.echo("✅ Transações atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import Transações: {str(e)}", err=True)


@update.command("balanca")
@click.pass_context
@with_appcontext
@with_progress_animation("Calculando balança comercial")
def balanca(ctx):
    """Importa os dados de balança comercial (exportação - importação)."""
    replace = ctx.obj["replace"]

    from src.utils.sqlalchemy import SQLAlchemy
    from .balanca import importar_balanca

    try:
        db = SQLAlchemy.get_instance()
        importar_balanca(db, replace == "sim")
        click.echo("✅ Balança comercial importada.")
    except Exception as e:
        click.echo(f"❌ Erro ao importar balança comercial: {str(e)}", err=True)

@update.command("somas")
@click.pass_context
@with_appcontext
@with_progress_animation()
def somas(ctx):
    """Importa as Somas de Importação e Exportação por UF e ano."""
    replace = ctx.obj["replace"]
    click.echo("📊 Importando as somas dos estados...")

    from src.utils.sqlalchemy import SQLAlchemy
    from .transacoes import calcular_somas_por_uf_e_ano_csv

    db = SQLAlchemy.get_instance()

    try:
        caminho_csv_imp = "./data/dados_comex_IMP_2014_2024.csv"
        caminho_csv_exp = "./data/dados_comex_EXP_2014_2024.csv"
        calcular_somas_por_uf_e_ano_csv(db, caminho_csv_imp, caminho_csv_exp, replace)
        click.echo("✅ Somas importadas com sucesso!")
    except Exception as e:
        click.echo(f"❌ Erro ao importar somas: {str(e)}", err=True)
