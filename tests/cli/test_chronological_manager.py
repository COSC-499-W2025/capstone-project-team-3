"""
Tests for chronological_manager.py - ChronologicalCLI class.
"""

import pytest
import sqlite3
from pathlib import Path
from app.utils.chronological_utils import ChronologicalManager
from app.cli.chronological_manager import ChronologicalCLI


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
    cur.execute("""
        INSERT INTO PROJECT (project_signature, name, path, created_at, last_modified)
        VALUES 
            ('test_proj1', 'Test Project 1', '/path/to/proj1', '2024-01-15 10:00:00', '2024-06-20 15:30:00'),
            ('test_proj2', 'Test Project 2', '/path/to/proj2', '2023-05-15T08:00:00', '2024-03-20T12:00:00')
    """)
    
    # Insert test skills
    cur.execute("""
        INSERT INTO SKILL_ANALYSIS (project_id, skill, source, date)
        VALUES 
            ('test_proj1', 'Python', 'code', '2024-01-15'),
            ('test_proj1', 'Flask', 'code', '2024-02-01'),
            ('test_proj2', 'JavaScript', 'code', '2023-05-15')
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    if db_path.exists():
        db_path.unlink()


class TestChronologicalCLI:
    """Test ChronologicalCLI class."""
    
    def test_initialization(self, temp_db):
        """Test CLI initialization."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        assert cli.manager == manager
        manager.close()
    
    def test_format_date_with_time(self, temp_db):
        """Test date formatting strips time."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Test with space separator
        assert cli._format_date('2024-01-15 10:00:00') == '2024-01-15'
        
        # Test with T separator
        assert cli._format_date('2024-01-15T10:00:00') == '2024-01-15'
        
        # Test with already clean date
        assert cli._format_date('2024-01-15') == '2024-01-15'
        
        manager.close()
    
    def test_date_normalization_with_missing_leading_zeros(self, temp_db, monkeypatch):
        """Test that dates without leading zeros are normalized correctly."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Simulate user input with missing leading zeros
        inputs = iter(['2025-2-1'])  # Missing leading zeros
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = cli._get_date_input("Enter date", "2024-01-01")
        
        # Should normalize to have leading zeros
        assert result == '2025-02-01'
        
        manager.close()
    
    def test_date_normalization_consistency(self, temp_db, monkeypatch):
        """Test that different input formats result in the same normalized output."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        test_cases = [
            '2025-2-1',      # No leading zeros
            '2025-02-1',     # Partial leading zeros
            '2025-2-01',     # Partial leading zeros (different)
            '2025-02-01',    # Full leading zeros
        ]
        
        expected = '2025-02-01'
        
        for test_input in test_cases:
            inputs = iter([test_input])
            monkeypatch.setattr('builtins.input', lambda _: next(inputs))
            result = cli._get_date_input("Enter date", "2024-01-01")
            assert result == expected, f"Failed for input: {test_input}"
        
        manager.close()
    
    def test_manage_project_skills_get_skills(self, temp_db):
        """Test that _manage_project_skills can retrieve chronological skills."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Get skills for test_proj1
        skills = manager.get_chronological_skills('test_proj1')
        
        assert len(skills) == 2
        assert skills[0]['skill'] == 'Python'
        assert skills[0]['date'] == '2024-01-15'
        assert skills[1]['skill'] == 'Flask'
        assert skills[1]['date'] == '2024-02-01'
        
        manager.close()
    
    def test_update_skill_date_in_cli(self, temp_db):
        """Test updating a skill date through CLI methods."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Update Flask date
        manager.update_skill_date('test_proj1', 'Flask', '2024-03-01')
        
        # Verify update
        skills = manager.get_chronological_skills('test_proj1')
        flask_skill = [s for s in skills if s['skill'] == 'Flask'][0]
        assert flask_skill['date'] == '2024-03-01'
        
        manager.close()
    
    def test_remove_skill_in_cli(self, temp_db):
        """Test removing a skill through CLI methods."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Remove Flask
        manager.remove_skill('test_proj1', 'Flask')
        
        # Verify removal
        skills = manager.get_chronological_skills('test_proj1')
        assert len(skills) == 1
        assert skills[0]['skill'] == 'Python'
        
        manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
