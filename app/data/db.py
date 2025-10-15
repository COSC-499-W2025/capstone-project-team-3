import sqlite3
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR 
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
    FOREIGN KEY (user_id) REFERENCES user(id)
);
"""

# --- DB Setup Functions ---
def init_db():
    """Create database file and initial tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    print(f"Database initialized at: {DB_PATH}")

def get_connection():
    """Get a connection to the database."""
    return sqlite3.connect(DB_PATH)

# --- Consent Management Functions ---
def create_consent(user_id: int, policy_version: str, consent_given: bool) -> int:
    """Create a new consent record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO CONSENT (user_id, policy_version, consent_given) VALUES (?, ?, ?)",
            (user_id, policy_version, 1 if consent_given else 0)
        )
        conn.commit()
        return cursor.lastrowid

def get_consent_status(user_id: int) -> dict:
    """Get the latest consent status for a user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_id, policy_version, consent_given, timestamp 
               FROM CONSENT 
               WHERE user_id = ? 
               ORDER BY timestamp DESC, id DESC 
               LIMIT 1""",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "policy_version": row[2],
                "consent_given": bool(row[3]),
                "timestamp": row[4]
            }
        return None

def update_consent(user_id: int, policy_version: str, consent_given: bool) -> int:
    """Update consent by creating a new record (maintains history)."""
    return create_consent(user_id, policy_version, consent_given)

def get_consent_history(user_id: int) -> list:
    """Get all consent records for a user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_id, policy_version, consent_given, timestamp 
               FROM CONSENT 
               WHERE user_id = ? 
               ORDER BY timestamp DESC, id DESC""",
            (user_id,)
        )
        rows = cursor.fetchall()
        return [{
            "id": row[0],
            "user_id": row[1],
            "policy_version": row[2],
            "consent_given": bool(row[3]),
            "timestamp": row[4]
        } for row in rows]
