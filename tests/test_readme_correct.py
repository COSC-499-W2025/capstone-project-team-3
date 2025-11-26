"""
Test README file handling - should parse FULL content, not git diffs.
"""
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import get_classified_non_code_file_paths, get_git_user_identity
from app.utils.non_code_parsing.document_parser import parsed_input_text

def test_readme_full_content():
    repo_path = Path(__file__).parent
    
    print("=" * 70)
    print("Testing README Full Content Parsing")
    print("=" * 70)
    
    # Get user
    user_identity = get_git_user_identity(repo_path)
    user_email = user_identity.get("email", "")
    
    print(f"\n📧 User: {user_email}")
    
    # Get classified files
    print("\n1. Classifying files...")
    classified = get_classified_non_code_file_paths(repo_path, user_email)
    
    # Find README files
    readme_in_collab = [f for f in classified.get("collaborative", []) if Path(f).name.lower().startswith("readme")]
    readme_in_non_collab = [f for f in classified.get("non_collaborative", []) if Path(f).name.lower().startswith("readme")]
    
    print(f"   README in collaborative (git diffs): {len(readme_in_collab)}")
    print(f"   README in non-collaborative (full content): {len(readme_in_non_collab)}")
    
    if readme_in_non_collab:
        print(f"\n   ✓ README files will get FULL content parsing:")
        for f in readme_in_non_collab[:3]:
            print(f"     - {Path(f).name}")
    
    # Parse files
    print("\n2. Parsing files...")
    parsed = parsed_input_text(classified, repo_path, user_email)
    
    # Check README files in parsed results
    readme_parsed = [f for f in parsed.get("parsed_files", []) if Path(f["path"]).name.lower().startswith("readme")]
    
    print(f"   Total README files parsed: {len(readme_parsed)}")
    
    if readme_parsed:
        print(f"\n3. Verifying README parsing:")
        for readme in readme_parsed[:2]:
            is_author_only = readme.get("is_author_only", False)
            has_content = len(readme.get("content", "")) > 0
            
            print(f"\n   File: {Path(readme['path']).name}")
            print(f"   Is author-only (git diff): {is_author_only}")
            print(f"   Has content: {has_content}")
            print(f"   Content length: {len(readme.get('content', ''))} chars")
            
            if not is_author_only and has_content:
                print(f"   ✓ CORRECT: Full content parsed")
            elif is_author_only:
                print(f"   ✗ WRONG: Should be full content, not git diff")
            else:
                print(f"   ✗ WRONG: No content found")
    
    # Final verification
    print("\n" + "=" * 70)
    readme_with_full_content = sum(1 for f in readme_parsed if not f.get("is_author_only") and len(f.get("content", "")) > 0)
    readme_with_git_diff = sum(1 for f in readme_parsed if f.get("is_author_only"))
    
    if readme_with_full_content > 0 and readme_with_git_diff == 0:
        print("✅ README HANDLING CORRECT")
        print(f"   All {readme_with_full_content} README files parsed with FULL content")
        print("   No README files extracted as git diffs")
        print("=" * 70)
        return True
    else:
        print("❌ README HANDLING INCORRECT")
        print(f"   Full content: {readme_with_full_content}")
        print(f"   Git diffs: {readme_with_git_diff}")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = test_readme_full_content()
    exit(0 if success else 1)
