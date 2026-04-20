import typer
from core.engine import run_query

app = typer.Typer(help="Kaizen - cybersecurity command learner")


@app.command()
def search(
    query: str = typer.Argument(..., help="Command or idea to search"),
    update: bool = typer.Option(False, "--update", "-u", help="Force update cache"),
    offline: bool = typer.Option(False, "--offline", "-o", help="Use cache only"),
    limit: int = typer.Option(int, "--limit", "-l", help="Limit example output"),
    start: int = typer.Option(
        int,
        "--startfrom",
        "-s",
        help="pick a number as a starting point, to limit scrolling, -l is void , when using this option",
    ),
    end: int = typer.Option(
        int,
        "--end",
        "-e",
        help="pick a number as a end point, to limit scrolling, -l is void when using this option",
    ),
):
    """
    Search for cybersecurity commands
    """
    run_query(
        query=query,
        update=update,
        offline=offline,
        limit=limit or 5,
        start=start,
        end=end,
    )


@app.command()
def clear():
    """
    Clear cache
    """
    from cache.store import clear_cache

    clear_cache()
    typer.echo("Cache cleared")


@app.command()
def list():
    """
    List cached commands
    """
    from cache.store import list_cache

    items = list_cache()

    for item in items:
        typer.echo(item)


if __name__ == "__main__":
    app()
