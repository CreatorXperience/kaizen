from typing import Any, Dict, List, Optional


def summarize_commands(
    query: str,
    commands: List[Dict[str, str]],
    man_page: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    start: int = 0,
    end: int = 0,
) -> Dict:
    """
    Convert extracted commands into TLDR-style output
    """

    cleaned = []
    seen = set()

    for item in commands:
        cmd = item.get("cmd", "").strip()
        desc = item.get("desc", "").strip()

        if not cmd:
            continue

        # remove duplicates
        if cmd in seen:
            continue

        seen.add(cmd)

        # fallback description
        if not desc:
            desc = generate_description(query, cmd)

        cleaned.append({"desc": desc, "cmd": cmd})

    payload = {}
    if start and end:
        payload = {
            "query": query,
            "commands": cleaned[start:end],
        }
    elif start and not end:
        payload = {
            "query": query,
            "commands": cleaned[start:],
        }
    elif end and not start:
        payload = {
            "query": query,
            "commands": cleaned[0:end],
        }

    if not start and not end:

        payload = {
            "query": query,
            "commands": cleaned[:limit],
        }

    if man_page:
        payload["man_page"] = man_page
        payload["summary"] = man_page.get("summary", "")
        payload["command"] = man_page.get("command", query)

    return payload


def generate_description(query: str, cmd: str) -> str:
    """
    Generate simple description from command
    """

    parts = cmd.split()

    if len(parts) == 1:
        return f"Run {parts[0]}"

    binary = parts[0]

    # simple heuristics
    if "-h" in cmd or "--help" in cmd:
        return "Show help"

    if "-v" in cmd:
        return "Verbose output"

    if "-p" in cmd:
        return "Specify port"

    if "-i" in cmd:
        return "Specify interface"

    if "-o" in cmd:
        return "Output to file"

    if "-w" in cmd:
        return "Write to file"

    return f"{query} example"
