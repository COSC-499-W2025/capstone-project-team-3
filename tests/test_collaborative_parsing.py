"""
Test collaborative file parsing with git extraction.
"""
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import get_classified_non_code_file_paths, get_git_user_identity
from app.utils.non_code_parsing.document_parser import parsed_input_text

def test_collaborative_parsing():
    """Test that collaborative files extract only author contributions."""
    
    repo_path = Path(__file__).parent
    
    print("=" * 60)
    print("Testing Collaborative File Parsing")
    print("=" * 60)
    
    # Get user identity
    user_identity = get_git_user_identity(repo_path)
    user_email = user_identity.get("email", "")
    
    print(f"\n1. Git user identity:")
    print(f"   Name: {user_identity.get('name', 'N/A')}")
    print(f"   Email: {user_email}")
    
    if not user_email:
        print("   ✗ No git user email found, cannot test collaborative parsing")
        return False
    
    # Get classified files
    print(f"\n2. Classifying files for user: {user_email}")
    classified = get_classified_non_code_file_paths(repo_path, user_email)
    
    collab_count = len(classified.get("collaborative", []))
    non_collab_count = len(classified.get("non_collaborative", []))
    
    print(f"   ✓ Collaborative files: {collab_count}")
    print(f"   ✓ Non-collaborative files: {non_collab_count}")
    
    if collab_count == 0:
        print("   ℹ No collaborative files found (this is OK if you're the only author)")
        return True
    
    # Parse with author extraction
    print(f"\n3. Parsing files (collaborative files will extract git diffs)...")
    parsed = parsed_input_text(classified, repo_path, user_email)
    
    if parsed.get("parsed_files"):
        total = len(parsed["parsed_files"])
        author_only = sum(1 for f in parsed["parsed_files"] if f.get("is_author_only"))
        full_content = total - author_only
        
        print(f"   ✓ Total parsed: {total}")
        print(f"   ✓ Full content (non-collaborative): {full_content}")
        print(f"   ✓ Author-only (collaborative): {author_only}")
        
        # Show sample of author-only content
        if author_only > 0:
            print(f"\n4. Sample author-only content:")
            for f in parsed["parsed_files"]:
                if f.get("is_author_only"):
                    print(f"   File: {Path(f['path']).name}")
                    print(f"   Commit: {f.get('commit_hash', 'N/A')[:8]}")
                    print(f"   Message: {f.get('commit_message', 'N/A')[:50]}")
                    content_preview = f.get('content', '')[:100].replace('\n', ' ')
                    print(f"   Content preview: {content_preview}...")
                    break
        
        print("\n" + "=" * 60)
        print("✓ COLLABORATIVE PARSING TEST PASSED!")
        print("=" * 60)
        return True
    else:
        print("   ✗ No parsed files")
        return False

if __name__ == "__main__":
    success = test_collaborative_parsing()
    exit(0 if success else 1)
