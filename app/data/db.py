import sqlite3
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.sqlite3"

# --- SQL Schema (draft To be Edited) ---
SCHEMA = """
CREATE TABLE IF NOT EXISTS USER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CONSENT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    policy_version TEXT,
    consent_given INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

# --- DB Setup Functions ---
def init_db():
        """TODO: Create database file and initial tables."""
        print(f" Database initialized at: {DB_PATH}")

def get_connection():
        "TODO: Outline connection function"
