import shutil
import subprocess
import sysconfig
import tomllib
from pathlib import Path

import pytest


def find_repo_root():
    # Walk up from this file until the directory holding pyproject.toml, rather
    # than indexing parents[], so moving the test does not silently break it.
    for parent in Path(__file__).resolve().parents:
        if (parent / 'pyproject.toml').exists():
            return parent
    raise RuntimeError(f'pyproject.toml not found above {__file__}')


REPO_ROOT = find_repo_root()


def find_bump_my_version():
    found = shutil.which('bump-my-version')
    if found:
        return found
    candidate = Path(sysconfig.get_path('scripts')) / 'bump-my-version'
    return str(candidate) if candidate.exists() else None


BUMP_MY_VERSION = find_bump_my_version()


@pytest.mark.skipif(BUMP_MY_VERSION is None, reason='bump-my-version is not installed')
def test_pyproject_bump_config(tmp_path):
    pyproject = tmp_path / 'pyproject.toml'
    shutil.copy2(REPO_ROOT / 'pyproject.toml', pyproject)

    before = tomllib.loads(pyproject.read_text(encoding='utf-8'))['project']['version']
    major, minor, patch = before.split('.')
    expected = f'{major}.{minor}.{int(patch) + 1}'

    result = subprocess.run(
        [BUMP_MY_VERSION, 'bump', 'patch', '--no-commit', '--no-tag'],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    bumped = tomllib.loads(pyproject.read_text(encoding='utf-8'))['project']['version']
    assert bumped == expected
