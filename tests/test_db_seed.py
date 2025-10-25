from app.data.db import get_connection

def test_all_tables_populated():
    """
    Test that all tables in the database now contain at least one row.
    Raises an AssertionError if any table is empty.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get all table names in the current database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    assert tables, "No tables found in the database."

    empty_tables = []

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        if count == 0:
            empty_tables.append(table)

    conn.close()

    # Assert all tables are populated
    assert not empty_tables, f"The following tables are empty: {', '.join(empty_tables)}"

    print("All tables are populated")

if __name__ == "__main__":
    test_all_tables_populated()
