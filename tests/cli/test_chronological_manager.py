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
    
    # Insert test projects
    cur.execute("""
        INSERT INTO PROJECT (project_signature, name, path, created_at, last_modified)
        VALUES 
            ('test_proj1', 'Test Project 1', '/path/to/proj1', '2024-01-15 10:00:00', '2024-06-20 15:30:00'),
            ('test_proj2', 'Test Project 2', '/path/to/proj2', '2023-05-15T08:00:00', '2024-03-20T12:00:00')
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
