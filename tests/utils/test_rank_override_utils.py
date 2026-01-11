import sqlite3

from app.utils.rank_override_utils import set_project_ranks


def test_set_project_ranks_overwrites_and_clears(monkeypatch, tmp_path):
    db_path = tmp_path / "rank_override.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE PROJECT (
            project_signature TEXT PRIMARY KEY,
            name TEXT,
            rank INTEGER
        )
        """
    )
    cur.executemany(
        "INSERT INTO PROJECT (project_signature, name, rank) VALUES (?, ?, ?)",
        [
            ("sig_1", "Project One", 5),
            ("sig_2", "Project Two", 4),
            ("sig_3", "Project Three", 3),
        ],
    )
    conn.commit()
    conn.close()

    def _get_connection():
        return sqlite3.connect(db_path)

    monkeypatch.setattr("app.utils.rank_override_utils.get_connection", _get_connection)

    set_project_ranks({"sig_1": 1, "sig_3": 3})

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT rank FROM PROJECT WHERE project_signature = 'sig_1'")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT rank FROM PROJECT WHERE project_signature = 'sig_2'")
    assert cur.fetchone()[0] is None
    cur.execute("SELECT rank FROM PROJECT WHERE project_signature = 'sig_3'")
    assert cur.fetchone()[0] == 3
    conn.close()
