import sys
import os
import time
import numpy as np
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
    Represents an academic module in the unigrade google sheet.

    Methods and attributes featured pertain to changing the module properties of existing modules in the unigrade google
    sheet, as well as adding new modules. Also includes class methods required by the Student class for processes such as
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
    def __init__(self, year, title, availability, module_credits,
                 compulsory_status, activity=True):
        self.title = title
        self.year = year
        self.activity = activity
        self.availability = availability
        self.compulsory_status = compulsory_status
        self.module_credits = module_credits

    @classmethod
    def retrieve_year_x_modules(cls, x):
        """
        Returns a list of all academic module titles for a chosen year x: 1<=x<=4, retrieved from the unigrade google sheet.
        """
        YEAR_X_MODULES_WORKSHEET = SHEET.worksheet(f'year {x} modules')
        year_x_modules = list(filter(lambda title: title != "",
                              YEAR_X_MODULES_WORKSHEET.row_values(1)))
        return year_x_modules

    @classmethod
    def retrieve_active_year_x_modules(cls, x, study_programme):
        """
        Returns a list of the active module titles for a programme and year x: 1<=x<=4, retrieved from the unigrade google sheet.
        """
        MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
        year_x_module_titles_col_number = MODULE_PROPERTIES_WORKSHEET.find(f'Year {x} Module Titles').col

        if study_programme == 'MSci Physics':
            module_info = MODULE_PROPERTIES_WORKSHEET.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 2)[:-1]}'],
                                                                major_dimension='ROWS')
        elif study_programme == 'BSc Physics':
            module_info = MODULE_PROPERTIES_WORKSHEET.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 1)[:-1]}',
                                                                f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 4)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 4)[:-1]}'],
                                                                major_dimension='ROWS')
            available_on_bsc_list = module_info.pop()
            for i in range(0, len(available_on_bsc_list), 1):
                module_info[0][i].extend(available_on_bsc_list[i])

        active_modules = [list[0] for list in module_info[0] if list.count('X') == 2]
        return active_modules

    @classmethod
    def retrieve_active_and_compulsory_year_x_modules(cls, x, study_programme):
        """
        Returns a list of the active and compulsory module titles for a programme and year x, retrieved from the unigrade google sheet.

        Args:
            x (int): the academic year the modules belong to, where 1<=x<=4.
            study_programme (str): the study programme the modules must be available on. Has the value 'MSci Physics' or 'BSc Physics'.

        """
        active_modules = AcademicModule.retrieve_active_year_x_modules(x, study_programme)
        MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
        year_x_module_titles_col_number = MODULE_PROPERTIES_WORKSHEET.find(f'Year {x} Module Titles').col

        if study_programme == 'MSci Physics':
            module_info = MODULE_PROPERTIES_WORKSHEET.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number)[:-1]}',
                                                                f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 3)}:{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 3)[:-1]}'],
                                                                major_dimension='ROWS')
        elif study_programme == 'BSc Physics':
            module_info = MODULE_PROPERTIES_WORKSHEET.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number)[:-1]}',
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
        Returns a dictionary containing the module credits for modules of a chosen year x: 1<=x<=4.
        """
        MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
        year_x_module_titles_col_number = MODULE_PROPERTIES_WORKSHEET.find(f'Year {x} Module Titles').col

        module_credits_info = MODULE_PROPERTIES_WORKSHEET.batch_get([f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number)[:-1]}',
                                                                    f'{gspread.utils.rowcol_to_a1(2, year_x_module_titles_col_number + 6)}:{gspread.utils.rowcol_to_a1(1, year_x_module_titles_col_number + 6)[:-1]}'],
                                                                    major_dimension='ROWS')
        year_x_module_credits_dict = {}
        credits_list = module_credits_info.pop()
        for i in range(0, len(credits_list), 1):
            year_x_module_credits_dict[module_credits_info[0][i][0]] = int(credits_list[i][0])
        return year_x_module_credits_dict

    @classmethod
    def retrieve_active_and_optional_year_x_modules(cls, x, study_programme):
        """
        Returns a list of the active optional modules for the academic year x and specified study programme.

        Retrieved from the unigrade google sheet.

        Args:
            x (int): the academic year to which the modules belong.
            study programme (str): the programme the modules must be taught on.
        """
        active_modules_this_year = AcademicModule.retrieve_active_year_x_modules(x, study_programme)
        active_and_compulsory_modules_this_year = AcademicModule.retrieve_active_and_compulsory_year_x_modules(x, study_programme)
        active_optional_modules_this_year_and_programme = [module for module in active_modules_this_year if module not in active_and_compulsory_modules_this_year]
        return active_optional_modules_this_year_and_programme

    @classmethod
    def fetch_module(cls, module_title):
        """
        Returns an AcademicModule instance with the requested module_title, if it exists.

        Searches the unigrade google sheet for a module with the specified module title; if it exists,
        its properties in the 'module properties worksheet' are retrieved and used to create an
        instance which is then returned. If it does not exist, a string is returned.

        Args:
            module_title (str): The module title of the module to fetch.
        """
        MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
        module_title_entry_cell = MODULE_PROPERTIES_WORKSHEET.find(f'{module_title}')
        if module_title_entry_cell is not None:
            module_properties_batch_get_range = f"{gspread.utils.rowcol_to_a1(module_title_entry_cell.row, module_title_entry_cell.col + 1)}:{gspread.utils.rowcol_to_a1(module_title_entry_cell.row, module_title_entry_cell.col + 6)}"
            module_properties_raw = MODULE_PROPERTIES_WORKSHEET.batch_get([module_properties_batch_get_range],
                                                                          major_dimension='ROWS')[0][0]
            module_year = int(MODULE_PROPERTIES_WORKSHEET.cell(1, module_title_entry_cell.col).value.split(' ')[1])

            programmes = ['MSci Physics', 'BSc Physics']
            activity = True if module_properties_raw[0] == 'X' else False
            module_credits = int(module_properties_raw[-1])
            availability = {}
            compulsory_status = {}
            j = 1
            i = 2
            while j <= len(programmes):
                availability[programmes[j - 1]] = True if module_properties_raw[i - 1] == 'X' else False
                i += 1
                compulsory_status[programmes[j - 1]] = True if module_properties_raw[i - 1] == 'X' else False
                i += 1
                j += 1

            return AcademicModule(module_year, module_title, availability,
                                  module_credits, compulsory_status, activity)
        else:
            return 'No module with this title exists.'

    def add_module(self):
        """
        Adds a new module, represented by the AcademicModule instance, to the unigrade google sheet.

        Uses instance properties, and appends a new module section to the 'year {self.year} modules worksheet' of the
        unigrade google sheet. Also adds a new row, containing the module properties, in the 'module properties worksheet'.
        Uses various gspread methods to preserve the formatting and layout of each unigrade worksheet.
        """
        MODULE_YEAR_MODULES_SHEET = SHEET.worksheet(f'year {self.year} modules')
        last_module_title = list(filter(lambda title: title != "", MODULE_YEAR_MODULES_SHEET.row_values(1)))[-1]
        last_occupied_column_index = MODULE_YEAR_MODULES_SHEET.find(last_module_title).col + 4

        append_columns_body = {
            "requests": [
                {
                    "appendDimension": {
                        "sheetId": MODULE_YEAR_MODULES_SHEET.id,
                        "dimension": "COLUMNS",
                        "length": 6
                    }
                }
            ]
        }
        SHEET.batch_update(append_columns_body)

        copy_paste_body = {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": MODULE_YEAR_MODULES_SHEET.id,
                            "startRowIndex": 0,
                            "endRowIndex": 2,
                            "startColumnIndex": last_occupied_column_index - 5,
                            "endColumnIndex": last_occupied_column_index

                        },
                        "destination": {
                            "sheetId": MODULE_YEAR_MODULES_SHEET.id,
                            "startRowIndex": 0,
                            "endRowIndex": 2,
                            "startColumnIndex": last_occupied_column_index + 1,
                            "endColumnIndex": last_occupied_column_index + 5
                        },
                        "pasteType": "PASTE_NORMAL",
                        "pasteOrientation": "NORMAL"
                    }
                }
            ]
        }
        # copies module section headings and formatting, and pastes them at the top of the newly created columns
        SHEET.batch_update(copy_paste_body)
        gen_functions.update_sheet_borders(MODULE_YEAR_MODULES_SHEET, SHEET)

        background_color_body = {
            "backgroundColor": {
                "red": 0,
                "green": 0,
                "blue": 0,
            }
        }
        # gives a black fill to the column separator between the newly created and previous module sections
        MODULE_YEAR_MODULES_SHEET.format(f"{gspread.cell.Cell(1, last_occupied_column_index + 1).address}:{gspread.cell.Cell(MODULE_YEAR_MODULES_SHEET.row_count, last_occupied_column_index + 1).address}",
                                         background_color_body)

        column_sizing_body = {
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": MODULE_YEAR_MODULES_SHEET.id,
                            "dimension": "COLUMNS",
                            "startIndex": last_occupied_column_index,
                            "endIndex": last_occupied_column_index + 1
                        },
                        "properties": {
                            "pixelSize": 13
                        },
                        "fields": "pixelSize"

                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": MODULE_YEAR_MODULES_SHEET.id,
                            "dimension": "COLUMNS",
                            "startIndex": last_occupied_column_index + 1,
                            "endIndex": last_occupied_column_index + 2
                        },
                        "properties": {
                            "pixelSize": 100
                        },
                        "fields": "pixelSize"

                    }
                },
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": MODULE_YEAR_MODULES_SHEET.id,
                            "dimension": "COLUMNS",
                            "startIndex": last_occupied_column_index + 2,
                            "endIndex": last_occupied_column_index + 6
                        }

                    }
                }
            ]
        }
        SHEET.batch_update(column_sizing_body)

        MODULE_YEAR_MODULES_SHEET.update_cell(1,
                                              last_occupied_column_index + 2,
                                              self.title)

        MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
        module_year_module_titles_col_num = MODULE_PROPERTIES_WORKSHEET.find(f'Year {self.year} Module Titles').col
        next_empty_row_num = len(MODULE_PROPERTIES_WORKSHEET.col_values(module_year_module_titles_col_num)) + 1
        batch_update_range = f'{gspread.utils.rowcol_to_a1(next_empty_row_num, module_year_module_titles_col_num)}:{gspread.utils.rowcol_to_a1(next_empty_row_num, module_year_module_titles_col_num + 6)}'
        batch_update_values = [self.title, 'X' if self.activity else '',
                               'X' if self.availability['MSci Physics'] else '',
                               'X' if self.compulsory_status['MSci Physics'] else '',
                               'X' if self.availability['BSc Physics'] else '',
                               'X' if self.compulsory_status['BSc Physics'] else '',
                               self.module_credits]
        MODULE_PROPERTIES_WORKSHEET.batch_update([{'range': batch_update_range,
                                                   'values': [batch_update_values]}])
        MODULE_PROPERTIES_WORKSHEET.add_rows(1)

    def edit_module_properties(self):
        """
        Uses instance properties to update the properties of the module, represented by the instance, in the unigrade google sheet.
        """
        MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
        module_title_entry_cell = MODULE_PROPERTIES_WORKSHEET.find(f'{self.title}')
        module_properties_batch_update_range = f"{gspread.utils.rowcol_to_a1(module_title_entry_cell.row, module_title_entry_cell.col + 1)}:{gspread.utils.rowcol_to_a1(module_title_entry_cell.row, module_title_entry_cell.col + 6)}"
        module_properties_batch_update_values = ['X' if self.activity else '',
                                                 'X' if self.availability['MSci Physics'] else '',
                                                 'X' if self.compulsory_status['MSci Physics'] else '',
                                                 'X' if self.availability['BSc Physics'] else '',
                                                 'X' if self.compulsory_status['BSc Physics'] else '',
                                                 self.module_credits]
        MODULE_PROPERTIES_WORKSHEET.batch_update([{'range': module_properties_batch_update_range,
                                                   'values': [module_properties_batch_update_values]}])

    def generate_module_statistics(self):
        """
        Generates and prints summary statistics for the AcademicModule instance, for any or all of its cohort years.

        Retrieves all the relevant data for the module, if any exists, from the unigrade google sheet, and
        prompts the user to select to view data for a single year, or for all years that data exists. Then generates
        and prints to the terminal a set of summary statistics.
        """
        while True:
            MODULE_YEAR_MODULES_SHEET = SHEET.worksheet(f'year {self.year} modules')
            MODULE_TITLE_CELL_COL_NUM = MODULE_YEAR_MODULES_SHEET.find(f'{self.title}', in_row=1).col
            batch_get_range = f"{gspread.utils.rowcol_to_a1(3, MODULE_TITLE_CELL_COL_NUM + 1)}:{gspread.utils.rowcol_to_a1(3, MODULE_TITLE_CELL_COL_NUM  + 4 )[:-1]}"
            module_data = MODULE_YEAR_MODULES_SHEET.batch_get([batch_get_range])[0]
            module_data = [data_row for data_row in module_data if data_row != []]
            module_data = [data_row for data_row in module_data if data_row[1] == 'completed']
            cohort_years = set()
            print('')
            for data_row in module_data:
                cohort_years.add(data_row[0])
            if len(cohort_years) == 0:
                print('No data exists for this module yet.\n')
                return
            else:
                print('Data exists for the following cohort years:',
                      sorted(cohort_years))
                print('')
                print(f"""Enter the year you wish to view, for example {list(cohort_years)[0]};
or enter 'all' to view data for all the years combined.""")
                while True:
                    try:
                        user_input = input('->')
                        if user_input != 'all' and user_input not in cohort_years:
                            raise ValueError("Invalid input. Enter a year from the available cohort years, or enter 'all'.")
                    except ValueError as error:
                        print(f'{error}\n')
                    else:
                        if user_input != 'all':
                            module_mark_data = [float(data_row[2]) for data_row in module_data if data_row[0] == user_input]
                        else:
                            module_mark_data = [float(data_row[2]) for data_row in module_data]
                        dataset_size = len(module_mark_data)
                        module_mark_data_array = np.array(module_mark_data, float)
                        mean_mark = round(np.mean(module_mark_data_array), 1)
                        mark_std = round(np.std(module_mark_data_array), 1)
                        quartiles = np.percentile(module_mark_data_array, [25, 50, 75])
                        interquartile_range = round(quartiles[2] - quartiles[0], 1)
                        percentage_pass_or_better = round(100 * len([mark for mark in module_mark_data if mark >= 40.0])/dataset_size, 1)
                        percentage_lower_second_or_better = round(100 * len([mark for mark in module_mark_data if mark >= 50.0])/dataset_size, 1)
                        percentage_upper_second_or_better = round(100 * len([mark for mark in module_mark_data if mark >= 60.0])/dataset_size, 1)
                        percentage_first_or_better = round(100 * len([mark for mark in module_mark_data if mark >= 70.0])/dataset_size, 1)

                        print('')
                        print(f"'{self.title}' module statistics for {user_input} {'years:' if user_input == 'all' else ':'}\n".center(60))
                        print(f'Dataset size: {dataset_size}\n')
                        print(f'mean mark (%): {mean_mark}',
                              f'mark standard deviation (%): {mark_std}\n',
                              sep=' '.center(10))
                        print(f'median mark (%): {round(quartiles[1], 1)}',
                              f'interquartile range (%): {interquartile_range}\n',
                              sep=' '.center(10))
                        print(f'pass or better (%): {percentage_pass_or_better}',
                              f'2:2 or better (%): {percentage_lower_second_or_better}\n',
                              sep=' '.center(10))
                        print(f'2:1 or better (%): {percentage_upper_second_or_better}',
                              f'1st or better (%): {percentage_first_or_better}\n',
                              sep=' '.center(10))
                        if len(cohort_years) > 1:
                            print('''View statistics for another cohort year of this module? Enter 1 for yes,
enter 2 for no.''')
                            valid_input = False
                            while not valid_input:
                                valid_input = gen_functions.validate_numeric_input(2)
                            if valid_input == '2':
                                gen_functions.clear()
                                return
                            else:
                                break
                        else:
                            return
