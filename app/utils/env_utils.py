# Create a new file for environment utilities

import os
from pathlib import Path

def check_gemini_api_key() -> tuple[bool, str]:
    """
    Check if GEMINI_API_KEY is available and valid.
    Returns (is_valid, message)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return False, "missing"
    
    if api_key.strip() == "":
        return False, "empty"
    
    # Basic validation - Gemini API keys typically start with specific pattern
    if not api_key.startswith(("AIza", "ya29.")):
        return False, "invalid_format"
    
    return True, "valid"

def get_env_file_path() -> Path:
    """Get the expected .env file path."""
    return Path.cwd() / ".env"

def create_env_template():
    """Create a template .env file with instructions."""
    env_path = get_env_file_path()
    template = """# Project Insights Environment Variables
# 
# Get your Gemini API key from: https://aistudio.google.com/app/apikey
# 
GEMINI_API_KEY=your_api_key_here

# Other optional variables
# PROMPT_ROOT=1
"""
    
    if not env_path.exists():
        env_path.write_text(template)
        return True
    return False