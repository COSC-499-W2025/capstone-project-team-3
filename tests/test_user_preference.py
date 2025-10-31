def test_save_and_get_preferences(tmp_path):
    db_path = tmp_path / "prefs.db"
    store = UserPreferenceStore(db_path=db_path)
    try:
        store.save_preferences(
            user_id="user1",
            name="Alice Example",
            github="alicegit",
            education="BSc Computer Science",
            industry="Technology",
            job_title="Developer"
        )

        prefs = store.get_preferences("user1")
        assert prefs is not None
        expected_keys = {"user_id", "name", "github", "education", "industry", "job_title"}
        assert set(prefs.keys()) == expected_keys
        assert prefs["name"] == "Alice Example"
        assert prefs["github"] == "alicegit"
    finally:
        store.close()

def test_get_preferences_returns_none_for_missing(tmp_path):
    db_path = tmp_path / "prefs.db"
    store = UserPreferenceStore(db_path=db_path)
    try:
        assert store.get_preferences("missing_user") is None
    finally:
        store.close()

def test_save_preferences_updates_existing_row(tmp_path):
    db_path = tmp_path / "prefs.db"
    store = UserPreferenceStore(db_path=db_path)
    try:
        store.save_preferences("user2", "First Name", "gh1", "MS", "Finance", "Analyst")
        store.save_preferences("user2", "Second Name", "gh2", "PhD", "Healthcare", "Senior Analyst")

        prefs = store.get_preferences("user2")
        assert prefs is not None
        assert prefs["name"] == "Second Name"
        assert prefs["github"] == "gh2"
        assert prefs["industry"] == "Healthcare"
    finally:
        store.close()