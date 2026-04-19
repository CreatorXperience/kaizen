from typing import Dict
import re

SECTION_HEADER = re.compile(r"^[A-Z][A-Z0-9 &/\-]{1,60}$")
SECTION_ALIASES = {"EXAMPLE": "EXAMPLES"}


def parse_man_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current = None
    buffer = []

    for line in text.splitlines():
        line_stripped = line.strip()

        if _is_section_header(line_stripped):
            if current:
                sections[current] = "\n".join(buffer).strip("\n")
                buffer = []

            current = SECTION_ALIASES.get(line_stripped, line_stripped)
            continue

        if current:
            buffer.append(line.rstrip())

    if current:
        sections[current] = "\n".join(buffer).strip("\n")

    return sections


def _is_section_header(line: str) -> bool:
    if not line:
        return False

    return bool(SECTION_HEADER.match(line))
