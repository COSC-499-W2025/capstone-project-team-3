from app.utils.env_utils import check_gemini_api_key, create_env_template, get_env_file_path

class LLMConsentManager:
    """Simple manager to ask: AI or local analysis?"""
    
    def ask_analysis_type(self, project_name: str) -> str:
        """
        Ask user to choose analysis type and validate requirements.
        """
        print(f"\n🔬 Analysis Choice for: {project_name}")
        print("="*60)
        
        # Check API key availability first
        api_available, api_status = check_gemini_api_key()
        
        # ENHANCED PRIVACY AND DATA IMPLICATIONS SECTION
        print("📊 ANALYSIS OPTIONS & DATA PRIVACY INFORMATION")
        print("="*60)
        
        print("\n🏠 LOCAL ANALYSIS:")
        print("   ✅ All processing happens on your machine")
        print("   ✅ No data leaves your computer")
        print("   ✅ Complete privacy - your code stays local")
        print("   ✅ Works offline")
        print("   ⚠️  Limited analysis capabilities (basic metrics only)")
        print("   ⚠️  No advanced insights or resume generation")
        
        if api_available:
            print("\n🤖 AI-ENHANCED ANALYSIS:")
            print("   ✅ Advanced insights and professional resume bullet generation")
            print("   ✅ Intelligent code pattern recognition")
            print("   ✅ Comprehensive project analysis")
            print("   ⚠️  PRIVACY IMPLICATIONS:")
            print("      📤 Project metrics and code patterns sent to Google Gemini API")
            print("      📤 File names, function names, and code structure analyzed remotely")
            print("      📤 Technical keywords and project summaries processed by AI")
            print("      🚫 Your actual source code content is NOT sent")
            print("      🚫 Sensitive data like passwords/keys are filtered out")
            print("      🔒 Data transmission encrypted (HTTPS)")
            print("      📋 Subject to Google's privacy policy: https://policies.google.com/privacy")
            print("      ⏱️  Data retention governed by Google's AI service terms")
            
            print(f"\n💡 WHAT GETS SENT TO AI:")
            print("   • Project structure and file organization")
            print("   • Programming languages used")
            print("   • Function/class names and counts")
            print("   • Import statements and dependencies")
            print("   • Code complexity metrics")
            print("   • Git commit patterns (if analyzing git repo)")
            
            print(f"\n🚫 WHAT NEVER GETS SENT:")
            print("   • Actual source code content")
            print("   • Variable values or business logic")
            print("   • Database credentials or API keys")
            print("   • Personal information in comments")
            
            ai_option = "🤖 'ai'    - Enhanced analysis (with data sharing) ✅"
        else:
            print("\n🤖 AI-ENHANCED ANALYSIS:")
            print("   ❌ Requires Gemini API key")
            print("   📋 Would provide advanced insights if configured")
            ai_option = "🤖 'ai'    - Enhanced analysis ❌ API key required"
        
        print("\n" + "="*60)
        print("CHOOSE YOUR ANALYSIS TYPE:")
        print("="*60)
        print(f"  {ai_option}")
        print("  🏠 'local' - Basic analysis (completely private)")
        print("\n📋 By choosing 'ai', you consent to sending project metadata to Google Gemini API")
        print("   for analysis purposes as described above.")
        print()
        
        while True:
            choice = input("Choice (ai/local): ").lower().strip()
            
            if choice in ['ai', 'llm', 'gemini', 'enhanced']:
                if not api_available:
                    self._handle_missing_api_key(api_status)
                    continue  # Ask again after handling API key issue
                
                # ADDITIONAL CONFIRMATION FOR AI CHOICE
                print(f"\n🔐 FINAL PRIVACY CONFIRMATION")
                print("="*40)
                print("You've chosen AI-enhanced analysis. This means:")
                print("• Project structure data will be sent to Google Gemini API")
                print("• Your actual source code content remains on your machine")
                print("• Analysis results will be more comprehensive")
                
                while True:
                    confirm = input("\n✅ Do you consent to this data sharing? (yes/no): ").lower().strip()
                    if confirm in ['yes', 'y', 'consent', 'agree', 'ok']:
                        print(f"✅ AI analysis selected for '{project_name}' with user consent")
                        return 'ai'
                    elif confirm in ['no', 'n', 'decline', 'disagree']:
                        print("🔄 Switching to local analysis to preserve privacy...")
                        print(f"✅ Local analysis selected for '{project_name}'")
                        return 'local'
                    else:
                        print("❌ Please enter 'yes' to consent or 'no' to decline")
                
            elif choice in ['local', 'basic', 'offline', 'no-ai', 'private']:
                print(f"✅ Local analysis selected for '{project_name}' - your data stays private")
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
        print("   2️⃣  Review Google's privacy policy: https://policies.google.com/privacy")
        print("   3️⃣  Add it to your .env file as: GEMINI_API_KEY=your_key_here")
        print("   4️⃣  Restart the application")
        
        print("\n⚠️  PRIVACY REMINDER:")
        print("   By using Gemini API, your project metadata will be sent to Google")
        print("   for analysis. Your source code content stays on your machine.")
        
        env_path = get_env_file_path()
        if not env_path.exists():
            while True:
                create_env = input(f"\n💡 Create template .env file at {env_path}? (y/n): ").lower().strip()
                if create_env in ['y', 'yes']:
                    if create_env_template():
                        print(f"✅ Template .env file created at: {env_path}")
                        print("   📝 Please edit it and add your Gemini API key.")
                        print("   📋 Remember: review Google's privacy policy before use.")
                    break
                elif create_env in ['n', 'no']:
                    break
                else:
                    print("❌ Please enter 'y' or 'n'")
        else:
            print(f"\n💡 Edit your existing .env file at: {env_path}")
            print("   📋 Remember: review Google's privacy policy before use.")
        
        print("\n🔄 For now, please choose 'local' analysis or restart after adding the API key.")
        print("="*60)