import sqlite3
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR 
DB_PATH = DATA_DIR / "app.sqlite3"

# --- SQL Schema (draft To be Edited) ---
SCHEMA = """
CREATE TABLE IF NOT EXISTS METADATA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author TEXT
);

CREATE TABLE IF NOT EXISTS CONSENT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    policy_version TEXT,
    consent_given INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);



"""

# --- DB Setup Functions ---
def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_connection():
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Create database file and initial tables."""
    ensure_data_dir()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")
