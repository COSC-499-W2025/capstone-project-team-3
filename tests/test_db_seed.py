from app.data.db import get_connection, seed_db

def test_all_tables_created():
    """
    Test that all expected tables are created in the database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Define the expected tables
    expected_tables = [
        "CONSENT",
        "USER_PREFERENCES",
        "PROJECT",
        "GIT_HISTORY",
        "SKILL_ANALYSIS",
        "DASHBOARD_DATA",
        "RESUME_SUMMARY"
    ]

    # Get all table names in the current database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    # Assert all expected tables are created
    for table in expected_tables:
        assert table in tables, f"Table '{table}' is not created."
        
    conn.close()
    print("All expected tables are created.")

def test_all_tables_populated():
    """
    Test that all tables in the database now contain at least one row.
    Raises an AssertionError if any table is empty.
    """
    conn = get_connection()
    cursor = conn.cursor()

    seed_db() # Ensure the database is seeded before testing

    # Get all table names in the current database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    empty_tables = []

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        if count == 0:
            empty_tables.append(table)

   

    # Assert all tables are populated
    assert not empty_tables, f"The following tables are empty: {', '.join(empty_tables)}"

    print("All tables are populated")

    # Remove test data from tables
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
    
    conn.commit()
    conn.close()

def test_skill_analysis_has_date_column():
    """
    Test that SKILL_ANALYSIS table has the date column for chronological tracking.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get column information for SKILL_ANALYSIS table
    cursor.execute("PRAGMA table_info(SKILL_ANALYSIS);")
    columns = cursor.fetchall()
    
    # Extract column names
    column_names = [col[1] for col in columns]
    
    # Assert date column exists
    assert 'date' in column_names, "SKILL_ANALYSIS table is missing 'date' column"
    
    conn.close()
    print("SKILL_ANALYSIS table has date column")

def test_seeded_skills_have_dates():
    """
    Test that seeded skills have date values populated.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    seed_db()  # Ensure database is seeded
    
    # Check if skills have dates
    cursor.execute("SELECT skill, date FROM SKILL_ANALYSIS WHERE date IS NOT NULL AND date != ''")
    skills_with_dates = cursor.fetchall()
    
    # Assert that at least some skills have dates
    assert len(skills_with_dates) > 0, "No skills have dates populated"
    
    # Verify date format (YYYY-MM-DD)
    for skill, date in skills_with_dates:
        assert len(date) == 10, f"Skill '{skill}' has invalid date format: {date}"
        assert date.count('-') == 2, f"Skill '{skill}' date missing dashes: {date}"
    
    conn.close()
    print(f"Found {len(skills_with_dates)} skills with valid dates")
    
if __name__ == "__main__":
    test_all_tables_created()
    test_all_tables_populated()
    test_skill_analysis_has_date_column()
    test_seeded_skills_have_dates()
