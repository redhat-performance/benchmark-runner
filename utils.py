
import os
from pathlib import Path

def get_project_root() -> Path:
    """
    Return the root directory of the project
    """
    return os.path.dirname(Path(__file__))
