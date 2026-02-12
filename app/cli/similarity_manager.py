"""
CLI manager for handling similar project detection and user confirmation.
"""

from typing import Dict


def prompt_update_confirmation(match_info: Dict, new_project_name: str) -> bool:
    """
    Simple CLI prompt asking user if they want to update the existing project.
    
    Args:
        match_info: Dictionary with similar project details
        new_project_name: Name of the project being uploaded
    
    Returns:
        True if user wants to update, False if they want to create new
    """
    print("\n" + "=" * 60)
    print("🔍 SIMILAR PROJECT DETECTED")
    print("=" * 60)
    print(f"\n📁 Uploading: {new_project_name}")
    print(f"📊 Similar to existing project: '{match_info['project_name']}'")
    print(f"   📈 Similarity: {match_info['similarity_percentage']}%")
    print(f"   🎯 Match type: {match_info['match_reason']}")
    print("\n" + "-" * 60)
    print("Would you like to UPDATE the existing project?")
    print("  • Yes → Replace existing project with new files")
    print("  • No  → Create as a new separate project")
    print("-" * 60)
    
    while True:
        choice = input("\nUpdate existing project? (yes/no): ").strip().lower()
        if choice in ('yes', 'y'):
            print(f"✅ Will update existing project '{match_info['project_name']}'")
            return True
        elif choice in ('no', 'n'):
            print(f"✅ Will create as new project '{new_project_name}'")
            return False
        else:
            print("❌ Please enter 'yes' or 'no'")
