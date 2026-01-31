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
        "RESUME_SUMMARY",
        "RESUME",
        "RESUME_PROJECT"
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
    
if __name__ == "__main__":
    test_all_tables_created()
    test_all_tables_populated()
