from pathlib import Path
import sqlite3
from consent_manager import ConsentManager

"This file manages user preferences via CLI by prompting the user. This will later on be replaced by UI"

DB_PATH = Path(__file__).parent / "db.py"
USER_ID = 

industry_options = [
    "Technology", "Healthcare", "Finance", "Education", "Manufacturing",
    "Retail", "Hospitality", "Transportation", "Construction", "Energy",
    "Entertainment", "Other"
]

class UserPreferences:
    def __init__(self):
        self.user_id = USER_ID
        self.education = ""
        self.industry = ""
        self.job_title = ""
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def get_preferences

    def manage_preferences(self):
        try:
            # --- TODO 2: Check consent ---
            consent_manager = ConsentManager()
            if not consent_manager.has_consent(self.user_id):
                print("User consent not found. Please provide consent first.")
                return

            # --- TODO 3: Check for existing preferences ---
            self.cursor.execute("SELECT * FROM USER_PREFERENCES WHERE user_id = ?", (self.user_id,))
            existing = self.cursor.fetchone()

            if existing:
                print(f"Existing preferences: {existing}")
                choice = input("Would you like to update them? (yes/no): ").strip().lower()
                if choice == "no":
                    print("Keeping existing preferences.")
                    return

            # --- TODO 4: Collect new or updated preferences ---
            while True:
                education = input("Enter your educational background: ").strip()
                industry = input(f"Select your industry {industry_options}: ").strip()
                job_title = input("Enter your job title. This can be current or aspiring: ").strip()

                if not education or not industry or not job_title:
                    print("Missing fields are required. Please try again.")
                else:
                    break

            self.education = education
            self.industry = industry
            self.job_title = job_title

            # --- TODO 5: Save to DB ---
            self.cursor.execute("""
                INSERT OR REPLACE INTO USER_PREFERENCES (user_id, education, industry, job_title)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, self.education, self.industry, self.job_title))

            # --- TODO 6: Commit ---
            self.conn.commit()
            print("Preferences saved successfully.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")

        finally:
            # --- TODO 7: Close connection ---
            self.conn.close()

if __name__ == "__main__":
    manager = UserPreferences()
    manager.manage_preferences()
