import json
from pathlib import Path

# Import the functions from your git_utils.py file
try:
    from git_utils import (
        extract_code_commit_content_by_author, 
        
    )
except ImportError:
    print("Error: Could not find git_utils.py.")
    print("Please make sure this script is in the same directory as git_utils.py")
    exit(1)

# --- Configuration ---
# 1. SET THE PATH TO YOUR GIT REPOSITORY HERE
#    (e.g., r"C:\Users\YourName\Projects\my-project" or "/home/user/my-project")
YOUR_REPO_PATH = "/Users/karimjassani/Desktop/COSC 499 Capstone/Capstone Project/capstone-project-team-3"


# 2. SET THE AUTHOR NAME OR EMAIL YOU WANT TO FIND
YOUR_AUTHOR_NAME = "kjassani"
# --- End of Configuration ---

def main():
    print(f"Analyzing repo at: {YOUR_REPO_PATH}")
    print(f"Searching for author: {YOUR_AUTHOR_NAME}")
    
    # --- This is where the function is called ---
    try:
        # We also pass max_commits=50 as a safety limit so it runs fast.
        # Feel free to remove 'max_commits' to get everything.
        json_output = extract_code_commit_content_by_author(
            path=YOUR_REPO_PATH,
            author=YOUR_AUTHOR_NAME,
            max_commits=50 
        )
        
        # --- This prints the final JSON to your console ---
        print("\n--- ANALYSIS COMPLETE ---")
        print(json_output)
        
        # # Optional: Save the output to a file
        # output_filename = "commit_analysis.json"
        # Path(output_filename).write_text(json_output, encoding="utf-8")
        # print(f"\nSuccessfully saved output to {output_filename}")

    except ValueError as e:
        print(f"\n--- ERROR ---")
        print(f"An error occurred: {e}")
        print("Please check that the path to your repository is correct.")
    except Exception as e:
        print(f"\n--- AN UNEXPECTED ERROR OCCURRED ---")
        print(e)

if __name__ == "__main__":
    # This makes the script runnable from the command line
    main()
 