#!/usr/bin/env python3
import platform
import re
import subprocess
import sys

"""
This script is intended to take in the stdin/stderr from the API
like so:

    uv run task api 2>&1 | uv run python ../dev/email_login_code_notifier.py

(`dev api` does this on macOS). In development the API logs the code as
"LOGIN CODE: XXXXXX".

when the script encounters what looks like a login code, it'll show
a desktop notification with the code and copy the code to the clipboard.
"""


def notify(code: str) -> None:
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "Found login code {code}. Copied to clipboard" with title "Polar login email" sound name "default"',
                "-e",
                f'set the clipboard to "{code}"',
            ],
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def main() -> None:
    # Only works on macOS
    assert platform.system() == "Darwin"

    # A decode error or crash here would close the pipe and take the API down with it
    sys.stdin.reconfigure(errors="replace")

    # Pattern to match login codes in the API's dev log
    pattern = re.compile(r"LOGIN CODE:\s*([0-9A-Z]{6})")

    for line in sys.stdin:
        # Print first to maintain stream flow, even if notifying is slow or fails
        print(line, end="", flush=True)

        for match in pattern.findall(line):
            notify(match)


if __name__ == "__main__":
    main()
