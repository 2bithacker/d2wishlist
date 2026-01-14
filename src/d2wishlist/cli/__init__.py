import typer

from .creator import create

app = typer.Typer()
app.command()(create)


if __name__ == "__main__":
    app()
