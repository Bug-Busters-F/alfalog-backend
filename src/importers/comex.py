import click
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


@click.group()
def update():
    """Import data from Comex and update the database."""
    pass


comex.add_command(update)


@update.command("todos")
@replace_option
def todos(replace: str):
    """Import all entities."""
    ctx = click.get_current_context()

    commands_to_run = [
        cmd for name, cmd in ctx.parent.command.commands.items() if name != "todos"
    ]

    # Run each command with the same replace parameter
    for cmd in commands_to_run:
        try:
            ctx.invoke(cmd, replace=replace)
        except Exception as e:
            click.echo(f"❌ Erro ao atualizar {cmd.name}: {str(e)}", err=True)
    click.echo("✅ Todos os comandos foram executados!")


@update.command("ufs")
@replace_option
@with_progress_animation()
def ufs(replace: str):
    """Import UFs."""
    click.echo(f"Importando UFs!")
    # click.progressbar

    from .ufs import importar

    try:
        importar(True if replace == "sim" else False)
        click.echo("✅ UFs atualizadas.")
    except Exception as e:
        err.echo(f"❌ Erro ao import UFs: {str(e)}", err=True)


@update.command("ncms")
@replace_option
@with_progress_animation()
def ncms(replace: str):
    """Import NCMs."""
    click.echo(f"Importando NCMs!")
    # click.progressbar

    from .ncms import importar

    try:
        importar(True if replace == "sim" else False)
        click.echo("✅ NCMs atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import NCMs: {str(e)}", err=True)


@update.command("paises")
@replace_option
@with_progress_animation()
def paises(replace: str):
    """Import Países."""
    click.echo(f"Importando Países!")
    # click.progressbar

    from .paises import importar

    try:
        importar(True if replace == "sim" else False)
        click.echo("✅ Países atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import Países: {str(e)}", err=True)


@update.command("sh4")
@replace_option
@with_progress_animation()
def sh4(replace: str):
    """Import SH4s."""
    click.echo(f"Importando SH4s!")
    # click.progressbar

    from .sh4 import importar

    try:
        importar(True if replace == "sim" else False)
    except Exception as e:
        click.echo(f"❌ Erro ao import SH4s: {str(e)}", err=True)
    click.echo("✅ SH4s atualizadas.")


@update.command("sh6")
@replace_option
@with_progress_animation()
def sh6(replace: str):
    """Import SH6s."""
    click.echo(f"Importando SH6s!")
    # click.progressbar

    from .sh6 import importar

    try:
        importar(True if replace == "sim" else False)
    except Exception as e:
        click.echo(f"❌ Erro ao import SH6s: {str(e)}", err=True)
    click.echo("✅ SH6s atualizadas.")


@update.command("ues")
@replace_option
@with_progress_animation()
def ues(replace: str):
    """Import UEs."""
    click.echo(f"Importando UEs!")
    # click.progressbar

    from .ues import importar

    try:
        importar(True if replace == "sim" else False)
        click.echo("✅ UEs atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import UEs: {str(e)}", err=True)


@update.command("urfs")
@replace_option
@with_progress_animation()
def urfs(replace: str):
    """Import URFs."""
    click.echo(f"Importando URFs!")
    # click.progressbar

    from .urfs import importar

    try:
        importar(True if replace == "sim" else False)
        click.echo("✅ URFs atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import URFs: {str(e)}", err=True)


@update.command("vias")
@replace_option
@with_progress_animation()
def vias(replace: str):
    """Import Vias."""
    click.echo(f"Importando Vias!")
    # click.progressbar

    from .vias import importar

    try:
        importar(True if replace == "sim" else False)
        click.echo("✅ Vias atualizadas.")
    except Exception as e:
        click.echo(f"❌ Erro ao import Vias: {str(e)}", err=True)
