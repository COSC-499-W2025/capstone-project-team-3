"""
Document parser for non-code files.
"""
import json
from pathlib import Path
from .file_size_checker import is_file_too_large, MAX_FILE_SIZE_MB


# If they're not installed, we keep their names as None and raise the
# same informative errors later when extraction is attempted.
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    import docx
except Exception:
    docx = None

def parse_documents_to_json(file_paths, output_path, repo_path=None, author=None):
    """
    Parse non-code documents and save results to JSON.
    If repo_path and author provided, also include author contributions.
    """
    results = []

    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        result = {
            "path": str(file_path),
            "name": file_path.name,
            "type": file_path.suffix.lower().lstrip('.'),
            "content": "",
            "success": False,
            "error": ""
        }

        try:
            if not file_path.exists():
                result["error"] = "File does not exist"
            elif is_file_too_large(file_path):
                result["error"] = f"File size exceeds {MAX_FILE_SIZE_MB} MB limit"
            elif file_path.suffix.lower() == '.pdf':
                result["content"] = _extract_pdf_text(file_path)
                result["success"] = True
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                result["content"] = _extract_word_text(file_path)
                result["success"] = True
            elif file_path.suffix.lower() in ['.txt', '.md', '.markdown']:
                result["content"] = _extract_text_file(file_path)
                result["success"] = True
            else:
                result["error"] = f"Unsupported file type: {file_path.suffix}"
            


        except Exception as e:
            result["error"] = str(e)

        results.append(result)

    # Add author contributions if repo_path and author provided
    if repo_path and author:
        try:
            author_data = parse_author_contributions(repo_path, author)
            if author_data.get("parsed_files"):
                for file_data in author_data["parsed_files"]:
                    file_data["is_author_only"] = True
                results.extend(author_data["parsed_files"])
        except Exception as e:
            print(f"Warning: Could not parse author contributions: {e}")
    
    # Save to JSON
    output_data = {"files": results}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Return the parsed object in JSON format
    return output_data


def parsed_input_text(file_paths_dict, repo_path=None, author=None):
    """
    Parse non-code files with different strategies based on collaboration status.
    - Non-collaborative files: Extract FULL content
    - Collaborative files: Extract ONLY author's git contributions
    
    Args:
        file_paths_dict: Dict with "collaborative" and "non_collaborative" keys
        repo_path: Git repository path (required for collaborative files)
        author: Author email (required for collaborative files)
        
    Returns:
        Dictionary with parsed_files array:
        {
            "parsed_files": [
                {
                    "path": "string",
                    "name": "string", 
                    "type": "string",
                    "content": "string",
                    "success": bool,
                    "error": "string",
                    "is_author_only": bool  # True for collaborative files
                }
            ]
        }
    """
    results = []
    
    # Parse NON-COLLABORATIVE files - extract FULL content
    for file_path_str in file_paths_dict.get("non_collaborative", []):
        file_path = Path(file_path_str)
        result = {
            "path": str(file_path.resolve()),
            "name": file_path.name,
            "type": file_path.suffix.lower().lstrip('.') if file_path.suffix else "unknown",
            "content": "",
            "success": False,
            "error": "",
            "contribution_frequency": 1
        }

        try:
            if not file_path.exists():
                result["error"] = "File does not exist"
            elif is_file_too_large(file_path):
                result["error"] = f"File size exceeds {MAX_FILE_SIZE_MB} MB limit"
            elif file_path.suffix.lower() == '.pdf':
                result["content"] = _extract_pdf_text(file_path)
                result["success"] = True
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                result["content"] = _extract_word_text(file_path)
                result["success"] = True
            elif file_path.suffix.lower() in ['.txt', '.md', '.markdown']:
                result["content"] = _extract_text_file(file_path)
                result["success"] = True
            else:
                result["error"] = f"Unsupported file type: {file_path.suffix}"
        except Exception as e:
            result["error"] = str(e)

        results.append(result)
    
    # Parse COLLABORATIVE files - extract ONLY author's contributions from git
    if repo_path and author and file_paths_dict.get("collaborative"):
        try:
            author_data = parse_author_contributions(repo_path, author)
            if author_data.get("parsed_files"):
                results.extend(author_data["parsed_files"])
        except Exception as e:
            print(f"Warning: Could not parse author contributions: {e}")
    
    return {"parsed_files": results}

def _extract_pdf_text(file_path):
    """Extract text from PDF file."""
    try:
        if PdfReader is None:
            raise ImportError
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                # page.extract_text() may return None for pages with no extractable text
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            return text.strip()
    except ImportError:
        raise Exception("pypdf not installed")
    except Exception as e:
        raise Exception(f"PDF extraction failed: {e}")

def _extract_word_text(file_path):
    """Extract text from Word document."""
    try:
        import docx
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        return text.strip()
    except ImportError:
        raise Exception("python-docx not installed")
    except Exception as e:
        raise Exception(f"Word extraction failed: {e}")

def _extract_text_file(file_path):
    """Extract text from plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
    except Exception as e:
        raise Exception(f"Text extraction failed: {e}")

def parse_author_contributions(repo_path, author, include_merges=False, max_commits=None):
    """
    Parse non-code file contributions by a specific author from a git repository.
    REUSES: extract_non_code_content_by_author() from git_utils and existing parsing logic.
    
    Args:
        repo_path: Path to git repository
        author: Author name or email to filter by
        include_merges: Include merge commits (default: False)
        max_commits: Maximum number of commits to process (default: None)
    
    Returns:
        Dictionary with parsed_files array containing author's contributions:
        {
            "parsed_files": [
                {
                    "path": "string",
                    "name": "string",
                    "type": "string",
                    "content": "string",  # Author's diff/patch content
                    "success": bool,
                    "error": "string",
                    "commit_hash": "string",
                    "commit_message": "string",
                    "authored_datetime": "string"
                }
            ]
        }
    """
    try:
        from app.utils.git_utils import extract_non_code_content_by_author
        import json
        
        # Get author's non-code contributions from git (excluding README files)
        commits_json = extract_non_code_content_by_author(
            repo_path, author, exclude_readme=True, exclude_pdf_docx=True,
            include_merges=include_merges, max_commits=max_commits
        )
        commits = json.loads(commits_json)
        
        results = []
        file_commit_count = {}
        
        # Count commits per file and aggregate content
        for commit in commits:
            for file_data in commit.get("files", []):
                file_path = file_data.get("path_after") or file_data.get("path_before", "")
                
                if file_path not in file_commit_count:
                    file_commit_count[file_path] = {
                        "count": 0,
                        "content": [],
                        "name": Path(file_path).name if file_path else "unknown",
                        "type": Path(file_path).suffix.lower().lstrip('.') if file_path else "unknown"
                    }
                
                file_commit_count[file_path]["count"] += 1
                file_commit_count[file_path]["content"].append(file_data.get("patch", ""))
        
        # Create results with aggregated content and contribution frequency
        for file_path, data in file_commit_count.items():
            result = {
                "path": file_path,
                "name": data["name"],
                "type": data["type"],
                "content": "\n\n".join(data["content"]),
                "success": True,
                "error": "",
                "contribution_frequency": data["count"]
            }
            results.append(result)
        
        return {"parsed_files": results}
    
    except Exception as e:
        return {
            "parsed_files": [],
            "error": f"Failed to parse author contributions: {str(e)}"
        }