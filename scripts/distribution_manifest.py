#!/usr/bin/env python3
"""Validate the collection's own metadata and the host manifests that project it.

distribution.json carries the canonical name, publisher UUID and release version; the
per-host manifests are projections of it, so what this checks is agreement rather than
each file on its own. That is a different subject from whether a skill folder is
well formed, and it shares no helper with it — notably it reports through print
directly and never through the skill validator's fail(), which is what let it move out
whole.

Standard library only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from diagnostic_text import printable
from read_whole import Unread, whole
from skill_model import NAME_PATTERN
from workspace_files import listed


VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

# Maintained, not derived, and deliberately so: which JSON file is a host manifest has no
# reliable signal to derive from — `.claude-plugin/marketplace.json` is one and carries no
# version at all — whereas a versioned install ref identifies itself, which is why the pin
# scan below derives and this does not.
#
# The cost is unguarded and stated rather than explained away: nothing catches a host
# manifest this tuple does not name, so adding a host means editing here. read_json_object
# covers a registered file that disappears, which is the direction the list already covers,
# not this one. Registered as `host-manifest-list-unguarded-additions`.
HOST_VERSION_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
)


HOST_DESCRIPTION_MANIFESTS = HOST_VERSION_MANIFESTS + (".claude-plugin/marketplace.json",)


# Presence only. Which files must carry a pin cannot be derived — an unpinned ref is
# a documented form — so this list answers the one direction the scan cannot.
PINNED_INSTALL_DOCS = (
    ".opencode/INSTALL.md",
    "README.md",
    "tools/fornax-cli/README.md",
)


@dataclass(frozen=True)
class DistributionValidation:
    passed: bool
    publisher_id: str | None


def read_json_object(path: Path) -> tuple[dict | None, str | None]:
    """Read one UTF-8 JSON object and return a diagnostic instead of raising."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeError:
        return None, "must use UTF-8"
    except (OSError, json.JSONDecodeError) as error:
        return None, str(error)
    if not isinstance(value, dict):
        return None, "must contain a JSON object"
    return value, None


def described_paths(manifest: dict) -> list[tuple[str, str]]:
    """Every description a host manifest carries, labelled by where it sits."""
    found = []

    if isinstance(manifest.get("description"), str):
        found.append(("description", manifest["description"]))

    for index, plugin in enumerate(manifest.get("plugins", [])):
        if isinstance(plugin, dict) and isinstance(plugin.get("description"), str):
            found.append((f"plugins[{index}].description", plugin["description"]))

    return found


def validate_projected_descriptions(root: Path, canonical: str) -> bool:
    """Require each host description to open with the canonical one.

    A prefix rather than an equality: a host may append to the canonical sentence
    — host-packaging.md calls these projections, and per-surface additions are
    legitimate — but may not replace it with a rewrite of its own.

    The canonical value arrives already validated. Judging it here made the one
    function scoped to projections the only place a distribution.json field defect
    was reported, so a caller reading `FAIL distribution.json` was looking at the
    projection loop for a rule that belongs beside name, version and publisher_id.
    """
    failed = False

    for relative_path in HOST_DESCRIPTION_MANIFESTS:
        path = root / relative_path
        manifest, error = read_json_object(path)
        if error is not None:
            if relative_path not in HOST_VERSION_MANIFESTS:
                print(printable(f"FAIL {relative_path} - {error}"))
                failed = True
            continue
        assert manifest is not None
        if not isinstance(manifest.get("plugins", []), list):
            print(f"FAIL {relative_path} - plugins must be a list")
            failed = True
            continue

        for label, description in described_paths(manifest):
            if not description.startswith(canonical):
                print(
                    f"FAIL {relative_path} - {label} must open with the description in "
                    "distribution.json"
                )
                failed = True

    return failed


WORD_QUOTES = "\"'`"
# git-check-ref-format forbids these anywhere in a ref name, and forbids whitespace,
# which is what bounds an unquoted one below. A set git specifies, not a guess about
# what a document puts next.
RELEASE_REF = re.compile(r"v[^\s~^:?*\[\\]+")


def install_refs(text: str, repository: str) -> tuple[list[str], list[Unread]]:
    """Every release ref the text documents installing from *repository*, read whole.

    Form after form of this said where a ref ends by listing what may follow it, and
    each list was short by a character a later document used: `+`, then `;`, `|` and
    `>`, then `_` and `/`. Each shortfall shortened a ref into one that equalled the
    expected tag and passed as current — a stale pin answering clean.

    Then the list moved rather than going away. `whole()` was called on a slice this
    function had already cut at a set of shell operators, so it proved the slice was
    complete and said nothing about the token: `@v0.4.1;old`, `@v0.4.1(rc)`,
    `@v0.4.1&next` and `@v0.4.1>old` each came back as `v0.4.1` and compared equal to
    the shipped tag. Every one of those characters is legal in a git ref name. A
    guarantee over a string the caller chose the end of is not a guarantee.

    So nothing here decides where a ref stops except grammars that own the question.
    A quoted ref ends at its closing quote — every install command in these documents
    wraps the URL in `"`, whether the surrounding text is a shell command or the JSON
    of an editor config, and `"` is a real closing delimiter. It ends there and nowhere
    else: whitespace was in the quoted token's end set as well, which is what an
    unquoted ref ends at, so `"…@v0.4.1 old"` read as `v0.4.1` and compared equal to
    the shipped tag — the same truncation as the operator lists above, arriving through
    a delimiter this docstring already claimed to be waiting for. An opening quote
    nothing closes is not a ref read to its end either, and is reported as one that
    cannot be read. An unquoted ref ends at whitespace, which git forbids inside a ref
    name. Pip's VCS URL grammar ends it at
    the `#` beginning the fragment, which is how `@v0.4.1#subdirectory=tools/` names a
    ref and a subdirectory in one URL.

    An unquoted `@v0.4.1; echo done` therefore reads as `v0.4.1;` and is reported. The
    shell would have cut it at the `;` and so would a reader, but a ref may hold one
    and this cannot tell which was meant — so it says so instead of choosing the
    reading that passes.

    `shlex` owns shell words and reads the workflow, but not this: the input is
    Markdown, so a line may hold prose, an apostrophe, or JSON, and a shell lexer reads
    those as unterminated quotes.
    """
    marker = re.compile(re.escape(repository) + r"\.git[@#]")
    refs: list[str] = []
    unreadable: list[Unread] = []
    for match in marker.finditer(text):
        index = match.start() - 1
        while index >= 0 and text[index] not in " \t\r\n" + WORD_QUOTES:
            index -= 1
        opening = text[index] if index >= 0 and text[index] in WORD_QUOTES else ""

        ends = {opening, "#"} if opening else set(" \t\r\n#")
        token: list[str] = []
        for char in text[match.end() :]:
            if char in ends:
                break
            token.append(char)

        # A ref carrying no version is a documented form, not a stale pin: tracking a
        # branch is deliberate, and only a ref already naming a release is a claim
        # about which one to install.
        if not token or token[0] != "v":
            continue
        # Where the ref ends and whether the word is closed are separate questions, and
        # answering them with one flag conflated them: `#` ends the ref inside quotes as
        # readily as outside, so `"…@v1.2.3#egg=x` with no closing quote counted the
        # fragment as the closure and read as the shipped tag. The word's closer is
        # wherever that quote character next appears, which is what the shell says too.
        if opening and opening not in text[match.end() :]:
            unreadable.append(
                Unread("".join(token), f"opens with {opening} that nothing closes")
            )
            continue
        read = whole("".join(token), RELEASE_REF, "a release ref")
        if isinstance(read, Unread):
            unreadable.append(read)
        else:
            refs.append(read.value)
    return refs, unreadable


