class LLMConsentManager:
    """Simple manager to ask: AI or local analysis?"""
    
    def ask_analysis_type(self, project_name: str) -> str:
        """
        Ask user what type of analysis they want for this project.
        Returns 'ai', 'local', or 'skip'.
        """
        print("\n" + "="*50)
        print(f"🔬 Analysis Choice for: {project_name}")
        print("="*50)
        print("Choose analysis type:")
        print("  🤖 'ai'    - Enhanced analysis (uses AI services)")
        print("  📊 'local' - Basic analysis (local only)")
        
        while True:
            choice = input(f"\nChoice (ai/local): ").strip().lower()
            
            if choice in ['ai', 'llm']:
                print(f"✅ AI analysis selected for '{project_name}'")
                return 'ai'
            elif choice in ['local', 'basic']:
                print(f"✅ Local analysis selected for '{project_name}'")
                return 'local'
            else:
                print("❌ Please enter 'ai' or 'local'")