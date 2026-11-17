"""Top-level pytest conftest: session-wide scrub of inherited git repo-locating variables."""

from __future__ import annotations

import os
from collections.abc import Iterator, MutableMapping

import pytest

__all__: list[str] = []

# Repo-locating variables a git hook exports into the environment of a test run.
# A test that shells out to `git init`, `git config` or `git commit` with one of
# them inherited writes into the SURROUNDING repository instead of its tmp path.
GIT_REPO_LOCATING_VARS: tuple[str, ...] = (
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_WORK_TREE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_PREFIX",
)


def scrub_inherited_git_repo_locating_env(environ: MutableMapping[str, str]) -> None:
    """Remove every repo-locating git variable from `environ`, leaving all others."""
    for var in GIT_REPO_LOCATING_VARS:
        environ.pop(var, None)


@pytest.fixture(scope="session", autouse=True)
def _scrub_inherited_git_repo_locating_env() -> Iterator[None]:
    """Scrub the inherited repo-locating git variables once for the WHOLE session."""
    saved = {var: os.environ[var] for var in GIT_REPO_LOCATING_VARS if var in os.environ}
    scrub_inherited_git_repo_locating_env(os.environ)
    yield
    os.environ.update(saved)
