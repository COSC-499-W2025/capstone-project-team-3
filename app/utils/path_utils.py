from pathlib import Path
from typing import Union

def is_existing_path(path: Union[str, Path]) -> bool:
    """
    Return True if `path` exists (file or directory).
    Raises ValueError if path is None.
    """
    if path is None:
        raise ValueError("path must be provided")

    p = Path(path)
    return p.exists()