def validate_install_pins(root: Path, repository: str, version: str) -> bool:
    """Require every documented install pin to name the release being shipped.

    The host manifests are checked above, but the commands a reader copies live
    in Markdown, and nothing compared those to distribution.json: a release that
    bumped every manifest and missed one pin shipped an install command that
    resolves to the previous tag, with every workspace check still green.

    The docs to read are derived from the workspace rather than listed here, so
    a pin added to a file nobody thought to register is judged like the rest. An
    unpinned ref is left alone: tracking the default branch is a documented form,
    not a stale pin, and only a ref already carrying a version is a claim about
    which release to install.

    Derivation and a declared set guard opposite directions, so both are here. The
    scan catches a stale pin in a file nobody registered, which a list cannot see.
    PINNED_INSTALL_DOCS catches a registered file that stops carrying a pin, which
    the scan cannot see: an unpinned ref is a documented form, so no rule over the
    text alone separates "deliberately unpinned" from "lost its pin".

    Replacing the list with the scan traded the second guarantee for the first and
    was described as only a gain. It was not.
    """
    failed = False
    expected = f"v{version}"
    carrying: set[str] = set()

    paths, error = listed(root)
    if error is not None:
        print(printable(f"FAIL distribution.json - {error}"))
        return True

    for path in sorted(paths):
        if path.suffix != ".md" or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue  # text hygiene owns unreadable files and reports them there
        refs, unreadable = install_refs(text, repository)
        relative_path = path.relative_to(root).as_posix()
        for unread in unreadable:
            print(printable(f"FAIL {relative_path} - install ref {unread}"))
            failed = True
        if not refs:
            continue
        carrying.add(relative_path)
        for stale in sorted(set(refs) - {expected}):
            print(f"FAIL {relative_path} - install ref {stale} must be {expected}")
            failed = True

    for relative_path in PINNED_INSTALL_DOCS:
        if relative_path not in carrying:
            print(f"FAIL {relative_path} - a registered install doc carrying no pin")
            failed = True

    # An emptied registry is a failure whatever the scan found. Conjoining "and the
    # scan found nothing" made this unreachable in a tree whose documents still carry
    # pins — which is every real tree, and the state the comment claimed to cover.
    if not PINNED_INSTALL_DOCS:
        print("FAIL distribution.json - no documented install pin names the release tag")
        failed = True

    return failed


def validate_distribution(root: Path) -> DistributionValidation:
    """Validate canonical distribution metadata and host projections."""
    distribution_file = root / "distribution.json"
    distribution, error = read_json_object(distribution_file)
    if error is not None:
        print(printable(f"FAIL distribution.json - {error}"))
        return DistributionValidation(False, None)
    assert distribution is not None

    failed = False
    name = distribution.get("name")
    version = distribution.get("version")
    publisher_id = distribution.get("publisher_id")
    description = distribution.get("description")
    skills_directory = distribution.get("skills_directory")
    repository = distribution.get("repository")
    if distribution.get("schema") != 1:
        print("FAIL distribution.json - schema must be 1")
        failed = True
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        print("FAIL distribution.json - name must use lowercase hyphen-case")
        failed = True
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        print("FAIL distribution.json - version must use semantic version format x.y.z")
        failed = True
    if not isinstance(description, str) or not description:
        print("FAIL distribution.json - description must be a non-empty string")
        failed = True
    canonical_publisher: str | None = None
    if not isinstance(publisher_id, str):
        print("FAIL distribution.json - publisher_id must be a UUID")
        failed = True
    else:
        try:
            parsed_publisher = str(UUID(publisher_id))
        except ValueError:
            print("FAIL distribution.json - publisher_id must be a UUID")
            failed = True
        else:
            if publisher_id != parsed_publisher:
                print(
                    "FAIL distribution.json - publisher_id must use canonical lowercase UUID form"
                )
                failed = True
            else:
                canonical_publisher = parsed_publisher
    if skills_directory != "skills":
        print("FAIL distribution.json - skills_directory must be skills")
        failed = True

    for relative_path in HOST_VERSION_MANIFESTS:
        path = root / relative_path
        manifest, error = read_json_object(path)
        if error is not None:
            print(printable(f"FAIL {relative_path} - {error}"))
            failed = True
            continue
        assert manifest is not None
        if manifest.get("name") != name:
            print(f"FAIL {relative_path} - name must match distribution.json")
            failed = True
        if manifest.get("version") != version:
            print(f"FAIL {relative_path} - version must match distribution.json")
            failed = True

    # Only when there is a release to compare pins against. An unusable version is
    # already reported above, and every pinned doc would repeat it once more.
    if isinstance(version, str) and VERSION_PATTERN.fullmatch(version):
        if not isinstance(repository, str) or not repository:
            print("FAIL distribution.json - repository must be a non-empty string to check pins")
            failed = True
        elif validate_install_pins(root, repository, version):
            failed = True

    # Only when there is a canonical sentence to project. Without one the failure is
    # already reported above, and every host would repeat it once more.
    if isinstance(description, str) and description:
        if validate_projected_descriptions(root, description):
            failed = True

    if not failed:
        print(printable(f"OK   distribution {name} {version}"))
    return DistributionValidation(not failed, canonical_publisher)
