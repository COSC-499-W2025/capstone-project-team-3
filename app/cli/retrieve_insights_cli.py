from app.utils.delete_insights_utils import get_projects
from app.utils.retrieve_insights_utils import get_project_insights 


def lookup_past_insights(existing_projects):
   
    print("\nWe found previously generated insights for your projects.")
    view_past = input("Would you like to view your portfolio and resume insights? (yes/Enter to skip): ").lower().strip()
    if view_past in ("yes", "y"):
        # Print heading
        print("\n--- Previously analyzed projects ---")
        print("\n" + "="*60)
        # Retrieve and display portfolio and resume insights from retrieval utils
        portfolio, resume = get_portfolio_resume_insights()

        # Display 
        print("\n" + "="*60)
        print("📁 PORTFOLIO")
        print("="*60)
        print("\nProjects & Summaries:")
        for proj in portfolio["projects"]:
            print(f"- {proj['name']} ({proj['duration']})")
            print(f"  Summary: {proj['summary']}")
            print(f"  Skills: {', '.join(proj['skills'])}")
        print("\nTop Ranked Projects:")
        for proj in portfolio["top_projects"]:
            print(f"- {proj['name']} ({proj['duration']})")
        print("\nChronological List of Projects:")
        for proj in portfolio["chronological"]:
            print(f"- {proj['name']} ({proj['uploaded_at']})")
        print("\n" + "="*60)
        print("📄 RESUME")
        print("="*60)
        for bullet in resume["bullets"]:
            print(f"- {bullet}")
        
