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
            choice = input("Select project number to edit (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("Exiting.")
                return
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    selected_project = projects[idx]
                    self._project_menu(selected_project)
                    
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
    
    def _project_menu(self, project: dict):
        """Show menu for project edits."""
        while True:
            print("\n" + "-" * 60)
            print(f"Project: {project['name']}")
            print("-" * 60)
            print("What would you like to edit?")
            print("  [1] Project dates")
            print("  [2] Chronological skills")
            print("  [b] Back to project selection")
            print("-" * 60)
            
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == '1':
                self._edit_project_dates(project)
            elif choice == '2':
                self._manage_project_skills(project)
            else:
                print("Invalid option. Try again.")
    
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
    
    def _manage_project_skills(self, project: dict):
        """Manage chronological skills for a specific project."""
        project_id = project['project_signature']
        
        while True:
            print("\n" + "-" * 60)
            print(f"Chronological Skills: {project['name']}")
            print("-" * 60)
            
            # Get chronological skills
            skills = self.manager.get_chronological_skills(project_id)
            
            if not skills:
                print("No skills found for this project.")
            else:
                print("\nSkills (ordered by date):\n")
                for idx, skill in enumerate(skills, 1):
                    date_str = skill['date'] or 'No date'
                    source_icon = "💻" if skill['source'] == 'code' else "👥"
                    print(f"{idx}. {source_icon} {skill['skill']:<30} | {date_str}")
            
            print("\n" + "-" * 60)
            print("Options:")
            print("  [1] View skills")
            print("  [2] Update skill date")
            print("  [3] Remove skill")
            print("  [b] Back")
            print("-" * 60)
            
            action = input("\nSelect option: ").strip().lower()
            
            if action == 'b':
                break
            elif action == '1':
                continue  # Refresh display
            elif action == '2':
                self._update_skill_date(project_id, skills)
            elif action == '3':
                self._remove_skill(project_id, skills)
            else:
                print("Invalid option. Try again.")
    
    def _update_skill_date(self, project_id: str, skills: list):
        """Update the date for a skill."""
        if not skills:
            print("No skills to update.")
            return
        
        print("\nSelect skill to update:")
        for idx, skill in enumerate(skills, 1):
            print(f"{idx}. {skill['skill']} (current: {skill['date'] or 'No date'})")
        
        try:
            choice = int(input("\nSkill number: ").strip()) - 1
            if 0 <= choice < len(skills):
                selected_skill = skills[choice]
                new_date = self._get_date_input(
                    f"Enter new date for '{selected_skill['skill']}' (YYYY-MM-DD)",
                    selected_skill['date']
                )
                
                self.manager.update_skill_date(project_id, selected_skill['skill'], new_date)
                print(f"✓ Updated {selected_skill['skill']} date to {new_date}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    
    def _add_skill(self, project_id: str):
        """Add a new skill with date."""
        print("\nAdd New Skill")
        skill_name = input("Skill name: ").strip()
        
        if not skill_name:
            print("Skill name cannot be empty.")
            return
        
        print("Source type:")
        print("  [1] Code")
        print("  [2] Non-code")
        source_choice = input("Select (1 or 2): ").strip()
        
        if source_choice == '1':
            source = 'code'
        elif source_choice == '2':
            source = 'non-code'
        else:
            print("Invalid source type.")
            return
        
        date = self._get_date_input("Enter date (YYYY-MM-DD)", "")
        
        if not date:
            print("Date is required.")
            return
        
        self.manager.add_skill_with_date(project_id, skill_name, source, date)
        print(f"✓ Added skill: {skill_name} ({date})")
    
    def _remove_skill(self, project_id: str, skills: list):
        """Remove a skill."""
        if not skills:
            print("No skills to remove.")
            return
        
        print("\nSelect skill to remove:")
        for idx, skill in enumerate(skills, 1):
            print(f"{idx}. {skill['skill']}")
        
        try:
            choice = int(input("\nSkill number: ").strip()) - 1
            if 0 <= choice < len(skills):
                selected_skill = skills[choice]
                confirm = input(f"Remove '{selected_skill['skill']}'? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    self.manager.remove_skill(project_id, selected_skill['skill'])
                    print(f"✓ Removed {selected_skill['skill']}")
                else:
                    print("Cancelled.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")


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
