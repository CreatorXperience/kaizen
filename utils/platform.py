import platform


def get_platform():
    system = platform.system().lower()

    if system == "darwin":
        return "macos"

    if system == "linux":
        return "linux"

    return "unknown"
