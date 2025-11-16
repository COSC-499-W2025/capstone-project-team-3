
def get_git_user_identity(repo_path: Union[str, Path]) -> Dict[str, str]:
    """
    Get the current git user's identity (name and email) from the repository.
    REUSES: get_repo() from git_utils.py
    
    Args:
        repo_path: Path to git repository
        
    Returns:
        Dict with 'name' and 'email' keys, or empty dict if not found
    """
    try:
        repo = get_repo(repo_path)  # REUSED from git_utils.py
        config_reader = repo.config_reader()
        
        name = config_reader.get_value("user", "name", default="")
        email = config_reader.get_value("user", "email", default="")
        
        return {
            "name": name,
            "email": email
        }
    except Exception:
        return {}


def verify_user_in_files(
    file_metadata: Dict[str, Dict[str, Any]],
    user_email: str
) -> Dict[str, List[str]]:
    """
    Verify which files the user actually contributed to vs files by others only.
    
    Ensures collaborative files have user + at least 1 other person.
    Ensures non-collaborative files have ONLY the user.
    
    Args:
        file_metadata: Output from collect_git_non_code_files_with_metadata()
        user_email: Email of the user to verify
    
    Returns:
        {
            "user_collaborative": [paths],    # Files with user + at least 1 other
            "user_solo": [paths],             # Files with ONLY user
            "others_only": [paths]            # Files WITHOUT user
        }
    """
    user_collaborative = []
    user_solo = []
    others_only = []
    
    for file_path, info in file_metadata.items():
        authors = info.get("authors", [])
        
        if user_email in authors:
            # User IS an author
            if len(authors) == 1:
                # ONLY user (solo work)
                user_solo.append(info["path"])
            else:
                # User + at least 1 other person (collaborative)
                user_collaborative.append(info["path"])
        else:
            # User is NOT an author (others' work)
            others_only.append(info["path"])
    
    return {
        "user_collaborative": user_collaborative,
        "user_solo": user_solo,
        "others_only": others_only
    }


def classify_non_code_files_with_user_verification(
    directory: Union[str, Path],
    user_email: str = None
) -> Dict[str, Any]:
    """
    Classify non-code files as collaborative or non-collaborative with user verification.
    REUSES: detect_git(), get_repo() from git_utils.py
           scan_project_files() from scan_utils.py
           filter_non_code_files() from this module
    
    Classification logic:
    - COLLABORATIVE: Git repo + 2+ authors + user is one of them
    - NON-COLLABORATIVE: 
        * Git repo + only 1 author (user) 
        * OR local files (non-git)
    
    Args:
        directory: Path to directory/repository
        user_email: Email of user (if None, gets from git config for git repos)
    
    Returns:
        {
            "is_git_repo": bool,
            "user_identity": {"name": str, "email": str} or {},
            "collaborative": [paths],        # Git + 2+ authors + user is author
            "non_collaborative": [paths],    # Git + user only OR local files
            "excluded": [paths]              # Git + user NOT author
        }
    """
    directory = Path(directory)
    
    # REUSED: detect_git() from git_utils.py
    if is_directory_git_repo(directory):
        # Git repository - get user identity
        if user_email is None:
            user_identity = get_git_user_identity(directory)
            user_email = user_identity.get("email", "")
        else:
            user_identity = {"name": "", "email": user_email}
        
        if not user_email:
            # Can't determine user - treat as error case
            return {
                "is_git_repo": True,
                "user_identity": {},
                "collaborative": [],
                "non_collaborative": [],
                "excluded": [],
                "error": "Could not determine git user identity"
            }
        
        # Collect git metadata (uses get_repo internally)
        metadata = collect_git_non_code_files_with_metadata(directory)
        
        # Verify user in files
        verified = verify_user_in_files(metadata, user_email)
        
        return {
            "is_git_repo": True,
            "user_identity": user_identity,
            "collaborative": verified["user_collaborative"],      # Git + 2+ authors + user
            "non_collaborative": verified["user_solo"],           # Git + user only
            "excluded": verified["others_only"]                   # Git + user NOT author
        }
    else:
        # Non-git directory - REUSE scan_project_files + filter_non_code_files
        all_files = scan_project_files(str(directory))
        local_files = filter_non_code_files(all_files)
        
        return {
            "is_git_repo": False,
            "user_identity": {},
            "collaborative": [],                                  # No git = no collaboration
            "non_collaborative": local_files,                     # All local files
            "excluded": []
        }

