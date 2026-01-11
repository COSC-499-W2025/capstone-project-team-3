from typing import Dict
from app.data.db import get_connection

def set_project_ranks(rank_map: Dict[str, int]) -> None:
    """
    rank_map: {project_signature: rank_int}
    Any project not in rank_map will have rank set to NULL.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Clear ranks for all projects first
        cur.execute("UPDATE PROJECT SET rank = NULL")

        # Apply new ranks
        for sig, rank in rank_map.items():
            cur.execute(
                "UPDATE PROJECT SET rank = ? WHERE project_signature = ?",
                (rank, sig),
            )

        conn.commit()
    finally:
        conn.close()
