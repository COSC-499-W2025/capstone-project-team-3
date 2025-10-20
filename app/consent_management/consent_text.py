# Main consent message shown to users initially
CONSENT_MESSAGE = """
=======================================================
PROJECT INSIGHTS - CONSENT AGREEMENT
=======================================================

This application needs your permission to:

1. Access and analyze your project files
2. Read Git history and contribution data 
3. Store analysis results locally

Your data remains on your machine and is not uploaded.
For more details, type 'more' or press Enter to continue.
"""

# Detailed privacy information shown when user requests more details
DETAILED_PRIVACY_INFO = """
=======================================================
PRIVACY DETAILS
=======================================================

DATA COLLECTION:
- Project file names, sizes, and content are analyzed locally
- Git commit history including authors and timestamps
- Language and framework detection results

DATA STORAGE:
- All results stored in local database
- Located at: ~/.project_insights/data.db
- No cloud upload or sharing of your data

DATA RETENTION:
- Data kept until explicitly deleted by you
- Use '--clear-data' command to remove all stored information

Press Enter to return to consent prompt.
"""

# Message shown when consent is granted
CONSENT_GRANTED_MESSAGE = """
✅ Consent granted! 

Thank you for providing consent. Project Insights is now ready to
analyze your project and provide valuable insights about your code.
"""

# Message shown when consent is declined
CONSENT_DECLINED_MESSAGE = """
⛔ You've declined consent.

Project Insights needs these permissions to function properly.
You can run the tool again if you change your mind.
"""

# Message shown when resuming with existing consent
CONSENT_ALREADY_PROVIDED_MESSAGE = """
✓ Consent previously provided.

Project Insights will continue analyzing your project.
To revoke consent, use the '--revoke-consent' command.
"""