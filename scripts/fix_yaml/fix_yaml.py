"""Fix linting errors from YAML files."""

from __future__ import annotations

import subprocess
from itertools import chain
from logging import INFO, basicConfig, info
from pathlib import Path
from typing import Iterable, TextIO

from pathspec import PathSpec

basicConfig(level=INFO)


class RootError(Exception):
    """Script not called from root exception."""

    def __init__(self: RootError) -> None:
        """RootError init."""
        self.message = "Call this script from root."
        super().__init__(self.message)


def load_lines_gitignore() -> list[str]:
    """Load lines from .gitignore file content."""
    path = Path(".gitignore")

    if not path.is_file():
        raise RootError

    with path.open() as file:
        lines = file.readlines()

    file.close()

    return lines


def find_yaml_files(source: str = ".") -> Iterable[Path]:
    """Find YAML files from source using glob patterns."""
    return chain(Path(source).glob("**/*.yml"), Path(source).glob("**/*.yaml"))


def fix_file_endings(path: str) -> None:
    """Fix file endings from CRLF to LF."""
    file: TextIO

    with Path.open(path, "rb") as file:
        content = file.read()

    content = content.replace(b"\r\n", b"\n")

    with Path.open(path, "wb") as file:
        file.write(content)

    file.close()


def run_yamlfix_file(path: str) -> str:
    """Run yamlfix on path and return process stderr."""
    return subprocess.run(
        f"poetry run yamlfix {path}",  # noqa: S603
        check=False,
        capture_output=True,
        text=True,
    ).stderr


def fix_yaml_files() -> None:
    """Fix all YAML files in the project.

    Find all YAML files in the project excluding paths from .gitignore.

    For each file:
      Run yamlfix on file

      if file was fixed
        Fix line endings from CRLF to LF.
    """
    paths_gitignore = PathSpec.from_lines("gitwildmatch", load_lines_gitignore())

    for yaml_file in find_yaml_files():
        if paths_gitignore.match_file(yaml_file):
            continue

        result = run_yamlfix_file(yaml_file)

        if result.find("1 fixed") != -1:
            fix_file_endings(yaml_file)

        info(f"Run yamlfix on file -> {yaml_file}\n{result}")
