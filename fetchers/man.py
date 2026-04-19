import subprocess
from typing import Optional
from parsers.man_normalizer import normalize_man_text


# def fetch_man_page(command: str) -> Optional[str]:
#     """
#     Fetch man page for a command
#     """

#     try:
#         # use col -b to remove backspaces formatting
#         result = subprocess.run(
#             f"man {command} | col -b",
#             shell=True,
#             capture_output=True,
#             text=True
#         )

#         if result.returncode != 0:
#             return None

#         output = result.stdout.strip()

#         if not output:
#             return None

#         return output

#     except Exception:
#         return None


def fetch_man_page(command: str):

    try:
        result = subprocess.run(["man", command], capture_output=True, text=True)

        if result.returncode != 0:
            return None

        text = _strip_terminal_formatting(result.stdout)

        return normalize_man_text(text)

    except Exception:
        return None


def _strip_terminal_formatting(text: str) -> str:
    try:
        result = subprocess.run(
            ["col", "-b"],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception:
        pass

    return text.replace("\b", "")
