#!/usr/bin/env python3
"""
Chronological Manager - Edit project dates directly.
Run this to correct dates for your analyzed projects.

Usage:
    python3 app/cli/chronological_manager.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.chronological_utils import ChronologicalManager
from datetime import datetime


class ChronologicalCLI:
    """Simple CLI for correcting project dates."""
    
    def __init__(self, manager: ChronologicalManager = None):
        self.manager = manager or ChronologicalManager()
    
    def _format_date(self, date_str: str) -> str:
        """Strip time from date string, show only date."""
        if not date_str:
            return date_str
        # Extract just YYYY-MM-DD part
        return date_str.split()[0] if ' ' in date_str else date_str.split('T')[0]
    
    def run(self):
        """Main entry point for date management."""
        print("=" * 60)
        print("PROJECT CHRONOLOGICAL MANAGER")
        print("=" * 60)
        print()
        
        # Get all projects
        projects = self.manager.get_all_projects()
        
        if not projects:
            print("No projects found in the database.")
            print("Please run project analysis first.")
            return
        
        # Display projects
        print(f"Found {len(projects)} project(s):\n")
        for idx, project in enumerate(projects, 1):
            created = self._format_date(project['created_at'])
            modified = self._format_date(project['last_modified'])
            print(f"{idx}. {project['name']}")
            print(f"   📅 {created} → {modified}")
            print()
        
        # Let user select project
        while True:
            choice = input("Select a project number to edit dates (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("Exiting.")
                return
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    selected_project = projects[idx]
                    self._edit_project_dates(selected_project)
                    
                    # Ask if they want to edit another
                    another = input("\nEdit another project? (yes/no): ").strip().lower()
                    if another != 'yes':
                        print("Done!")
                        return
                    print("\n" + "=" * 60 + "\n")
                    
                    # Refresh project list
                    projects = self.manager.get_all_projects()
                    for idx, project in enumerate(projects, 1):
                        created = self._format_date(project['created_at'])
                        modified = self._format_date(project['last_modified'])
                        print(f"{idx}. {project['name']}")
                        print(f"   📅 {created} → {modified}")
                        print()
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a valid number or 'q' to quit.")
    
    def _edit_project_dates(self, project: dict):
        """Edit dates for a specific project."""
        created = self._format_date(project['created_at'])
        modified = self._format_date(project['last_modified'])
        
        print("\n" + "-" * 60)
        print(f"Editing: {project['name']}")
        print("-" * 60)
        print(f"Current created date: {created}")
        print(f"Current modified date: {modified}")
        print()
        
        # Edit created date
        new_created = self._get_date_input(
            "Enter new created date (YYYY-MM-DD) or press Enter to keep current",
            created
        )
        
        # Edit modified date
        new_modified = self._get_date_input(
            "Enter new modified date (YYYY-MM-DD) or press Enter to keep current",
            modified
        )
        
        # Confirm changes
        if new_created != created or new_modified != modified:
            print("\n" + "-" * 60)
            print("Summary of changes:")
            if new_created != created:
                print(f"  Created: {created} → {new_created}")
            if new_modified != modified:
                print(f"  Modified: {modified} → {new_modified}")
            print("-" * 60)
            
            confirm = input("Save these changes? (yes/no): ").strip().lower()
            if confirm == 'yes':
                self.manager.update_project_dates(
                    project['project_signature'],
                    new_created,
                    new_modified
                )
                print("✓ Dates updated successfully!")
            else:
                print("Changes discarded.")
        else:
            print("No changes made.")
    
    def _get_date_input(self, prompt: str, current_value: str) -> str:
        """Get date input from user with validation."""
        while True:
            user_input = input(f"{prompt}: ").strip()
            
            # Keep current if empty
            if not user_input:
                return current_value
            
            # Validate date format and normalize it
            try:
                date_obj = datetime.strptime(user_input, '%Y-%m-%d')
                # Return normalized format with leading zeros (YYYY-MM-DD)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                print("  Invalid date format. Please use YYYY-MM-DD (e.g., 2024-01-15)")


def main():
    """Main entry point."""
    try:
        cli = ChronologicalCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
