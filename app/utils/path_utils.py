from pathlib import Path
from typing import Union


def is_existing_directory(path: Union[str, Path]) -> bool:
    """
    Return True if `path` exists and is a directory.
    Raises ValueError if path is None.
    """
    if path is None:
        raise ValueError("path must be provided")
    p = Path(path)
    return p.exists()