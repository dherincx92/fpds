import typer

app = typer.Typer()


@app.callback()
def callback() -> None:
    """Welcome to the fpds CLI 🚀"""
