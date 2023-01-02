import typer

from hyper_bump_it._cli.by import by_command
from hyper_bump_it._cli.init import init_command
from hyper_bump_it._cli.to import to_command

app = typer.Typer()
app.command(name="by", help="Bump the project version by a specific version part.")(
    by_command
)
app.command(name="to", help="Bump the project to a specific version")(to_command)
app.command(name="init", help="Initial setup of configuration")(init_command)
