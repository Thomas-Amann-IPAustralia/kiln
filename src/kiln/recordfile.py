"""One file per record: YAML front matter that is the record, then a Markdown rendering of it.

Machines read the front matter; Tom reads the body, often on a phone. The two must never
disagree, so a record file is valid only if it is byte-for-byte what its record renders to:
the canonical front matter, then the body its renderer produces. An edit to either half that
is not re-rendered is caught, and the file's content hash identifies one exact version.

`kiln records render` rewrites a hand-edited file into that canonical form.
"""

from __future__ import annotations

import os
import re
import tempfile
import unicodedata
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, cast

import yaml
from pydantic import BaseModel, ValidationError

from kiln.errors import KilnError

FENCE = "---\n"
_SLUG_MAX = 60

M = TypeVar("M", bound=BaseModel)


class _Dumper(yaml.SafeDumper):
    """Canonical YAML: block style, key order as the model declares it, multi-line text as a
    literal block so it reads as written."""


def _represent_str(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar(  # pyright: ignore[reportUnknownMemberType]
        "tag:yaml.org,2002:str", value, style=style
    )


_Dumper.add_representer(str, _represent_str)


def front_matter(record: BaseModel) -> str:
    """The record as canonical YAML: its id first, then its fields in the model's order."""
    data = record.model_dump(mode="json")
    if "id" in data:
        data = {"id": data.pop("id"), **data}
    return yaml.dump(data, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100)


def compose(record: BaseModel, body: str) -> str:
    """The whole file: front matter between fences, a blank line, then the body."""
    return FENCE + front_matter(record) + FENCE + "\n" + body.rstrip("\n") + "\n"


def split(text: str, *, item: str) -> dict[str, Any]:
    """The front matter of a record file, parsed but not yet validated."""
    if not text.startswith(FENCE):
        raise KilnError("a record file must open with `---` front matter", item=item)
    end = text.find("\n" + FENCE, len(FENCE) - 1)
    if end == -1:
        raise KilnError("the front matter has no closing `---`", item=item)
    try:
        data: object = yaml.safe_load(text[len(FENCE) : end + 1])
    except yaml.YAMLError as exc:
        raise KilnError(f"the front matter is not valid YAML: {exc}", item=item) from exc
    if not isinstance(data, dict):
        raise KilnError("the front matter must be a mapping of fields", item=item)
    return {str(key): value for key, value in cast("dict[object, Any]", data).items()}


def parse(text: str, model: type[M], *, item: str) -> M:
    """Validate a record file's front matter as `model`. The body is not checked here."""
    try:
        return model.model_validate(split(text, item=item))
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "(record)"
        raise KilnError(
            f"invalid {model.__name__} ({exc.error_count()} problem(s)); first: "
            f"{where}: {first['msg']}",
            item=item,
        ) from exc


def load(text: str, model: type[M], render: Callable[[M], str], *, item: str) -> M:
    """Validate a record file, and require it to be exactly its record's rendering."""
    record = parse(text, model, item=item)
    if text != compose(record, render(record)):
        raise KilnError(
            "the file is not its record's rendering: the body or the layout was edited by "
            "hand. Edit the front matter, then run `kiln records render`",
            item=item,
            see="src/kiln/recordfile.py",
        )
    return record


def slugify(title: str) -> str:
    """A file-name slug: lower-case ASCII words joined by hyphens, at most 60 characters."""
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", ascii_title.lower())
    slug = ""
    for word in words:
        candidate = f"{slug}-{word}" if slug else word
        if len(candidate) > _SLUG_MAX:
            break
        slug = candidate
    if not slug:
        raise ValueError(f"a title needs at least one letter or digit: {title!r}")
    return slug


def write_atomic(path: Path, text: str, *, exclusive: bool = False) -> None:
    """Write `text` to `path` all at once. With `exclusive`, refuse to replace a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        if exclusive:
            try:
                os.link(tmp, path)
            except FileExistsError as exc:
                raise KilnError("refusing to replace an existing record", item=str(path)) from exc
        else:
            tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
