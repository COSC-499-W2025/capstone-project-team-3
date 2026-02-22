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
    
    def test_manage_skill_dates_get_skills(self, temp_db):
        """Test that _manage_skill_dates can retrieve chronological skills."""
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
    
    def test_manage_skills_get_skills(self, temp_db):
        """Test that _manage_skills can retrieve skills."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Get skills for test_proj1
        skills = manager.get_chronological_skills('test_proj1')
        
        assert len(skills) == 2
        assert skills[0]['skill'] == 'Python'
        assert skills[1]['skill'] == 'Flask'
        
        manager.close()
    
    def test_update_skill_date_in_cli(self, temp_db):
        """Test updating a skill date through CLI methods."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Get Flask skill ID
        skills = manager.get_chronological_skills('test_proj1')
        flask_skill = [s for s in skills if s['skill'] == 'Flask'][0]
        
        # Update Flask date
        manager.update_skill_date(flask_skill['id'], '2024-03-01')
        
        # Verify update
        skills = manager.get_chronological_skills('test_proj1')
        flask_skill = [s for s in skills if s['skill'] == 'Flask'][0]
        assert flask_skill['date'] == '2024-03-01'
        
        manager.close()
    
    def test_remove_skill_in_cli(self, temp_db):
        """Test removing a skill through CLI methods."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Get Flask skill ID
        skills = manager.get_chronological_skills('test_proj1')
        flask_skill = [s for s in skills if s['skill'] == 'Flask'][0]
        
        # Remove Flask
        manager.remove_skill(flask_skill['id'])
        
        # Verify removal
        skills = manager.get_chronological_skills('test_proj1')
        assert len(skills) == 1
        assert skills[0]['skill'] == 'Python'
        
        manager.close()
    
    def test_add_skill_with_cli(self, temp_db, monkeypatch):
        """Test adding a new skill with date through CLI."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Simulate user input: skill name, source type, date
        inputs = iter(['Docker', '1', '2024-04-01'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        # Add skill
        cli._add_skill('test_proj1')
        
        # Verify addition
        skills = manager.get_chronological_skills('test_proj1')
        assert len(skills) == 3
        docker_skill = [s for s in skills if s['skill'] == 'Docker'][0]
        assert docker_skill['skill'] == 'Docker'
        assert docker_skill['source'] == 'code'
        assert docker_skill['date'] == '2024-04-01'
        
        manager.close()
    
    def test_add_skill_non_code_source(self, temp_db, monkeypatch):
        """Test adding a skill with non-code source."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Simulate user input: skill name, non-code source, date
        inputs = iter(['Leadership', '2', '2024-05-15'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        # Add skill
        cli._add_skill('test_proj1')
        
        # Verify addition
        skills = manager.get_chronological_skills('test_proj1')
        leadership_skill = [s for s in skills if s['skill'] == 'Leadership'][0]
        assert leadership_skill['skill'] == 'Leadership'
        assert leadership_skill['source'] == 'non-code'
        assert leadership_skill['date'] == '2024-05-15'
        
        manager.close()
    
    def test_add_skill_validates_empty_name(self, temp_db, monkeypatch, capsys):
        """Test that adding skill with empty name is rejected."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Simulate empty skill name
        inputs = iter([''])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        # Try to add skill
        cli._add_skill('test_proj1')
        
        # Verify no skill was added
        skills = manager.get_chronological_skills('test_proj1')
        assert len(skills) == 2  # Still only original 2 skills
        
        # Verify error message
        captured = capsys.readouterr()
        assert 'cannot be empty' in captured.out
        
        manager.close()
    
    def test_add_skill_validates_invalid_source(self, temp_db, monkeypatch, capsys):
        """Test that invalid source type is rejected."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Simulate invalid source type
        inputs = iter(['NewSkill', '3'])  # 3 is invalid
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        # Try to add skill
        cli._add_skill('test_proj1')
        
        # Verify no skill was added
        skills = manager.get_chronological_skills('test_proj1')
        assert len(skills) == 2
        
        # Verify error message
        captured = capsys.readouterr()
        assert 'Invalid source type' in captured.out
        
        manager.close()
    
    def test_edit_skill_name(self, temp_db, monkeypatch):
        """Test renaming a skill through CLI."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Get skills list
        skills = manager.get_chronological_skills('test_proj1')
        
        # Simulate user input: select skill 1 (Python), new name, confirm
        inputs = iter(['1', 'Python3', 'yes'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        # Edit skill
        cli._edit_skill_name(skills)
        
        # Verify rename
        updated_skills = manager.get_chronological_skills('test_proj1')
        skill_names = [s['skill'] for s in updated_skills]
        assert 'Python3' in skill_names
        assert 'Python' not in skill_names
        
        manager.close()
    
    def test_edit_skill_name_preserves_properties(self, temp_db, monkeypatch):
        """Test that renaming preserves date and source."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Get original Flask skill properties
        skills = manager.get_chronological_skills('test_proj1')
        flask_skill = [s for s in skills if s['skill'] == 'Flask'][0]
        original_date = flask_skill['date']
        original_source = flask_skill['source']
        
        # Simulate renaming Flask to Flask-RESTful (will be normalized to Flask-Restful)
        inputs = iter(['2', 'Flask-RESTful', 'yes'])  # Skill 2 is Flask
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        cli._edit_skill_name(skills)
        
        # Verify properties preserved (note: normalized to Flask-Restful via title case)
        updated_skills = manager.get_chronological_skills('test_proj1')
        flask_restful = [s for s in updated_skills if s['skill'] == 'Flask-Restful'][0]
        assert flask_restful['date'] == original_date
        assert flask_restful['source'] == original_source
        
        manager.close()
    
    def test_edit_skill_name_validates_empty(self, temp_db, monkeypatch, capsys):
        """Test that empty new name is rejected."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        skills = manager.get_chronological_skills('test_proj1')
        
        # Simulate empty new name
        inputs = iter(['1', ''])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        cli._edit_skill_name(skills)
        
        # Verify no change
        updated_skills = manager.get_chronological_skills('test_proj1')
        assert updated_skills == skills
        
        # Verify error message
        captured = capsys.readouterr()
        assert 'cannot be empty' in captured.out
        
        manager.close()
    
    def test_edit_skill_name_cancelled(self, temp_db, monkeypatch, capsys):
        """Test cancelling skill rename."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        skills = manager.get_chronological_skills('test_proj1')
        original_names = [s['skill'] for s in skills]
        
        # Simulate cancelling rename
        inputs = iter(['1', 'NewName', 'no'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        cli._edit_skill_name(skills)
        
        # Verify no change
        updated_skills = manager.get_chronological_skills('test_proj1')
        updated_names = [s['skill'] for s in updated_skills]
        assert updated_names == original_names
        
        # Verify cancelled message
        captured = capsys.readouterr()
        assert 'Cancelled' in captured.out
        
        manager.close()
    
    def test_normalize_skill_name_known_skills(self, temp_db):
        """Test skill name normalization for known technical skills."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Test various casings of known skills
        assert cli._normalize_skill_name('python') == 'Python'
        assert cli._normalize_skill_name('PYTHON') == 'Python'
        assert cli._normalize_skill_name('PyThOn') == 'Python'
        
        assert cli._normalize_skill_name('javascript') == 'JavaScript'
        assert cli._normalize_skill_name('JAVASCRIPT') == 'JavaScript'
        
        assert cli._normalize_skill_name('postgresql') == 'PostgreSQL'
        assert cli._normalize_skill_name('docker') == 'Docker'
        assert cli._normalize_skill_name('aws') == 'AWS'
        
        manager.close()
    
    def test_normalize_skill_name_unknown_skills(self, temp_db):
        """Test skill name normalization for unknown skills defaults to title case."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Test unknown skills get title cased
        assert cli._normalize_skill_name('some skill') == 'Some Skill'
        assert cli._normalize_skill_name('custom tool') == 'Custom Tool'
        assert cli._normalize_skill_name('MY FRAMEWORK') == 'My Framework'
        
        manager.close()
    
    def test_is_yes_various_inputs(self, temp_db):
        """Test _is_yes accepts various affirmative inputs."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Test yes variations
        assert cli._is_yes('y') is True
        assert cli._is_yes('Y') is True
        assert cli._is_yes('yes') is True
        assert cli._is_yes('Yes') is True
        assert cli._is_yes('YES') is True
        assert cli._is_yes('  yes  ') is True  # with whitespace
        
        # Test non-yes inputs
        assert cli._is_yes('n') is False
        assert cli._is_yes('no') is False
        assert cli._is_yes('yeah') is False
        assert cli._is_yes('yep') is False
        assert cli._is_yes('') is False
        
        manager.close()
    
    def test_is_no_various_inputs(self, temp_db):
        """Test _is_no accepts various negative inputs."""
        manager = ChronologicalManager(db_path=temp_db)
        cli = ChronologicalCLI(manager=manager)
        
        # Test no variations
        assert cli._is_no('n') is True
        assert cli._is_no('N') is True
        assert cli._is_no('no') is True
        assert cli._is_no('No') is True
        assert cli._is_no('NO') is True
        assert cli._is_no('  no  ') is True  # with whitespace
        
        # Test non-no inputs
        assert cli._is_no('y') is False
        assert cli._is_no('yes') is False
        assert cli._is_no('nope') is False
        assert cli._is_no('nah') is False
        assert cli._is_no('') is False
        
        manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
