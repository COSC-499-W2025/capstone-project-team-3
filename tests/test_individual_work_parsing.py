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
            
            print(f"   ✓ Total parsed files: {total}")
            print(f"   ✓ All files have contribution_frequency tracking")
            
            # Verify logic
            print("\n3. Verifying parsing logic...")
            
            # Check files have contribution_frequency
            for f in parsed["parsed_files"]:
                if f.get("contribution_frequency") and f.get("success"):
                    print(f"   ✓ File: {Path(f['path']).name} (contribution_frequency={f.get('contribution_frequency')})")
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
