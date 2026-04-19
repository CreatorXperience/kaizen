from dataclasses import asdict, dataclass
import re
from typing import Dict, List, Optional

from parsers.man_sections import parse_man_sections

SHORT_OPTION_RE = r"-[^,\s](?:\[[^\]]+\])?"
LONG_OPTION_RE = r"--[A-Za-z0-9][A-Za-z0-9-]*(?:\[[^\]]+\])?"
AT_OPTION_RE = r"@[A-Za-z0-9_<>\[\]./\-]+"
OPTION_TOKEN_RE = rf"(?:{AT_OPTION_RE}|{LONG_OPTION_RE}|{SHORT_OPTION_RE})(?:[ =][A-Za-z<>\[\]\-][A-Za-z0-9_<>\[\]\-]*)?"
OPTION_DECL_RE = re.compile(
    rf"^\s*(?P<usage>{OPTION_TOKEN_RE}(?:\s*,\s*{OPTION_TOKEN_RE})*)(?:\s{{2,}}|\t+|$)"
)
FLAG_CAPTURE_RE = re.compile(
    rf"(?<!\w)({AT_OPTION_RE}|{LONG_OPTION_RE}|{SHORT_OPTION_RE})"
)


@dataclass
class ManOption:
    usage: str
    description: str
    flags: List[str]
    short_flags: List[str]
    long_flags: List[str]
    argument: Optional[str] = None


@dataclass
class ManPage:
    command: str
    aliases: List[str]
    summary: str
    synopsis: List[str]
    options: List[ManOption]
    examples: List[Dict[str, str]]
    sections: Dict[str, str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def parse_man_page(text: str, query: str = "") -> ManPage:
    sections = parse_man_sections(text)

    command, aliases, summary = _parse_name_section(
        sections.get("NAME", ""), fallback=query
    )
    known_commands = [item for item in [command, *aliases, query] if item]

    synopsis = _parse_synopsis(sections.get("SYNOPSIS", ""), known_commands)
    options = _extract_options(sections)
    examples = _extract_examples(sections, known_commands)

    if not command:
        command = _fallback_command(query=query, synopsis=synopsis)

    return ManPage(
        command=command,
        aliases=aliases,
        summary=summary,
        synopsis=synopsis,
        options=options,
        examples=examples,
        sections=sections,
    )


def _parse_name_section(text: str, fallback: str = "") -> tuple[str, List[str], str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return fallback.strip(), [], ""

    collapsed = " ".join(lines)
    match = re.match(r"^(?P<names>.+?)\s+-\s+(?P<summary>.+)$", collapsed)

    if match:
        names_text = match.group("names").strip()
        summary = _collapse_whitespace(match.group("summary"))
    else:
        names_text = lines[0]
        summary = ""

    names = [item.strip() for item in names_text.split(",") if item.strip()]
    if fallback and fallback in names:
        command = fallback
        aliases = [item for item in names if item != fallback]
    else:
        command = names[0] if names else fallback.strip()
        aliases = names[1:] if len(names) > 1 else []

    return command, aliases, summary


def _parse_synopsis(text: str, known_commands: List[str]) -> List[str]:
    lines = text.splitlines()
    entries: List[str] = []
    current: List[str] = []

    command_pattern = None
    command_names = [re.escape(item) for item in known_commands if item]
    if command_names:
        command_pattern = re.compile(rf"^(?:{'|'.join(command_names)})\b")

    for raw_line in lines:
        stripped = _collapse_whitespace(raw_line)
        if not stripped:
            continue

        starts_new = bool(command_pattern and command_pattern.match(stripped))

        if starts_new and current:
            entries.append(" ".join(current))
            current = [stripped]
            continue

        if not current:
            current = [stripped]
            continue

        current.append(stripped)

    if current:
        entries.append(" ".join(current))

    return _dedupe(entries)


def _extract_options(sections: Dict[str, str]) -> List[ManOption]:
    options: List[ManOption] = []

    for section_name in (
        "OPTIONS",
        "DESCRIPTION",
        "COMMAND-LINE OPTIONS",
        "LISTING OPTIONS",
    ):
        section_text = sections.get(section_name, "")
        if not section_text:
            continue

        options.extend(_extract_options_from_text(section_text))

    deduped: List[ManOption] = []
    seen = set()

    for option in options:
        key = option.usage.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(option)

    return deduped


def _extract_options_from_text(text: str) -> List[ManOption]:
    options: List[ManOption] = []
    current_header: Optional[str] = None
    current_body: List[str] = []

    for raw_line in text.splitlines():
        if _is_option_start(raw_line):
            if current_header:
                parsed = _build_option(current_header, current_body)
                if parsed:
                    options.append(parsed)
            current_header = raw_line.rstrip()
            current_body = []
            continue

        if current_header:
            current_body.append(raw_line.rstrip())

    if current_header:
        parsed = _build_option(current_header, current_body)
        if parsed:
            options.append(parsed)

    return options


def _extract_examples(
    sections: Dict[str, str], known_commands: List[str]
) -> List[Dict[str, str]]:
    examples: List[Dict[str, str]] = []

    for section_name in ("EXAMPLES", "EXAMPLE"):
        section_text = sections.get(section_name, "")
        if not section_text:
            continue
        examples.extend(_extract_examples_from_text(section_text, known_commands))

    deduped: List[Dict[str, str]] = []
    seen = set()

    for item in examples:
        cmd = item.get("cmd", "").strip()
        if not cmd or cmd in seen:
            continue
        seen.add(cmd)
        deduped.append(
            {
                "cmd": cmd,
                "desc": _collapse_whitespace(item.get("desc", "")),
            }
        )

    return deduped


def _extract_examples_from_text(
    text: str, known_commands: List[str]
) -> List[Dict[str, str]]:
    examples: List[Dict[str, str]] = []
    description_parts: List[str] = []
    command_pattern = _compile_command_pattern(known_commands)

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        if _looks_like_example_command(stripped, command_pattern):
            command = _strip_prompt(stripped)
            examples.append(
                {
                    "cmd": command,
                    "desc": _collapse_whitespace(" ".join(description_parts)),
                }
            )
            description_parts = []
            continue

        description_parts.append(_normalize_example_description(stripped))

    return examples


def _build_option(header: str, body: List[str]) -> Optional[ManOption]:
    match = OPTION_DECL_RE.match(header)
    if not match:
        return None

    usage = _collapse_whitespace(match.group("usage"))
    description_parts = []

    tail = header[match.end() :].strip()
    if tail:
        description_parts.append(tail)

    description_parts.extend(line.strip() for line in body if line.strip())
    description = _collapse_whitespace(" ".join(description_parts))

    flags = [_normalize_flag(flag) for flag in FLAG_CAPTURE_RE.findall(usage)]
    flags = _dedupe(flags)

    short_flags = [
        flag for flag in flags if flag.startswith("-") and not flag.startswith("--")
    ]
    long_flags = [flag for flag in flags if flag.startswith("--")]

    return ManOption(
        usage=usage,
        description=description,
        flags=flags,
        short_flags=short_flags,
        long_flags=long_flags,
        argument=_extract_argument(usage),
    )


def _is_option_start(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.endswith(":"):
        return False

    return bool(OPTION_DECL_RE.match(line))


def _extract_argument(usage: str) -> Optional[str]:
    patterns = (
        r"--[A-Za-z0-9][A-Za-z0-9-]*\[?=(?P<arg>[A-Za-z<>\[\]\-][A-Za-z0-9_<>\[\]\-]*)\]?",
        r"(?:--[A-Za-z0-9][A-Za-z0-9-]*|-[^,\s]|@[A-Za-z0-9_<>\[\]./\-]+)\s+(?P<arg>[A-Za-z<>\[\]\-][A-Za-z0-9_<>\[\]\-]*)",
        r"@(?P<arg>[A-Za-z0-9_<>\[\]./\-]+)$",
    )

    for pattern in patterns:
        match = re.search(pattern, usage)
        if match:
            return match.group("arg").strip("<>[]")

    return None


def _normalize_flag(flag: str) -> str:
    flag = re.sub(r"\[=.*$", "", flag)
    flag = re.sub(r"\[[^\]]+\]$", "", flag)
    return flag


def _fallback_command(query: str, synopsis: List[str]) -> str:
    if query:
        return query

    for entry in synopsis:
        match = re.match(r"^([a-zA-Z0-9_\-]+)", entry)
        if match:
            return match.group(1)

    return ""


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    output = []

    for item in items:
        if item in seen:
            continue
        seen.add(item)
        output.append(item)

    return output


def _compile_command_pattern(known_commands: List[str]) -> Optional[re.Pattern[str]]:
    names = [re.escape(item) for item in known_commands if item]
    if not names:
        return None

    return re.compile(rf"^(?:{'|'.join(names)})\b")


def _looks_like_example_command(
    line: str, command_pattern: Optional[re.Pattern[str]]
) -> bool:
    if line.startswith(("$ ", "# ")):
        return True

    if command_pattern and command_pattern.match(line):
        return True

    if command_pattern and any(token in line for token in ("|", ";", "&&")):
        return bool(command_pattern.search(line))

    return False


def _strip_prompt(line: str) -> str:
    if line.startswith(("$ ", "# ")):
        return line[2:].strip()

    return line.strip()


def _normalize_example_description(line: str) -> str:
    return line.lstrip("-* ").strip()
