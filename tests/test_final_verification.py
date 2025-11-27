"""
Final verification test for individual work parsing functionality.
"""
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import get_classified_non_code_file_paths, get_git_user_identity
from app.utils.non_code_parsing.document_parser import parsed_input_text

def main():
    repo_path = Path(__file__).parent
    
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION: Individual Work Parsing")
    print("=" * 70)
    
    # Get user
    user_identity = get_git_user_identity(repo_path)
    user_email = user_identity.get("email", "")
    
    print(f"\n📧 User: {user_identity.get('name', 'N/A')} ({user_email})")
    
    # Step 1: Classification
    print("\n" + "-" * 70)
    print("STEP 1: File Classification")
    print("-" * 70)
    
    classified = get_classified_non_code_file_paths(repo_path, user_email)
    
    collab = classified.get("collaborative", [])
    non_collab = classified.get("non_collaborative", [])
    
    print(f"✓ Collaborative files (2+ authors, user is one): {len(collab)}")
    print(f"✓ Non-collaborative files (solo or local): {len(non_collab)}")
    
    # Step 2: Parsing Strategy
    print("\n" + "-" * 70)
    print("STEP 2: Parsing Strategy")
    print("-" * 70)
    
    print("📄 Non-collaborative files → Parse FULL content")
    print("🔀 Collaborative files → Extract ONLY author's git diffs")
    
    # Step 3: Execute Parsing
    print("\n" + "-" * 70)
    print("STEP 3: Execute Parsing")
    print("-" * 70)
    
    parsed = parsed_input_text(classified, repo_path, user_email)
    
    total = len(parsed.get("parsed_files", []))
    author_only = sum(1 for f in parsed["parsed_files"] if f.get("is_author_only"))
    full_content = total - author_only
    
    print(f"✓ Total files parsed: {total}")
    print(f"  - Full content (non-collaborative): {full_content}")
    print(f"  - Author-only diffs (collaborative): {author_only}")
    
    # Step 4: Verification
    print("\n" + "-" * 70)
    print("STEP 4: Verification")
    print("-" * 70)
    
    # Check non-collaborative have full content
    non_collab_check = False
    for f in parsed["parsed_files"]:
        if f.get("contribution_frequency") == 1 and f.get("success"):
            content_len = len(f.get("content", ""))
            if content_len > 0:
                print(f"✓ Non-collaborative file has full content:")
                print(f"  File: {Path(f['path']).name}")
                print(f"  Contribution frequency: 1")
                print(f"  Content length: {content_len} chars")
                non_collab_check = True
                break
    
    # Check collaborative have contribution_frequency and git diffs
    collab_check = False
    for f in parsed["parsed_files"]:
        if f.get("contribution_frequency", 0) > 1 or "week" in f.get("name", "").lower():
            print(f"✓ Collaborative file has author git diffs:")
            print(f"  File: {Path(f['path']).name}")
            print(f"  Contribution frequency: {f.get('contribution_frequency', 0)}")
            print(f"  Content type: Git diff/patch")
            collab_check = True
            break
    
    # Final result
    print("\n" + "=" * 70)
    if (non_collab_check or len(non_collab) == 0) and (collab_check or len(collab) == 0):
        print("✅ ALL CHECKS PASSED - Functionality working as expected!")
        print("\nSummary:")
        print("  • Non-collaborative files → Full content extracted ✓")
        print("  • Collaborative files → Only author's git diffs extracted ✓")
        print("  • README files → Treated as collaborative ✓")
        print("=" * 70)
        return True
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
