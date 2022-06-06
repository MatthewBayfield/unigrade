import sys
import os
import time
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
    gen_functions.clear()
    print('Quitting the unigrade program...')
    time.sleep(3.0)
    gen_functions.clear()
    sys.exit()


class AcademicModule:
    """
    Represents an academic module.
    
    Methods and attributes featured pertain to changing the module properties of existing modules in the unigrade google sheet,
    as well as adding new modules. Also includes class methods required by the Student class for processes such as
    student module enrolment. Finally includes methods and attributes necessary for producing module statistics.

    Attributes:
        title (str): the full title of the module.
        year (int): the year the module belongs to.
        activity (bool): indicating whether the module is currently active.
        availability (dict): a dictionary with 'study programme key':'boolean value' pairs indicating the module availability
                            on each programme.
        compulsory_status (dict): a dictionary with 'study programme key':'boolean value' pairs indicating if the module is
                                compulsory on each programme.
        module_credits (int): credits the module is worth.
    """
    def __init__(self, year, title, availablity, module_credits, compulsory_status, activity=True):
        self.title = title
        self.year = year
        self.activity = activity
        self.availablity = availablity
        self.compulsory_status = compulsory_status
        self.module_credits = module_credits

    @classmethod
    def retrieve_year_x_modules(cls, x):
        """
        Produces a list of all academic module titles for a chosen year x: 1<=x<=4, retrieved from the unigrade google sheet.
        """
        YEAR_X_MODULES_WORKSHEET = SHEET.worksheet(f'year {x} modules')
        year_x_modules = list(filter(lambda title: title != "", YEAR_X_MODULES_WORKSHEET.row_values(1)))
        return year_x_modules

    @classmethod
    def retrieve_active_year_x_modules(cls, x, programme):
        """
        Returns a list of the currently active academic module titles for the programme 'MSci Physics' or 'BSc Physics', and year x: 1<=x<=4, retrieved from the unigrade google sheet.
        """
        module_information_worksheet = SHEET.worksheet('module properties')
        year_x_module_titles_col_number = module_information_worksheet.find(f'Year {x} Module Titles').col

        if programme == 'MSci Physics':
            module_info = module_information_worksheet.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 2)[:-1]}'],
                                                                 major_dimension='ROWS')
        elif programme == 'BSc Physics':
            module_info = module_information_worksheet.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 1)[:-1]}',
                                                                 f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 4)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 4)[:-1]}'],
                                                                 major_dimension='ROWS')
            available_on_bsc_list = module_info.pop()
            for i in range(0, len(available_on_bsc_list), 1):
                module_info[0][i].extend(available_on_bsc_list[i])

        active_modules = [list[0] for list in module_info[0] if list.count('X') == 2]
        return active_modules

    @classmethod
    def retrieve_active_and_compulsory_year_x_modules(cls, x, programme):
        """
        Returns a list of the currently active and compulsory academic module titles for the programme 'MSci Physics' or 'BSc Physics', and year x: 1<=x<=4, retrieved from the unigrade google sheet.
        """
        active_modules = AcademicModule.retrieve_active_year_x_modules(x, programme)
        module_information_worksheet = SHEET.worksheet('module properties')
        year_x_module_titles_col_number = module_information_worksheet.find(f'Year {x} Module Titles').col

        if programme == 'MSci Physics':
            module_info = module_information_worksheet.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number)[:-1]}',
                                                                  f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 3)}:{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 3)[:-1]}'],
                                                                 major_dimension='ROWS')
        elif programme == 'BSc Physics':
            module_info = module_information_worksheet.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number)[:-1]}', 
                                                                  f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 5)}:{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 5)[:-1]}'],
                                                                 major_dimension='ROWS')

        compulsory_on_programme_list = module_info.pop()
        for i in range(0, len(compulsory_on_programme_list), 1):
            module_info[0][i].extend(compulsory_on_programme_list[i])

        compulsory_modules = [list[0] for list in module_info[0] if list.count('X') == 1]
        active_and_compulsory_modules = [module_title for module_title in compulsory_modules if module_title in active_modules]
        return active_and_compulsory_modules

    @classmethod
    def retrieve_year_x_module_credits(cls, x):
        """
        Returns a dictionary containing the module credits for modules of a chosen year x parameter.
        """
        module_properties_worksheet = SHEET.worksheet('module properties')
        year_x_module_titles_col_number = module_properties_worksheet.find(f'Year {x} Module Titles').col

        module_credits_info = module_properties_worksheet.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number)[:-1]}',
                                                                    f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 6)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 6)[:-1]}'],
                                                                     major_dimension='ROWS')
        year_x_module_credits_dict = {}
        credits_list = module_credits_info.pop()
        for i in range(0, len(credits_list), 1):
            year_x_module_credits_dict[module_credits_info[0][i][0]] = int(credits_list[i][0])
        return year_x_module_credits_dict
