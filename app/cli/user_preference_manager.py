
from pathlib import Path
import sqlite3

# //TO DO: 
# 1. Check User has accepted consent value in DB
# 2. If yes, check for existing user preferences
#     a. If yes, load preferences and give user option to update 
#     b. If no, proceed to ask user for their educational backgroud, select a industry and input a job_title,
# 4. Save user preferences to DB
#     a. If any field is empty, show error message and re-prompt user for input
# 5. Close DB connection