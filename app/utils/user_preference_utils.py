from pathlib import Path
import sqlite3
from app.data.db import get_connection, DB_PATH, ensure_data_dir

"""This file contains utility functions for managing user preferences in the database."""

# Initialize the UserPreferenceStore with the database path
class UserPreferenceStore:

    def __init__(self, db_path=None):
        """
        Initialize the store. If db_path is provided, open a connection to that path
        (creating parent directories if necessary). Otherwise, ensure the data
        directory exists and use the default DB connection.
        """
        if db_path is None:
            ensure_data_dir()  # Ensure the data directory exists
            self.db_path = DB_PATH
            self.conn = get_connection()  # get a connection to the default DB
        else:
            self.db_path = Path(db_path)
            # Ensure the parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(self.db_path))

    # Get user preferences by user_id if exists (Read from DB)
    def get_preferences(self, user_id: str):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT user_id, name, github_user, education, industry, job_title FROM USER_PREFERENCES WHERE user_id = ?",
            (user_id,),
                        )
        row = cur.fetchone()
        if not row:
            return None
        keys = ["user_id", "name", "github_user", "education", "industry", "job_title"]
        return dict(zip(keys, row))

    # Save/Update user preferences (Write to DB)
    def save_preferences(self, user_id: str, name: str, github_user: str, education: str, industry: str, job_title: str):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO USER_PREFERENCES (user_id, name, github_user, education, industry, job_title)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, github_user, education, industry, job_title),
        )
        self.conn.commit()

    # Close the DB connection
    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass