from app.utils.env_utils import check_gemini_api_key, create_env_template, get_env_file_path


class LLMConsentManager:
    """Simple manager to ask: AI or local analysis?"""
    
    def ask_analysis_type(self, project_name: str) -> str:
        """
        Ask user to choose analysis type and validate requirements.
        """
        print(f"\n🔬 Analysis Choice for: {project_name}")
        print("="*50)
        
        # Check API key availability first
        api_available, api_status = check_gemini_api_key()
        
        if api_available:
            ai_option = "🤖 'ai'    - Enhanced analysis (uses AI services) ✅"
        else:
            ai_option = "🤖 'ai'    - Enhanced analysis (uses AI services) ❌ API key required"
        
        print("Choose analysis type:")
        print(f"  {ai_option}")
        print("  📊 'local' - Basic analysis (local only)")
        print()
        
        while True:
            choice = input("Choice (ai/local): ").lower().strip()
            
            if choice in ['ai', 'llm', 'gemini', 'enhanced']:
                if not api_available:
                    self._handle_missing_api_key(api_status)
                    continue  # Ask again after handling API key issue
                
                print(f"✅ AI analysis selected for '{project_name}'")
                return 'ai'
                
            elif choice in ['local', 'basic', 'offline', 'no-ai']:
                print(f"✅ Local analysis selected for '{project_name}'")
                return 'local'
                
            else:
                print("❌ Please enter 'ai' or 'local'")
    
    def _handle_missing_api_key(self, api_status: str):
        """Handle missing or invalid API key scenarios."""
        print("\n" + "🚨" + "="*58 + "🚨")
        print("   API KEY REQUIRED FOR AI ANALYSIS")
        print("🚨" + "="*58 + "🚨")
        
        if api_status == "missing":
            print("❌ GEMINI_API_KEY environment variable not found.")
        elif api_status == "empty":
            print("❌ GEMINI_API_KEY environment variable is empty.")
        elif api_status == "invalid_format":
            print("❌ GEMINI_API_KEY appears to be in invalid format.")
        
        print("\n📋 To use AI analysis, you need to:")
        print("   1️⃣  Get a Gemini API key from: https://aistudio.google.com/app/apikey")
        print("   2️⃣  Add it to your .env file as: GEMINI_API_KEY=your_key_here")
        print("   3️⃣  Restart the application")
        
        env_path = get_env_file_path()
        if not env_path.exists():
            while True:
                create_env = input(f"\n💡 Create template .env file at {env_path}? (y/n): ").lower().strip()
                if create_env in ['y', 'yes']:
                    if create_env_template():
                        print(f"✅ Template .env file created at: {env_path}")
                        print("   📝 Please edit it and add your Gemini API key.")
                    break
                elif create_env in ['n', 'no']:
                    break
                else:
                    print("❌ Please enter 'y' or 'n'")
        else:
            print(f"\n💡 Edit your existing .env file at: {env_path}")
        
        print("\n🔄 For now, please choose 'local' analysis or restart after adding the API key.")
        print("="*60)