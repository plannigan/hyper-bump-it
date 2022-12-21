import typer

from hyper_bump_it._cli.by import by
from hyper_bump_it._cli.to import to

app = typer.Typer()
app.command(help="Bump the project to a specific version")(to)
app.command(help="Bump the project version by a specific version part.")(by)
