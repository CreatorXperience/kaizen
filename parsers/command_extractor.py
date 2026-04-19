import re
from typing import List, Dict


COMMAND_REGEX = [
    # commands with flags
    r"^\s*([a-zA-Z0-9_\-]+(?:\s+-[^\n]+)+)",
    # commands with arguments
    r"^\s*([a-zA-Z0-9_\-]+\s+[^\n]*<[^>]+>[^\n]*)",
    # basic command usage lines
    r"^\s*([a-zA-Z0-9_\-]+\s+[^\n]+)",
]


def looks_like_command(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    # allow simple commands like "ls", "whoami", "pwd"
    if re.match(r"^[a-zA-Z0-9_\-]+$", line):
        return True

    # allow commands with args
    if re.match(r"^[a-zA-Z0-9_\-]+(\s+.+)?$", line):
        return True

    return False


def extract_commands(text: str) -> List[Dict[str, str]]:
    """
    Extract command examples from text
    """

    lines = text.splitlines()
    commands = []
    seen = set()

    for i, line in enumerate(lines):

        for regex in COMMAND_REGEX:
            match = re.search(regex, line)

            if not match:
                continue

            cmd = match.group(1).strip()

            # skip long paragraphs
            if len(cmd.split()) > 12:
                continue

            # skip duplicates
            if cmd in seen:
                continue

            seen.add(cmd)

            # try get description from previous line
            desc = ""

            if i > 0:
                prev = lines[i - 1].strip()

                if len(prev) < 80:
                    desc = prev

            commands.append({"desc": desc, "cmd": cmd})

    return commands
