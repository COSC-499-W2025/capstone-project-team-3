from app.utils.user_preference_utils import UserPreferenceStore

"This file manages user preferences via CLI by prompting the user. This will later on be replaced by UI"

DB_PATH = Path(__file__).parent / "db.py"
USER_ID = 

industry_options = [
    "Technology", "Healthcare", "Finance", "Education", "Manufacturing",
    "Retail", "Hospitality", "Transportation", "Construction", "Energy",
    "Entertainment", "Other"
]

class UserPreferences:
    def __init__(self, store: Optional[UserPreferenceStore] = None):
        self.store = store or UserPreferenceStore()

    def manage_preferences(self):
        try:
            user_id = input("Enter a user id (email or username) to load/save preferences: ").strip()
            if not user_id:
                print("User id is required.")
                return

            existing = self.store.get_preferences(user_id)
            if existing:
                print("Existing preferences found:")
                for k, v in existing.items():
                    print(f"  {k}: {v}")
                choice = input("Would you like to update them? (yes/no): ").strip().lower()
                if choice == "no":
                    print("Keeping existing preferences.")
                    return

            name = input("Enter your full name: ").strip()
            github = input("Enter your GitHub username (or leave blank): ").strip()
            while True:
                education = input("Enter your educational background: ").strip()
                print(f"Industry options: {industry_options}")
                industry = input("Select your industry (type one of the options): ").strip()
                job_title = input("Enter your job title (current or aspiring): ").strip()

                if not education or not industry or not job_title:
                    print("Missing fields are required. Please try again.")
                else:
                    break

            self.store.save_preferences(
                user_id=user_id,
                name=name,
                github_user=github,
                education=education,
                industry=industry,
                job_title=job_title
            )
            print("Preferences saved successfully.")

        finally:
            self.store.close()

if __name__ == "__main__":
    UserPreferences().manage_preferences()
