"""One error type for every failure a person has to act on.

Failure is loud (CLAUDE.md, working principle 2): a command that cannot do its job exits with
code 2 and prints one line naming the cause, the item and where to read more.
"""

from __future__ import annotations

EXIT_FAILURE = 2


class KilnError(Exception):
    """A failure with a one-line cause, the item it concerns and a pointer to the detail."""

    def __init__(self, cause: str, *, item: str | None = None, see: str | None = None) -> None:
        super().__init__(cause)
        self.cause = cause
        self.item = item
        self.see = see

    def one_line(self) -> str:
        parts = [self.cause]
        if self.item:
            parts.append(f"item: {self.item}")
        if self.see:
            parts.append(f"see: {self.see}")
        return " | ".join(parts)
