"""
Utility functions for managing project chronology in the database.
"""

import sqlite3
from app.data.db import get_connection, DB_PATH, ensure_data_dir


class ChronologicalManager:
    """Handles reading and updating project dates."""
    
    def __init__(self, db_path=None):
        """
        Initialize the manager.
        
        Args:
            db_path: Optional path to database. Uses default if not provided.
        """
        if db_path is None:
            ensure_data_dir()
            self.db_path = DB_PATH
            self.conn = get_connection()
        else:
            from pathlib import Path
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(self.db_path))
    
    def get_all_projects(self) -> list:
        """
        Get all projects with their dates.
        
        Returns:
            List of dictionaries with project info
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT project_signature, name, path, created_at, last_modified
            FROM PROJECT
            ORDER BY name
        """)
        
        rows = cur.fetchall()
        
        projects = []
        for row in rows:
            projects.append({
                'project_signature': row[0],
                'name': row[1],
                'path': row[2],
                'created_at': row[3],
                'last_modified': row[4]
            })
        
        return projects
    
    def update_project_dates(self, project_signature: str, created_at: str, last_modified: str):
        """
        Update dates for a specific project.
        
        Args:
            project_signature: Unique identifier for the project
            created_at: New created date (YYYY-MM-DD HH:MM:SS or YYYY-MM-DD)
            last_modified: New modified date (YYYY-MM-DD HH:MM:SS or YYYY-MM-DD)
        """
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE PROJECT
            SET created_at = ?, last_modified = ?
            WHERE project_signature = ?
        """, (created_at, last_modified, project_signature))
        
        self.conn.commit()
    
    def get_project_by_signature(self, project_signature: str) -> dict:
        """
        Get a specific project by its signature.
        
        Args:
            project_signature: Unique identifier for the project
        
        Returns:
            Dictionary with project info or None if not found
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT project_signature, name, path, created_at, last_modified
            FROM PROJECT
            WHERE project_signature = ?
        """, (project_signature,))
        
        row = cur.fetchone()
        if not row:
            return None
        
        return {
            'project_signature': row[0],
            'name': row[1],
            'path': row[2],
            'created_at': row[3],
            'last_modified': row[4]
        }
    
    def get_chronological_skills(self, project_id: str) -> list:
        """
        Get all skills for a project, ordered chronologically by date.
        
        Args:
            project_id: Project signature to get skills for
            
        Returns:
            List of dicts with id, skill, source, and date ordered by date ascending
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, skill, source, date
            FROM SKILL_ANALYSIS
            WHERE project_id = ?
            ORDER BY date ASC, skill ASC
        """, (project_id,))
        
        rows = cur.fetchall()
        return [
            {
                'id': row[0],
                'skill': row[1],
                'source': row[2],
                'date': row[3] or ''
            }
            for row in rows
        ]
    
    def update_skill_date(self, skill_id: int, new_date: str):
        """
        Update the date for a specific skill entry by ID.
        
        Args:
            skill_id: ID of the skill entry to update
            new_date: New date in YYYY-MM-DD format
        """
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE SKILL_ANALYSIS
            SET date = ?
            WHERE id = ?
        """, (new_date, skill_id))
        
        self.conn.commit()
    
    def add_skill_with_date(self, project_id: str, skill: str, source: str, date: str):
        """
        Add a new skill with a date to a project.
        
        Args:
            project_id: Project signature
            skill: Skill name
            source: Source of skill ('code' or 'non-code')
            date: Date in YYYY-MM-DD format
        """
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO SKILL_ANALYSIS (project_id, skill, source, date)
            VALUES (?, ?, ?, ?)
        """, (project_id, skill, source, date))
        
        self.conn.commit()
    
    def remove_skill(self, skill_id: int):
        """
        Remove a skill entry by ID.
        
        Args:
            skill_id: ID of the skill entry to remove
        """
        cur = self.conn.cursor()
        cur.execute("""
            DELETE FROM SKILL_ANALYSIS
            WHERE id = ?
        """, (skill_id,))
        
        self.conn.commit()
    
    def update_skill_name(self, skill_id: int, new_skill: str):
        """
        Rename a skill entry by ID.
        
        Args:
            skill_id: ID of the skill entry to update
            new_skill: New skill name
        """
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE SKILL_ANALYSIS
            SET skill = ?
            WHERE id = ?
        """, (new_skill, skill_id))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
