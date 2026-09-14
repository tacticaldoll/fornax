#!/usr/bin/env python3
"""Read a declared path the way any host this collection installs on would read it.

Absoluteness and parent traversal are host grammar. This repository validates on the
maintainer's machine, while the manifests and links it ships are read on the
installer's, so asking only the running host's grammar leaves the other one's holes
open. A backslash is an ordinary filename character on POSIX and a separator on
Windows, which makes "..\\shared" one filename here and a traversal there — and a
file of that name is creatable on POSIX, so the gap is reachable rather than
theoretical.

Both grammars are therefore asked, and a path either of them reads as leaving its
folder is refused. Standard library only, and no filesystem is touched, so an
installer can apply these before the target exists.
"""

from __future__ import annotations

from pathlib import PurePosixPath, PureWindowsPath


def is_absolute_anywhere(value: str) -> bool:
    """Whether either grammar reads the path as absolute or drive-relative.

    A Windows drive with no root counts. "C:x" names a location on another drive's
    current directory, which is no more relative to a skill folder than "C:/x" is.

    Only a single letter can be a drive, so real URI schemes — "https:", "mailto:" —
    are not caught here. A one-letter scheme would be, and that is the intended
    reading: none is registered, and on Windows such a prefix is a drive.
    """
    windows = PureWindowsPath(value)
    return PurePosixPath(value).is_absolute() or windows.is_absolute() or bool(windows.drive)


def has_parent_segment_anywhere(value: str) -> bool:
    """Whether either grammar reads a ".." segment in the path."""
    return ".." in PurePosixPath(value).parts or ".." in PureWindowsPath(value).parts
