from pathlib import Path
from typing import Union
import zipfile
import tempfile

def is_existing_path(path: Union[str, Path]) -> bool:
    """
    Return True if `path` exists (file or directory).
    Raises ValueError if path is None.
    """
    if path is None:
        raise ValueError("path must be provided")

    p = Path(path)
    return p.exists()

def is_zip_file(path: Union[str, Path]) -> bool:
    """
    Check whether the given file is a valid zip file.

    Returns True if it is a valid zip file, False otherwise.
    Raises ValueError if path is None or does not exist.
    """

    if path is None:
        raise ValueError("path must be provided")

    p = Path(path)

    if not p.exists():
        raise ValueError(f"The path '{p}' does not exist.")

    if not p.is_file():
        raise ValueError(f"The path '{p}' is not a file.")

    # Check if the file is a valid ZIP
    return zipfile.is_zipfile(p)

def extract_zipped_contents(path: Union[str, Path]) -> bool:
    """
    Extracts the contents of the zipped file to a temporary folder.
    Returns True if the extraction of contents runs successfully
    Raises ValueError if path is None.
    Raise ValueError if it is not a valid zipped file or something went wrong during extraction
    """
    if path is None:
        raise ValueError("path must be provided")
    
    zipped_path = Path(path)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        with zipfile.ZipFile(zipped_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return True
    except zipfile.BadZipFile:
        raise ValueError(f"The file {zipped_path} is not a valid zip archive.")
    except Exception as e:
        raise RuntimeError(f"An error occured during extraction: {e}")