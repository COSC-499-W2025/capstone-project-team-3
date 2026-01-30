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

def parse_documents_to_json(file_paths, output_path):
    """
    Parse non-code documents and save results to JSON.
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
    
    # Save to JSON
    output_data = {"files": results}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Return the parsed object in JSON format
    return output_data


def parsed_input_text(file_paths_dict, repo_path=None, author=None):
    """
    Parse non-code files with different strategies based on collaboration status.
    - Non-collaborative files: Extract FULL content + count commits
    - Collaborative files: Extract ONLY author's git contributions + count commits
    
    Args:
        file_paths_dict: Dict with "collaborative" and "non_collaborative" keys
        repo_path: Git repository path
        author: Author email
        
    Returns:
        Dictionary with parsed_files array with contribution_frequency for each file
    """
    results = []
    
    # Get commit counts for ALL files once (efficient)
    commit_counts = {}
    if repo_path and author:
        commit_counts = _get_all_file_commit_counts(repo_path, author)
    
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
            "contribution_frequency": commit_counts.get(str(file_path.resolve()), 1)
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
            author_data = _parse_collaborative_files(repo_path, author, commit_counts)
            results.extend(author_data)
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

def _get_all_file_commit_counts(repo_path, author):
    """Get commit counts for ALL non-code files by author (single call)."""
    try:
        from app.utils.git_utils import extract_non_code_content_by_author
        import json
        
        commits_json = extract_non_code_content_by_author(
            repo_path, author, exclude_readme=True, exclude_pdf_docx=True
        )
        commits = json.loads(commits_json)
        
        counts = {}
        # Git returns paths relative to repo root, so resolve relative to repo_path
        repo_base = Path(repo_path).resolve()
        for commit in commits:
            for file_data in commit.get("files", []):
                file_path = file_data.get("path_after") or file_data.get("path_before", "")
                if file_path:
                    # Join with repo_base to get absolute path
                    resolved = str((repo_base / file_path).resolve())
                    counts[resolved] = counts.get(resolved, 0) + 1
        
        return counts
    except Exception:
        return {}

def _parse_collaborative_files(repo_path, author, commit_counts):
    """Parse collaborative files - extract only author's patches."""
    try:
        from app.utils.git_utils import extract_non_code_content_by_author
        import json
        
        commits_json = extract_non_code_content_by_author(
            repo_path, author, exclude_readme=True, exclude_pdf_docx=True
        )
        commits = json.loads(commits_json)
        
        # Git returns paths relative to repo root, so resolve relative to repo_path
        repo_base = Path(repo_path).resolve()
        
        file_patches = {}
        for commit in commits:
            for file_data in commit.get("files", []):
                file_path = file_data.get("path_after") or file_data.get("path_before", "")
                if not file_path:
                    continue
                
                # Resolve relative to repo_path for consistency with commit_counts
                resolved = str((repo_base / file_path).resolve())
                    
                if resolved not in file_patches:
                    file_patches[resolved] = {"name": Path(file_path).name, "patches": []}
                file_patches[resolved]["patches"].append(file_data.get("patch", ""))
        
        results = []
        for resolved, data in file_patches.items():
            results.append({
                "path": resolved,
                "name": data["name"],
                "type": Path(resolved).suffix.lower().lstrip('.'),
                "content": "\n\n".join(data["patches"]),
                "success": True,
                "error": "",
                "contribution_frequency": commit_counts.get(resolved, 1)
            })
        
        return results
    except Exception as e:
        print(f"Error parsing collaborative files: {e}")
        return []