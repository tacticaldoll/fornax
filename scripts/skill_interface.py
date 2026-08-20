#!/usr/bin/env python3
"""Read, validate, index, and query optional portable skill interfaces.

The sidecar intentionally uses a tiny YAML subset: one scalar ``publisher`` and
scalar list items under ``produces`` and ``consumes``. Keeping the grammar this
small lets this parser stay dependency-free and fail closed instead of growing
an incomplete general YAML parser.

Record identities use this canonical form::

    <publisher-uuid>/<record-type>@<major> <media-type>

Usage:
    .venv/bin/python scripts/skill_interface.py --skills-path skills --list
    .venv/bin/python scripts/skill_interface.py --skills-path skills --recommend RECORD
    .venv/bin/python scripts/skill_interface.py --skills-path skills \
        --recommend RECORD --prefer SKILL
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from constrained_yaml import raw_scalar
from diagnostic_text import printable


INTERFACE_FILE = "skill-interface.yaml"
RECORD_PATTERN = re.compile(
    r"^(?P<publisher>[0-9a-fA-F-]{36})/"
    r"(?P<record_type>[a-z0-9]+(?:-[a-z0-9]+)*)@"
    r"(?P<major>[1-9][0-9]*) "
    r"(?P<media_type>[a-z0-9][a-z0-9!#$&^_.+-]*/[a-z0-9][a-z0-9!#$&^_.+-]*)$",
    re.IGNORECASE,
)
TOP_LEVEL = re.compile(r"^(publisher|produces|consumes)\s*:\s*(.*?)\s*$")
LIST_ITEM = re.compile(r"^  -\s+(.+?)\s*$")


class InterfaceError(ValueError):
    """An invalid interface declaration with a user-facing diagnostic."""


@dataclass(frozen=True)
class RecordIdentity:
    publisher: str
    record_type: str
    major: int
    media_type: str

    @classmethod
    def parse(cls, value: str) -> "RecordIdentity":
        raw = value.strip()
        match = RECORD_PATTERN.fullmatch(raw)
        if not match:
            raise InterfaceError(
                "record must be '<publisher-uuid>/<record-type>@<major> <media-type>'"
            )
        try:
            publisher = str(UUID(match.group("publisher")))
        except ValueError as error:
            raise InterfaceError("record publisher must be a UUID") from error
        identity = cls(
            publisher=publisher,
            record_type=match.group("record_type").lower(),
            major=int(match.group("major")),
            media_type=match.group("media_type").lower(),
        )
        if raw != str(identity):
            raise InterfaceError(f"record must use canonical form: {identity}")
        return identity

    def __str__(self) -> str:
        return f"{self.publisher}/{self.record_type}@{self.major} {self.media_type}"


@dataclass(frozen=True)
class SkillInterface:
    skill: str
    publisher: str
    produces: tuple[RecordIdentity, ...]
    consumes: tuple[RecordIdentity, ...]
    source: str = ""


def _publisher(value: str) -> str:
    try:
        publisher = str(UUID(value.strip()))
    except ValueError as error:
        raise InterfaceError("publisher must be a UUID") from error
    if value.strip() != publisher:
        raise InterfaceError(f"publisher must use canonical form: {publisher}")
    return publisher


def _raw_scalar(value: str, number: int) -> str:
    return raw_scalar(value, number, InterfaceError)


def load(path: Path, skill: str | None = None) -> SkillInterface:
    """Load one sidecar, accepting only the documented constrained YAML shape."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeError as error:
        raise InterfaceError(f"{path.name} must use UTF-8") from error
    except OSError as error:
        raise InterfaceError(str(error)) from error

    values: dict[str, str | list[str]] = {}
    active_list: str | None = None

    for number, raw in enumerate(lines, start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = LIST_ITEM.fullmatch(raw)
        if item:
            if active_list is None:
                raise InterfaceError(f"line {number}: list item has no list field")
            assert isinstance(values[active_list], list)
            values[active_list].append(_raw_scalar(item.group(1), number))
            continue
        field = TOP_LEVEL.fullmatch(raw)
        if not field:
            raise InterfaceError(f"line {number}: unsupported YAML shape")
        key, scalar = field.groups()
        if key in values:
            raise InterfaceError(f"line {number}: duplicate {key}")
        if key in {"produces", "consumes"}:
            if scalar:
                raise InterfaceError(f"line {number}: {key} must be a block list")
            values[key] = []
            active_list = key
        else:
            if not scalar:
                raise InterfaceError(f"line {number}: publisher must not be empty")
            values[key] = _raw_scalar(scalar, number)
            active_list = None

    if "publisher" not in values:
        raise InterfaceError("missing publisher")
    publisher = _publisher(str(values["publisher"]))
    produces = tuple(RecordIdentity.parse(item) for item in values.get("produces", []))
    consumes = tuple(RecordIdentity.parse(item) for item in values.get("consumes", []))
    if not produces and not consumes:
        raise InterfaceError("declare at least one produces or consumes record")
    if len(set(produces)) != len(produces) or len(set(consumes)) != len(consumes):
        raise InterfaceError("record declarations must not contain duplicates")
    foreign = [record for record in produces if record.publisher != publisher]
    if foreign:
        raise InterfaceError("produced record publisher must match sidecar publisher")
    return SkillInterface(
        skill or path.parent.name, publisher, produces, consumes, str(path.parent.resolve())
    )


def discover(skills_path: Path) -> tuple[list[SkillInterface], list[str]]:
    """Read opt-in skill interfaces below one installed-skills directory."""
    interfaces: list[SkillInterface] = []
    errors: list[str] = []
    try:
        skill_dirs = sorted(path for path in skills_path.iterdir() if path.is_dir())
    except OSError as error:
        return [], [f"{skills_path}: {error}"]
    for skill_dir in skill_dirs:
        sidecar = skill_dir / INTERFACE_FILE
        if not sidecar.exists():
            continue
        try:
            interfaces.append(load(sidecar, skill_dir.name))
        except InterfaceError as error:
            errors.append(f"{sidecar}: {error}")
    return interfaces, errors


def recommend(
    record: RecordIdentity,
    interfaces: list[SkillInterface],
    preferences: tuple[str, ...] = (),
) -> list[SkillInterface]:
    """Return exact-match consumers, with an explicit preference winning ties."""
    matches = sorted(
        (interface for interface in interfaces if record in interface.consumes),
        key=lambda interface: (interface.skill, interface.source),
    )
    for preferred in preferences:
        preferred_matches = [interface for interface in matches if interface.skill == preferred]
        if preferred_matches:
            return preferred_matches
    return matches


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect portable skill interface declarations.")
    parser.add_argument("--skills-path", action="append", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--list", action="store_true")
    action.add_argument("--recommend", metavar="RECORD")
    parser.add_argument("--prefer", action="append", default=[], metavar="SKILL")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    interfaces: list[SkillInterface] = []
    errors: list[str] = []
    for skills_path in args.skills_path:
        found, found_errors = discover(skills_path)
        interfaces.extend(found)
        errors.extend(found_errors)
    if errors:
        for error in errors:
            print(printable(f"FAIL {error}"), file=sys.stderr)
        return 1
    if args.list:
        unique = {(item.skill, item.source): item for item in interfaces}
        for interface in sorted(unique.values(), key=lambda item: (item.skill, item.source)):
            print(printable(f"{interface.skill} ({interface.source})"))
            for record in interface.produces:
                print(f"  produces: {record}")
            for record in interface.consumes:
                print(f"  consumes: {record}")
        return 0
    try:
        record = RecordIdentity.parse(args.recommend)
    except InterfaceError as error:
        print(printable(f"FAIL {error}"), file=sys.stderr)
        return 2
    unique = {(item.skill, item.source): item for item in interfaces}
    matches = recommend(record, list(unique.values()), tuple(args.prefer))
    if len(matches) == 1:
        print(printable(f"recommended: {matches[0].skill}"))
    elif matches:
        print(
            "candidates: "
            + ", ".join(f"{interface.skill} ({interface.source})" for interface in matches)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
