from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def format_output(data: Dict[str, Any], from_cache: bool = False) -> str:
    """
    Format output for terminal display
    """

    payload = data.get("data", data)
    commands = payload.get("commands", [])
    man_page = payload.get("man_page", {})

    if not commands:
        return "No commands found"

    header = (
        man_page.get("command")
        or payload.get("command")
        or payload.get("query")
        or "Cyber TLDR"
    )
    if from_cache:
        header += " (cached)"

    console.print(Panel.fit(header, style="bold cyan"))

    summary = man_page.get("summary") or payload.get("summary")
    if summary:
        console.print(Text(summary, style="italic"))

    for item in commands:
        desc = item.get("desc", "").strip()
        cmd = item.get("cmd", "").strip()

        if desc:
            console.print(f"[bold green]{desc}[/bold green]")

        console.print(Panel(Text(cmd, style="bold red"), border_style="blue"))

    return ""
