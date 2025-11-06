"""
Non-code file checker and filtering for parsing.
Reuses existing git_utils and non_code_analysis functions.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from app.utils.git_utils import detect_git, is_collaborative
from app.utils.non_code_analysis import (
    classify_local_files_as_non_code,
    classify_non_code_files_in_repo_by_collaboration,
    is_code_file
)
from app.utils.document_parser import parse_documents_to_json


def filter_and_send_non_code_files_for_parsing(
    path: Union[str, Path],
    output_json_path: str,
    author_threshold: int = 1,
    max_commits: Optional[int] = None,
    include_merges: bool = False,
    exclude_patterns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Main orchestrator function that:
    1. Detects if path is a git repo or local directory
    2. Filters non-code files (collaborative or non-collaborative)
    3. Sends filtered files to parse_documents_to_json()
    
    Args:
        path: Root directory or git repo path
        output_json_path: Where to save parsed document JSON
        author_threshold: Min authors for collaborative classification (default 1)
        max_commits: Limit commit history scan
        include_merges: Whether to include merge commits
        exclude_patterns: Directory patterns to skip (e.g., ['node_modules', '.git'])
    
    Returns:
        Dict with keys:
            - "is_git": bool
            - "is_collaborative": bool (only for git repos)
            - "non_code_files": list of file paths sent for parsing
            - "parsed_output": result from parse_documents_to_json()
    """
    path = Path(path)
    
    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")
    
    is_git = detect_git(path)
    result = {
        "is_git": is_git,
        "is_collaborative": False,
        "non_code_files": [],
        "parsed_output": None
    }
    
    non_code_file_paths = []
    
    if is_git:
        # Git repository flow
        result["is_collaborative"] = is_collaborative(path)
        
        # Get non-code files with collaboration metadata
        non_code_metadata = classify_non_code_files_in_repo_by_collaboration(
            repo_path=str(path),
            author_threshold=author_threshold,
            max_commits=max_commits,
            include_merges=include_merges
        )
        
        # Extract file paths (both collaborative and non-collaborative)
        # We want ALL non-code files from git repos
        for file_path in non_code_metadata.keys():
            full_path = path / file_path
            if full_path.exists():
                non_code_file_paths.append(str(full_path))
        
    else:
        # Local directory flow (non-git)
        result["is_collaborative"] = False  # Local files are always non-collaborative
        
        # Get non-code files from local directory
        local_non_code = classify_local_files_as_non_code(
            root=str(path),
            exclude_patterns=exclude_patterns
        )
        
        # Extract absolute paths
        non_code_file_paths = [
            info["abs_path"] 
            for info in local_non_code.values()
        ]
    
    # Filter to only parseable file types (pdf, docx, txt, md, etc.)
    parseable_files = _filter_parseable_files(non_code_file_paths)
    result["non_code_files"] = parseable_files
    
    # Send to parser
    if parseable_files:
        parsed_output = parse_documents_to_json(
            file_paths=parseable_files,
            output_path=output_json_path
        )
        result["parsed_output"] = parsed_output
    else:
        result["parsed_output"] = {"files": []}
        # Still write empty output
        import json
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump({"files": []}, f, indent=2)
    
    return result


def _filter_parseable_files(file_paths: List[str]) -> List[str]:
    """
    Filter list of file paths to only include parseable document types.
    Supported: .pdf, .docx, .doc, .txt, .md, .markdown
    """
    parseable_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md', '.markdown'}
    filtered = []
    
    for fpath in file_paths:
        ext = Path(fpath).suffix.lower()
        if ext in parseable_extensions:
            filtered.append(fpath)
    
    return filtered


def get_non_code_files_by_collaboration_status(
    repo_path: Union[str, Path],
    author_threshold: int = 1,
    max_commits: Optional[int] = None,
    include_merges: bool = False
) -> Dict[str, List[str]]:
    """
    Helper to separate non-code files into collaborative vs non-collaborative lists.
    Only works for git repositories.
    
    Returns:
        {
            "collaborative": [list of file paths],
            "non_collaborative": [list of file paths]
        }
    """
    if not detect_git(repo_path):
        raise ValueError(f"Path is not a git repository: {repo_path}")
    
    repo_path = Path(repo_path)
    
    non_code_metadata = classify_non_code_files_in_repo_by_collaboration(
        repo_path=str(repo_path),
        author_threshold=author_threshold,
        max_commits=max_commits,
        include_merges=include_merges
    )
    
    collaborative = []
    non_collaborative = []
    
    for file_path, metadata in non_code_metadata.items():
        full_path = repo_path / file_path
        if not full_path.exists():
            continue
            
        if metadata["collaborative"]:
            collaborative.append(str(full_path))
        else:
            non_collaborative.append(str(full_path))
    
    return {
        "collaborative": collaborative,
        "non_collaborative": non_collaborative
    }


def send_specific_non_code_files_for_parsing(
    file_paths: List[str],
    output_json_path: str
) -> Dict[str, Any]:
    """
    Direct function to parse a specific list of non-code file paths.
    No filtering - assumes caller has already identified non-code files.
    
    Args:
        file_paths: List of absolute paths to non-code files
        output_json_path: Where to save parsed JSON
    
    Returns:
        Result from parse_documents_to_json()
    """
    parseable = _filter_parseable_files(file_paths)
    
    if not parseable:
        import json
        empty_output = {"files": []}
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(empty_output, f, indent=2)
        return empty_output
    
    return parse_documents_to_json(
        file_paths=parseable,
        output_path=output_json_path
    )
