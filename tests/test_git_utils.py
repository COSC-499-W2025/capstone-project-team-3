from app.utils.git_utils import detect_git
from git import Repo


def test_detect_git_with_git_repo(tmp_path):
    """
    Test for when a git folder path is specified
    """
    Repo.init(tmp_path)
    assert detect_git(tmp_path) is True
    
def test_detect_git_with_folder(tmp_path):
    """
    Test for when a plain folder without git is specified
    """
    assert detect_git(tmp_path) is False

