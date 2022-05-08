import gspread
from google.oauth2.service_account import Credentials


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('unigrade-physics')



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
        year_x_modules = list(filter(lambda title: title != "", YEAR_x_MODULES_WORKSHEET.row_values(1)))
        return year_x_modules