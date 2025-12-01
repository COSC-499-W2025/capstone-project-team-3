from app.utils.retrieve_insights_utils import get_portfolio_resume_insights
from app.utils.user_preference_utils import UserPreferenceStore 


def lookup_past_insights():
   
    print("\nWe found previously generated insights for your projects.")
    view_past = input("Would you like to view your portfolio and resume insights? (yes/no): ").lower().strip()
    if view_past in ("yes", "y"):
        # Print heading
        print("\n--- Previously analyzed projects ---")
        print("\n" + "="*60)
        # Retrieve and display portfolio and resume insights from retrieval utils
        portfolio, resume = get_portfolio_resume_insights()
        
        # Check for empty data
        if not portfolio["projects"]:
            print("No projects found.")
            print("\n" + "="*60)
        if not resume["bullets"]:
            print("No resume bullets found.")
            print("\n" + "="*60)
        if not portfolio["projects"] or not resume["bullets"]:
            return
        
        # Grab user information
        user_info = UserPreferenceStore.get_user_info()
        
        # Display 
        print("\n" + "="*60)
        print("📁 PORTFOLIO")
        print("="*60)
        print("\nProjects & Summaries:")
        for proj in portfolio["projects"]:
            print(f"- {proj['name']} ({proj['created_at']}) (Duration: {proj['duration']})")
            print(f"  Summary: {proj['summary']}")
            print(f"  Skills: {', '.join(proj['skills'])}")
        print("\nTop Ranked Projects:")
        for proj in portfolio["top_projects"]:
            print(f"- {proj['name']} ({proj['created_at']}) (Duration: {proj['duration']})")
        print("\nChronological List of Projects:")
        for proj in portfolio["chronological"]:
            print(f"- {proj['name']} ({proj['created_at']}) (Duration: {proj['duration']})")
        print("\n" + "="*60)
        print("📄 RESUME")
        print("="*60)
        print(f"User: {user_info.get('name')} | Email: {user_info.get('email')}")
        print(f"Industry: {user_info.get('industry')} | Job Title: {user_info.get('job_title')} | Education: {user_info.get('education')}")
        for bullet in resume["bullets"]:
            print(f"- {bullet}") 
    else:
        print("Skipping display of past insights.")
        return
