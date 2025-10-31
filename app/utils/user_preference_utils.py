from pathlib import Path
import sqlite3

"""This file contains utility functions for managing user preferences in the database."""

DB_PATH = Path(__file__).parent.parent / "db.py"

    # Initialize the UserPreferenceStore with the database path
class UserPreferenceStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._ensure_table()   # Ensure the USER_PREFERENCES table exists

  # Get user preferences by user_id (Read from DB)
    def get_preferences(self, user_id: str) -> Optional[Dict[str, str]]:
        cur = self.conn.cursor()
        cur.execute("SELECT user_id, name, github, education, industry, job_title FROM USER_PREFERENCES WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return None
        keys = ["user_id", "name", "github", "education", "industry", "job_title"]
        return dict(zip(keys, row))

    # Save/Update user preferences (Write to DB)
    def save_preferences(self, user_id: str, name: str, github: str, education: str, industry: str, job_title: str):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO USER_PREFERENCES (user_id, name, github, education, industry, job_title)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, github, education, industry, job_title))
        self.conn.commit()

    #Close the DB connection
    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass