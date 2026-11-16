"""
Unit tests for the packaging of the OCP resource templates.

The installers render their templates from <resource>/template/ at runtime, so a template
directory missing from the published wheel leaves the installer with nothing to apply: LVMS
did exactly that in CI, where the container runs the released package while a source checkout
still had the files on disk.
"""
import fnmatch
import tomllib
from pathlib import Path

import pytest

import benchmark_runner.common.ocp_resources as ocp_resources_module

PACKAGE_PATH = Path(ocp_resources_module.__file__).parent
REPO_ROOT = PACKAGE_PATH.parents[2]
PYPROJECT_PATH = REPO_ROOT / 'pyproject.toml'
TEMPLATE_EXTENSIONS = ('.yaml', '.sh')


def _package_data() -> dict:
    with open(PYPROJECT_PATH, 'rb') as f:
        return tomllib.load(f)['tool']['setuptools']['package-data']


def _template_dirs() -> list:
    return sorted(path for path in PACKAGE_PATH.glob('*/template') if path.is_dir())


def _package(resource: str) -> str:
    return f'benchmark_runner.common.ocp_resources.{resource}.template'


def test_template_dirs_are_discovered():
    """Guard the parametrized test below: a wrong path would make it collect nothing."""
    assert {path.parent.name for path in _template_dirs()} >= {'lvms', 'lso', 'odf'}


@pytest.mark.parametrize('template_dir', _template_dirs(), ids=lambda path: path.parent.name)
def test_package_data_ships_every_template(template_dir: Path):
    """
    Every template file must be covered by a [tool.setuptools.package-data] pattern,
    otherwise it is left out of the wheel and the installer silently applies nothing.
    """
    package = _package(template_dir.parent.name)
    patterns = _package_data().get(package, [])
    templates = [path.name for path in template_dir.iterdir()
                 if path.is_file() and path.suffix in TEMPLATE_EXTENSIONS]
    assert templates, f'{package} has no templates to check'

    missing = sorted(name for name in templates
                     if not any(fnmatch.fnmatch(name, pattern) for pattern in patterns))
    assert not missing, f'{package} is missing from [tool.setuptools.package-data] in pyproject.toml for: {missing}'
