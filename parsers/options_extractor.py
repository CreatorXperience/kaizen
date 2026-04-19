import re
from typing import List, Dict


OPTION_REGEX = re.compile(
    r"""
    ^
    \s*
    (?P<option>
        (?:-\w[, ]*)+
        (?:\s+[A-Z<>\[\]\-]+)?
    )
    \s+
    (?P<desc>.+)
    """,
    re.VERBOSE,
)


def extract_options(text: str) -> List[Dict[str, str]]:
    options = []

    for line in text.splitlines():

        match = OPTION_REGEX.match(line)

        if not match:
            continue

        option = match.group("option").strip()
        desc = match.group("desc").strip()

        options.append({"option": option, "desc": desc})

    return options
