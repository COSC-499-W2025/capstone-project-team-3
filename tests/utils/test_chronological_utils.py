"""
Tests for chronological_utils.py - ChronologicalManager utility class.
"""

import pytest
import sqlite3
from pathlib import Path
from app.utils.chronological_utils import ChronologicalManager


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database with test projects."""
    db_path = tmp_path / "test_chronology.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    # Create PROJECT table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PROJECT (
            project_signature TEXT PRIMARY KEY,
            name TEXT,
            path TEXT,
            created_at TIMESTAMP,
            last_modified TIMESTAMP
        )
    """)
    
    # Create SKILL_ANALYSIS table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS SKILL_ANALYSIS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            skill TEXT,
            source TEXT,
            date TEXT,
            FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
        )
    """)
    
    # Insert test projects
    test_projects = [
        ('proj1', 'Project One', '/path/to/proj1', '2024-01-15 10:00:00', '2024-06-20 15:30:00'),
        ('proj2', 'Project Two', '/path/to/proj2', '2023-05-15T08:00:00', '2024-03-20T12:00:00'),
        ('proj3', 'Project Three', '/path/to/proj3', '2024-12-01', '2025-01-15')
    ]
    
    cur.executemany("""
        INSERT INTO PROJECT (project_signature, name, path, created_at, last_modified)
        VALUES (?, ?, ?, ?, ?)
    """, test_projects)
    
    # Insert test skills
    test_skills = [
        ('proj1', 'Python', 'code', '2024-01-15'),
        ('proj1', 'Flask', 'code', '2024-02-01'),
        ('proj1', 'Docker', 'code', '2024-03-15'),
        ('proj2', 'JavaScript', 'code', '2023-05-15'),
        ('proj2', 'React', 'code', '2023-06-01'),
    ]
    
    cur.executemany("""
        INSERT INTO SKILL_ANALYSIS (project_id, skill, source, date)
        VALUES (?, ?, ?, ?)
    """, test_skills)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    if db_path.exists():
        db_path.unlink()


class TestChronologicalManager:
    """Test ChronologicalManager utility class."""
    
    def test_initialization(self, temp_db):
        """Test manager initialization with custom db path."""
        manager = ChronologicalManager(db_path=temp_db)
        assert manager.db_path == temp_db
        assert manager.conn is not None
        manager.close()
    
    def test_get_all_projects(self, temp_db):
        """Test retrieving all projects from database."""
        manager = ChronologicalManager(db_path=temp_db)
        projects = manager.get_all_projects()
        
        assert len(projects) == 3
        assert all('project_signature' in p for p in projects)
        assert all('name' in p for p in projects)
        assert all('created_at' in p for p in projects)
        assert all('last_modified' in p for p in projects)
        
        # Verify projects are ordered by name
        assert projects[0]['name'] == 'Project One'
        assert projects[1]['name'] == 'Project Three'
        assert projects[2]['name'] == 'Project Two'
        
        manager.close()
    
    def test_get_all_projects_empty_database(self, tmp_path):
        """Test getting projects from empty database."""
        db_path = tmp_path / "empty.db"
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS PROJECT (
                project_signature TEXT PRIMARY KEY,
                name TEXT,
                path TEXT,
                created_at TIMESTAMP,
                last_modified TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        manager = ChronologicalManager(db_path=db_path)
        projects = manager.get_all_projects()
        
        assert projects == []
        manager.close()
    
    def test_update_project_dates(self, temp_db):
        """Test updating project dates."""
        manager = ChronologicalManager(db_path=temp_db)
        
        # Update dates
        manager.update_project_dates('proj1', '2024-02-01', '2024-07-01')
        
        # Verify update
        project = manager.get_project_by_signature('proj1')
        assert project['created_at'] == '2024-02-01'
        assert project['last_modified'] == '2024-07-01'
        
        manager.close()
    
    def test_update_project_dates_with_timestamps(self, temp_db):
        """Test updating dates with full timestamps."""
        manager = ChronologicalManager(db_path=temp_db)
        
        manager.update_project_dates('proj2', '2024-03-15 09:30:00', '2024-08-20 14:45:00')
        
        project = manager.get_project_by_signature('proj2')
        assert '2024-03-15' in project['created_at']
        assert '2024-08-20' in project['last_modified']
        
        manager.close()
    
    def test_get_project_by_signature(self, temp_db):
        """Test getting a specific project by signature."""
        manager = ChronologicalManager(db_path=temp_db)
        
        project = manager.get_project_by_signature('proj2')
        
        assert project is not None
        assert project['project_signature'] == 'proj2'
        assert project['name'] == 'Project Two'
        assert project['path'] == '/path/to/proj2'
        assert '2023-05-15' in project['created_at']
        assert '2024-03-20' in project['last_modified']
        
        manager.close()
    
    def test_get_project_by_signature_not_found(self, temp_db):
        """Test getting a non-existent project."""
        manager = ChronologicalManager(db_path=temp_db)
        
        project = manager.get_project_by_signature('nonexistent_project')
        assert project is None
        
        manager.close()
    
    def test_close_connection(self, temp_db):
        """Test closing database connection."""
        manager = ChronologicalManager(db_path=temp_db)
        
        # Connection should be open
        assert manager.conn is not None
        
        # Close connection
        manager.close()
        
        # After closing, attempting to use connection should fail
        with pytest.raises(sqlite3.ProgrammingError):
            manager.conn.execute("SELECT 1")
    
    def test_get_chronological_skills(self, temp_db):
        """Test getting chronological skills for a project."""
        manager = ChronologicalManager(db_path=temp_db)
        
        skills = manager.get_chronological_skills('proj1')
        
        assert len(skills) == 3
        # Verify chronological order (by date ascending)
        assert skills[0]['skill'] == 'Python'
        assert skills[0]['date'] == '2024-01-15'
        assert skills[1]['skill'] == 'Flask'
        assert skills[1]['date'] == '2024-02-01'
        assert skills[2]['skill'] == 'Docker'
        assert skills[2]['date'] == '2024-03-15'
        
        manager.close()
    
    def test_get_chronological_skills_empty(self, temp_db):
        """Test getting skills for project with no skills."""
        manager = ChronologicalManager(db_path=temp_db)
        
        skills = manager.get_chronological_skills('proj3')
        assert skills == []
        
        manager.close()
    
    def test_update_skill_date(self, temp_db):
        """Test updating a skill's date."""
        manager = ChronologicalManager(db_path=temp_db)
        
        # Update Flask date
        manager.update_skill_date('proj1', 'Flask', '2024-02-15')
        
        # Verify update
        skills = manager.get_chronological_skills('proj1')
        flask_skill = [s for s in skills if s['skill'] == 'Flask'][0]
        assert flask_skill['date'] == '2024-02-15'
        
        manager.close()
    
    def test_add_skill_with_date(self, temp_db):
        """Test adding a new skill with date."""
        manager = ChronologicalManager(db_path=temp_db)
        
        # Add new skill
        manager.add_skill_with_date('proj1', 'PostgreSQL', 'code', '2024-04-01')
        
        # Verify addition
        skills = manager.get_chronological_skills('proj1')
        assert len(skills) == 4
        postgres_skill = [s for s in skills if s['skill'] == 'PostgreSQL'][0]
        assert postgres_skill['date'] == '2024-04-01'
        assert postgres_skill['source'] == 'code'
        
        manager.close()
    def test_remove_skill(self, temp_db):
        """Test removing a skill from a project."""
        manager = ChronologicalManager(db_path=temp_db)
        
        # Remove Flask
        manager.remove_skill('proj1', 'Flask')
        
        # Verify removal
        skills = manager.get_chronological_skills('proj1')
        assert len(skills) == 2
        assert all(s['skill'] != 'Flask' for s in skills)
        
        manager.close()
    
    def test_skill_chronological_order_after_update(self, temp_db):
        """Test that skills remain chronologically ordered after date update."""
        manager = ChronologicalManager(db_path=temp_db)
        
        # Update Docker to an earlier date
        manager.update_skill_date('proj1', 'Docker', '2024-01-20')
        
        # Verify chronological order
        skills = manager.get_chronological_skills('proj1')
        dates = [s['date'] for s in skills]
        assert dates == sorted(dates)  # Should be in ascending order
        
        manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
