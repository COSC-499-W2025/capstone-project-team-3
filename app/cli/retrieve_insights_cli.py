import json
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
        

        # Portfolio Section
        print("\n" + "="*60)
        print("📁 PORTFOLIO")
        print("="*60)
        print("\n✨ Projects & Summaries:\n")
        for proj in portfolio["projects"]:
            print(f"🗂️  {proj['name']}")
            print(f"📅 Duration: {proj['duration']}")
            print(f"📝 Summary: {proj['summary']}")
            print(f" 🛠️ Skills:")
            for skill in list(sorted(set(proj['skills'])))[:5]:  # Limit to 5 skills
                print(f"      • {skill}")
            print("\n" + "-"*40 + "\n")
            # Iterate over metrics from project and include in portfolio output
            if proj.get('metrics'):
                print(f" 📊 Metrics:")
                for metric_name, metric_value in proj['metrics'].items():  
                    print(f"      📈 {metric_name}: {metric_value}")  
            
            print("\n" + "-"*40 + "\n")

        print("🏆 Top Ranked Projects:\n")
        for proj in portfolio["top_projects"]:
            print(f"   🥇 {proj['name']} — ({proj['duration']}) \n ({proj['summary']})")
        print("\n📜 Chronological List of Projects:\n")
        for proj in portfolio["chronological"]:
            print(f"   ⏳ {proj['name']} — ({proj['duration']})")
        print("\n" + "="*60)

        # Resume Section
        print("📄 RESUME")
        print("="*60)
        if user_info:
            print(f"{user_info.get('name')} | 📧 Email: {user_info.get('email')}")
            print(f"🏢 Industry: {user_info.get('industry')} | 🎓 Education: {user_info.get('education')}")
        
        bullets_by_project = {}
        for entry in resume["bullets"]:
            project, items = _flatten_resume_entry(entry)
            bullets_by_project.setdefault(project, []).extend(items)

        for project_name, items in bullets_by_project.items():
            print(f"\n🗂️  {project_name}:")
            if not items:
                print("   • No resume bullets found")
                continue
            for bullet in items:
                print(f"   • {bullet}")
        print("\n" + "="*60)
        
        print("Download your resume in Latex/PDF format here:")
        print("   → http://localhost:8000/resume")
    else:
        print("Skipping display of past insights.")
        return

# Add this function after lookup_past_insights():

def get_specific_projects_info(project_signatures):
    """
    Get detailed information for specific projects by their signatures.
    
    Args:
        project_signatures (list): List of project signature strings
        
    Returns:
        dict: Formatted output with project details and summary
    """
    from app.utils.retrieve_insights_utils import get_projects_by_signatures
    
    if not project_signatures:
        return {
            "success": False,
            "message": "No project signatures provided",
            "projects": []
        }
    
    # Get projects using the utility function
    projects = get_projects_by_signatures(project_signatures)
    
    if not projects:
        return {
            "success": False,
            "message": "No projects found with the provided signatures",
            "projects": []
        }
    
    # Format output for CLI display
    formatted_output = {
        "success": True,
        "message": f"Found {len(projects)} project(s)",
        "projects": projects,
        "summary": {
            "total_projects": len(projects),
            "unique_skills": list(set(skill for proj in projects for skill in proj['skills'])),
            "date_range": {
                "earliest": min(proj['created_at'] for proj in projects),
                "latest": max(proj['created_at'] for proj in projects)
            }
        }
    }
    
    return formatted_output

def display_specific_projects(project_signatures):
    """
    Display detailed information for specific projects.
    
    Args:
        project_signatures (list): List of project signature strings
    """
    result = get_specific_projects_info(project_signatures)
    
    if not result["success"]:
        print(f"\n❌ {result['message']}")
        return
    
    projects = result["projects"]
    summary = result["summary"]
    
    print(f"\n📁 SPECIFIC PROJECT DETAILS")
    print("="*60)
    print(f"📊 {result['message']}")
    print(f"🎯 Skills Found: {len(summary['unique_skills'])} unique skills")
    print(f"📅 Date Range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
    print("="*60)
    
    for i, proj in enumerate(projects, 1):
        print(f"\n{i}. 🗂️  {proj['name']}")
        print(f"   📅 Duration: {proj['duration']}")
        print(f"   📝 Summary: {proj['summary']}")
        print(f"   🏆 Score: {proj['rank']}")
        
        # Skills
        print(f"   🛠️  Skills ({len(proj['skills'])}):")
        for skill in sorted(set(proj['skills']))[:8]:  # Limit to 8 skills
            print(f"      • {skill}")
        
        # Metrics
        if proj.get('metrics'):
            print(f"   📊 Metrics ({len(proj['metrics'])}):")
            for metric_name, metric_value in proj['metrics'].items():
                print(f"      📈 {metric_name}: {metric_value}")
        
        # ADD RESUME BULLETS SECTION
        if proj.get('resume_bullets'):
            print(f"   📄 Resume Bullets ({len(proj['resume_bullets'])}):")
            for bullet in proj['resume_bullets']:
                if bullet and bullet.strip():
                    print(f"      • {bullet}")
        else:
            print(f"   📄 Resume Bullets: None found")
        
        print("\n" + "-"*50)
    
    print(f"\n🎯 All Skills Across Selected Projects:")
    for skill in sorted(summary['unique_skills'])[:15]:  # Limit to 15 total skills
        print(f"   • {skill}")
    
    print("\n" + "="*60)
    
def _flatten_resume_entry(entry):
    project = entry.get("project_name", "Unknown Project")
    raw = entry.get("bullet", [])
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = [raw]
    if not isinstance(raw, list):
        raw = [str(raw)]
    return project, [b.strip() for b in raw if isinstance(b, str) and b.strip()]