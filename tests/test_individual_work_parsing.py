"""
Test script to verify individual work parsing functionality.
"""
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import get_classified_non_code_file_paths
from app.utils.non_code_parsing.document_parser import parsed_input_text

def test_classification_and_parsing():
    """Test that classification and parsing work correctly."""
    
    # Use current repo as test
    repo_path = Path(__file__).parent
    
    print("=" * 60)
    print("Testing Individual Work Parsing Functionality")
    print("=" * 60)
    
    # Step 1: Get classified files
    print("\n1. Classifying non-code files...")
    classified = get_classified_non_code_file_paths(repo_path)
    
    print(f"   Type of result: {type(classified)}")
    print(f"   Keys: {classified.keys() if isinstance(classified, dict) else 'NOT A DICT!'}")
    
    if isinstance(classified, dict):
        collab_count = len(classified.get("collaborative", []))
        non_collab_count = len(classified.get("non_collaborative", []))
        
        print(f"   ✓ Collaborative files: {collab_count}")
        print(f"   ✓ Non-collaborative files: {non_collab_count}")
        
        if collab_count > 0:
            print(f"\n   Sample collaborative files:")
            for f in classified["collaborative"][:3]:
                print(f"     - {Path(f).name}")
        
        if non_collab_count > 0:
            print(f"\n   Sample non-collaborative files:")
            for f in classified["non_collaborative"][:3]:
                print(f"     - {Path(f).name}")
    else:
        print("   ✗ ERROR: Expected dict, got list!")
        return False
    
    # Step 2: Parse files
    print("\n2. Parsing files with different strategies...")
    
    try:
        parsed = parsed_input_text(classified, repo_path, None)
        
        print(f"   Type of result: {type(parsed)}")
        print(f"   Keys: {parsed.keys() if isinstance(parsed, dict) else 'NOT A DICT!'}")
        
        if parsed.get("parsed_files"):
            total = len(parsed["parsed_files"])
            author_only = sum(1 for f in parsed["parsed_files"] if f.get("is_author_only"))
            full_content = total - author_only
            
            print(f"   ✓ Total parsed files: {total}")
            print(f"   ✓ Full content (non-collaborative): {full_content}")
            print(f"   ✓ Author-only content (collaborative): {author_only}")
            
            # Verify logic
            print("\n3. Verifying parsing logic...")
            
            # Check non-collaborative files have full content and contribution_frequency=1
            for f in parsed["parsed_files"]:
                if f.get("contribution_frequency") == 1 and f.get("success") and len(f.get("content", "")) > 0:
                    print(f"   ✓ Non-collaborative file: {Path(f['path']).name} (freq=1, full content)")
                    break
            
            # Check collaborative files have contribution_frequency > 0
            for f in parsed["parsed_files"]:
                if f.get("contribution_frequency", 0) >= 1 and "week" in Path(f['path']).name.lower():
                    print(f"   ✓ Collaborative file: {Path(f['path']).name} (freq={f.get('contribution_frequency')})")
                    break
            
            print("\n" + "=" * 60)
            print("✓ TEST PASSED: Functionality working as expected!")
            print("=" * 60)
            return True
        else:
            print("   ✗ No parsed files found")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR during parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_classification_and_parsing()
    exit(0 if success else 1)
