import sys
import os
import gspread
from google.oauth2.service_account import Credentials
academic_module_dir = os.path.dirname(__file__)
general_functions_dir = os.path.join(academic_module_dir, '..')
sys.path.insert(1, general_functions_dir)
import general_functions as gen_functions
import decorated_gspread_methods

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

try:
    CREDS = Credentials.from_service_account_file('creds.json')
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    SHEET = GSPREAD_CLIENT.open('unigrade-physics')
except gspread.exceptions.GSpreadException:
    print('''ERROR ENCOUNTERED: There seems to be a problem accessing
the unigrade google sheet. The unigrade program will now terminate.
Please try running the program again. If the error persists try again later.\n''')
    print('Enter any key to initiate exiting the unigrade program.')
    input('->')
    system('clear')
    print('Quitting the unigrade program...')
    time.sleep(3.0)
    system('clear')
    sys.exit()




class AcademicModule:
    """
    Represents an academic module. Class/instance methods and properties featured pertain to adding and removing modules;
    viewing module statistics; assigning module weightings.
    """
    @classmethod
    def retrieve_year_x_modules(cls, x):
        """
        Produces a list of academic module titles for a chosen year x: 1<=x<=4, retrieved from the unigrade google sheet.
        """
        YEAR_X_MODULES_WORKSHEET = SHEET.worksheet(f'year {x} modules')
        year_x_modules = list(filter(lambda title: title != "", YEAR_X_MODULES_WORKSHEET.row_values(1)))
        return year_x_modules