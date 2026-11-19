"""A seeded finding for Semgrep: CI proves the scanner still detects (D-013).

Synthetic. Never imported, never run. The pinned rule
`python.lang.security.audit.subprocess-shell-true.subprocess-shell-true` must flag it.
"""

import subprocess


def seeded(command: str) -> None:
    subprocess.call(command, shell=True)
