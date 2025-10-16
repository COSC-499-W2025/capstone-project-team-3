import os
from consent_management.consent_text import CONSENT_MESSAGE, DETAILED_PRIVACY_INFO

class ConsentCLI:
    def __init__(self, consent_manager):
        self.consent_manager = consent_manager
    
    def prompt_for_consent(self):
        """Display consent prompt and get user's decision"""
        # Clear screen for better readability
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display the consent message
        print(CONSENT_MESSAGE)
        
        # Get user response
        while True:
            response = input("\nDo you accept? (yes/no/more): ").strip().lower()
            
            if response == 'more':
                self._show_detailed_info()
                # After showing details, show consent message again
                print(CONSENT_MESSAGE)
            elif response in ('yes', 'y'):
                self.consent_manager.record_consent(True)
                return True
            elif response in ('no', 'n'):
                self.consent_manager.record_consent(False)
                return False
            else:
                print("Please answer 'yes', 'no', or 'more'.")
    
    def _show_detailed_info(self):
        """Show detailed privacy information"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(DETAILED_PRIVACY_INFO)
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')