import sqlite3
from app.data.db import get_connection, ensure_data_dir

def get_projects():
    """Return list of projects with name and project_signature."""
    ensure_data_dir()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, project_signature FROM PROJECT ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [{"name": r[0], "project_signature": r[1]} for r in rows]
    finally:
        conn.close()

def delete_project_by_signature(project_signature: str) -> bool:
    """Delete a project by exact project_signature. Returns True if deleted."""
    ensure_data_dir()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM PROJECT WHERE project_signature = ?", (project_signature,))
        deleted = cur.rowcount
        conn.commit()
        return deleted > 0
    finally:
        conn.close()