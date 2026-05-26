"""
IO helpers: serialise/deserialise LEXON data to/from JSONL files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def write_jsonl(records: list[BaseModel], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for rec in records:
            f.write(rec.model_dump_json() + "\n")


def read_jsonl(path: Path, model_cls: type[T]) -> list[T]:
    records: list[T] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(model_cls.model_validate_json(line))
    return records


def write_json(obj: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(obj.model_dump_json(indent=2))


def write_text(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
