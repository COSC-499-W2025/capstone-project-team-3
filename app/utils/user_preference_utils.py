from pathlib import Path
import sqlite3
from app.data.db import get_connection, DB_PATH, ensure_data_dir

"""This file contains utility functions for managing user preferences in the database."""

# Initialize the UserPreferenceStore with the database path
class UserPreferenceStore:

    def __init__(self, db_path=None):
        """
        Initialize the store. If db_path is provided, open a connection to that path. 
        Otherwise, ensure the data
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
    
    # Retrieve latest record of user preferences (Read from DB)
    def get_latest_preferences(self,email):
        """
        Retrieve the latest user preferences based on the most recent updated_at timestamp.
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT name, email, github_user, education, industry, job_title
            FROM USER_PREFERENCES
            WHERE email = ?
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (email,)
        )
        row = cur.fetchone()
        if not row:
            return None
        keys = [ "name", "email", "github_user", "education", "industry", "job_title"]
        return dict(zip(keys, row))

    # Save/Update user preferences (Write to DB)
    def save_preferences(self, name: str, email: str, github_user: str, education: str, industry: str, job_title: str):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO USER_PREFERENCES (name, email, github_user, education, industry, job_title)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ( name, email, github_user, education, industry, job_title),
        )
        self.conn.commit()

    # Optimized static functions to get latest industry/job/education preferences without email lookup
    @staticmethod
    def get_latest_preferences_no_email():
        store = UserPreferenceStore()
        cur = store.conn.cursor()
        cur.execute(
            """
            SELECT industry, job_title, education
            FROM USER_PREFERENCES
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        store.close()
        if not row:
            return None
        keys = ["industry", "job_title", "education"]
        return dict(zip(keys, row))


    # Close the DB connection
    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass