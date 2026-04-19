import re
from utils.platform import get_platform


def normalize_man_text(text: str) -> str:
    system = get_platform()

    # common cleanup for ALL platforms
    text = text.replace("\t", " ")
    text = re.sub(r"\n{2,}", "\n", text)

    # macOS-specific cleanup
    if system == "macos":
        text = re.sub(r"^[A-Z]+\(\d\)\s+.*$", "", text, flags=re.MULTILINE)

    # linux-specific cleanup
    if system == "linux":
        text = re.sub(r"^\s*\w+\(\d\)\s+.*$", "", text, flags=re.MULTILINE)

    return text
