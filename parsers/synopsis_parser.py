import re


def extract_base_command(synopsis: str) -> str:
    for line in synopsis.splitlines():

        line = line.strip()

        if not line:
            continue

        # extract first word only (works for ls, nmap, etc)
        match = re.match(r"^([a-zA-Z0-9_\-]+)", line)

        if match:
            return match.group(1)

    return ""
