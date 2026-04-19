from typing import Dict, List


def build_commands(man_page: Dict[str, object]) -> List[Dict[str, str]]:
    commands: List[Dict[str, str]] = []
    seen = set()

    command = str(man_page.get("command", "")).strip()
    examples = man_page.get("examples", []) or []
    options = man_page.get("options", []) or []
    summary = str(man_page.get("summary", "")).strip()

    for item in examples:
        if not isinstance(item, dict):
            continue
        cmd = item.get("cmd", "").strip()
        if not cmd or cmd in seen:
            continue
        seen.add(cmd)
        commands.append(
            {
                "desc": item.get("desc", "").strip() or "Example from the man page",
                "cmd": cmd,
            }
        )

    for option in options[:20]:
        if not isinstance(option, dict):
            continue
        usage = option.get("usage", "").strip()
        if not usage or not command:
            continue

        cmd = f"{command} {usage}".strip()
        if cmd in seen:
            continue

        seen.add(cmd)
        commands.append(
            {
                "desc": option.get("description", "").strip(),
                "cmd": cmd,
            }
        )

    if not commands and command:
        commands.append({"desc": summary or f"Run {command}", "cmd": command})

    return commands
