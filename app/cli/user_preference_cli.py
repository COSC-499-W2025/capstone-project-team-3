from app.utils.user_preference_utils import UserPreferenceStore
import re

"This file manages user preferences via CLI by prompting the user. This will later on be replaced by UI"


industry_options = [
    "Technology", "Healthcare", "Finance", "Education", "Manufacturing",
    "Retail", "Hospitality", "Transportation", "Construction", "Energy",
    "Entertainment", "Other"
]

class UserPreferences:
    def __init__(self, store: UserPreferenceStore = None):
        self.store = store or UserPreferenceStore()

    def manage_preferences(self):
        """
        Prompt user to enter or update their preferences via CLI.
        """
        while True:
            email = input("Enter your email: ").strip()
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                print("Invalid email format. Please try again.")
            else:
                break  # Exit the loop when a valid email is entered

        existing_preferences = self.store.get_latest_preferences(email)
        if existing_preferences:
            print("Existing preferences found: ")
            for k, v in existing_preferences.items():
                print(f"  {k}: {v}")
            choice = input("Would you like to update them? (yes/no): ").strip().lower()
            if choice == "no":
                print("Keeping existing preferences.")
                return

        name = input("Enter your full name: ").strip()
        github = input("Enter your GitHub username if you have one(or leave blank): ").strip()
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
            name=name,
            email=email,
            github_user=github,
            education=education,
            industry=industry,
            job_title=job_title
        )
        print("Preferences saved successfully.")


    def get_latest_preferences(self, email):
        """
        Retrieve the latest user preferences.
        """
        return self.store.get_latest_preferences(email)

if __name__ == "__main__":
    try:
        UserPreferences().manage_preferences()
    finally:
        UserPreferences().store.close()
