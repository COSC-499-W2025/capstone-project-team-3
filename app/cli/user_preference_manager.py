
from pathlib import Path
import sqlite3

# --- Constants ---
DB_PATH = Path(__file__).parent / "database.db"
industry_options = [
    "Technology",       
    "Healthcare",
    "Finance",
    "Education",
    "Manufacturing",
    "Retail",
    "Hospitality",
    "Transportation",
    "Construction",
    "Energy",
    "Entertainment",
    "Other"
]
def get_user_preferences(user_id):
    """
    Retrieve and/or save user preference input.
    """
    # TODO 1: Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # TODO 2: Check if the user has accepted consent in the DB
        # SELECT consent_status FROM CONSENT WHERE user_id = ?
        # If not accepted, print message and exit function

        # TODO 3: Check if user preferences already exist
        # SELECT * FROM USER_PREFERENCES WHERE user_id = ?
        # If preferences exist:
        #     a. Load and display current preferences
        #     b. Ask user if they want to update them (yes/no)
        #     If yes → continue to step 4
        #     If no → return current preferences

        # TODO 4: If no existing preferences, or user chooses to update:
        #     Prompt user for:
        #         - Educational background
        #         - Industry
        #         - Job title
        #     Validate inputs:
        #         a. If any field is empty, show an error and re-prompt

        # TODO 5: Save new or updated preferences to DB
        # Use INSERT OR REPLACE INTO USER_PREFERENCES (user_id, education, industry, job_title)
        # values (?, ?, ?, ?)

        # TODO 6: Commit transaction to save changes
        conn.commit()

    except sqlite3.Error as e:
        # TODO: Handle database errors 
        print(f"Database error: {e}")

    finally:
        # TODO 7: Close DB connection
        conn.close()

# Example usage
if __name__ == "__main__":
    # TODO: Replace with user_id from local storage or session
    user_id = 1
    get_user_preferences(user_id)
