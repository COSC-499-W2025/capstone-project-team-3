from pathlib import Path

class ConsentManager:
    def __init__(self):
        """Initialize simple consent manager"""
        # Setup basic file storage until database is connected
        self.data_dir = Path.home() / ".project_insights"
        self.data_dir.mkdir(exist_ok=True)
        self.consent_file = self.data_dir / "consent_status.txt"
    
    def has_consent(self):
        """Check if consent has been given"""
        if not self.consent_file.exists():
            return False
            
        content = self.consent_file.read_text().strip()
        return content == "accepted"
    
    def record_consent(self, accepted):
        """Temporarily record consent status to file"""
        # TODO: Replace with database storage once connected
        status = "accepted" if accepted else "declined"
        self.consent_file.write_text(status)
        
        print(f"[Debug] Consent status ({status}) stored temporarily. Will be in database later.")
        return True