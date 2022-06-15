import sys
import os
import gspread
from google.oauth2.service_account import Credentials
from tabulate import tabulate
import datetime
import time
from os import system
student_dir = os.path.dirname(__file__)
general_functions_dir = os.path.join(student_dir, '..')
sys.path.insert(1, general_functions_dir)
import general_functions as gen_functions
import decorated_gspread_methods
import classes.academic_module as academic_module
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


class StudentMixin(object):
    """
    A mixin class, that contains methods used by student class instances for the initialisation and updating of
    their properties, in the process of retrieving and displaying student information, and updating the unigrade-physics
    google sheet, for example during student registration.
    """
    def set_student_identifiers(self, identifier, identifier_type, register=False):
        """
        Searches the unigrade google sheet for a student using the identifier param; if the student exists, instance properties
         of the student class instance are assigned with the student google sheet properties. Also when the register param value
         is True, the user is prompted for input, to assign the instance properties, which are then used to update the
         google sheet.
        """
        STUDENT_DETAILS = SHEET.worksheet('student details')
        student_identifier_cell = STUDENT_DETAILS.find(identifier)
        if not isinstance(student_identifier_cell, type(None)):
            if identifier_type == 'name':
                self.student_name = identifier
                self.student_id = STUDENT_DETAILS.cell(student_identifier_cell.row, student_identifier_cell.col - 1).value
            else:
                self.student_name = STUDENT_DETAILS.cell(student_identifier_cell.row, student_identifier_cell.col + 1).value
                self.student_id = identifier
            return 'Student is currently registered.\n'
        else:
            if register:
                used_ids_str = set(STUDENT_DETAILS.col_values(1))
                used_ids_str.remove('Student ID')
                if identifier_type == 'name':
                    self.student_name = identifier
                    print('Now enter the 9 digit student ID of the student.\n')
                    valid_input = False
                    while not valid_input:
                        try:
                            ID_input = input('->')
                            if not (ID_input.isdigit() and len(ID_input) == 9):
                                raise ValueError("""Invalid ID, please check you have entered the student's ID correctly: it should contain 9 digits and nothing else.\n""")
                            elif ID_input in used_ids_str:
                                raise ValueError("This ID belongs to an already registered student, please check you have entered the student's ID correctly.\n")
                        except ValueError as error:
                            print(f"{error}\n")
                        else:
                            print(f"Student ID: {ID_input} ")
                            print('is this correct? Enter 1 for yes, 2 for no.\n')
                            valid_input = gen_functions.is_this_correct_checker(ID_input, 'Student ID:')
                    self.student_id = valid_input
                else:
                    self.student_id = identifier
                    print('''Now enter the student's full name separated by a comma;\nfor example: John,Smith.\n''')
                    valid_input = False
                    while not valid_input:
                        valid_input = gen_functions.validate_student_name_input()
                    self.student_name = valid_input

                next_empty_row_number = len(used_ids_str) + 2
                STUDENT_DETAILS.update_cell(next_empty_row_number, 2, self.student_name)
                UNIGRADE_WORKSHEETS = SHEET.worksheets()
                print('Adding student identifiers to the unigrade google sheet, please wait...')
                for sheet in UNIGRADE_WORKSHEETS:
                    if sheet.title != 'module properties':
                        sheet.add_rows(1)
                        gen_functions.update_sheet_borders(sheet, SHEET)
                        if sheet.id == 0:
                            sheet.update_cell(next_empty_row_number, 1, self.student_id)
                        else:
                            sheet.update_cell(next_empty_row_number + 1, 1, self.student_id)
                print('Student identifiers added.')
                time.sleep(1.5)
            else:
                return 'Student not registered.\n'

    def set_study_programme(self, assignment='edit', programme_change=False):
        """
        For an initial assignment param value, searches the unigrade google sheet for the student, and if they exist, assigns the
        study_programme instance property for a student class instance, using the corresponding google sheet student property.
        For an edit param value, prompts the user for input in order to assign the study_programme instance property, and update
        the google sheet.
        """
        STUDENT_DETAILS = SHEET.worksheet('student details')
        student_name_cell = STUDENT_DETAILS.find(self.student_name)
        if assignment == 'initial':
            if not isinstance(student_name_cell, type(None)):
                self.study_programme = STUDENT_DETAILS.cell(student_name_cell.row, student_name_cell.col + 1).value
        else:
            def execute_programme_change():
                correct = False
                print("Enter the student's study programme:\n")
                while not correct:
                    print("For MSci Physics enter 1.\n")
                    print("For BSc Physics enter 2.\n")
                    user_options = {'1': 'MSci Physics', '2': 'BSc Physics'}
                    valid_input = False
                    while not valid_input:
                        valid_input = gen_functions.validate_numeric_input(2)
                    self.study_programme = user_options[valid_input]
                    print(f"{self.student_name} study programme: {self.study_programme}")
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct = gen_functions.is_this_correct_checker(self.study_programme, 'study programme')
                    STUDENT_DETAILS.update_cell(student_name_cell.row, student_name_cell.col + 1, self.study_programme)
                print('study programme confirmed.\n')
            
            if not programme_change:
                execute_programme_change()
                return
            else:
                print('Student study programme:'.center(60))
                print('')
                student_current_academic_year = self.student_current_year()[0]
                if (isinstance(student_current_academic_year, int) and student_current_academic_year < 3) or student_current_academic_year == 'yet to start':
                    execute_programme_change()
                    self.set_year(programme_change=True)
                    return
                else:
                    print(f"student current academic year: {student_current_academic_year}.")
                    print("Too late to change the student's programme.")
                    print('Enter any key to continue.')
                    input('->')
                    print('')
                    return

    def set_year(self, programme_change=False, assignment='edit'):
        """
        For an initial assignment param value, searches the unigrade google sheet for the student, and if they exist, assigns the
        start_year or end_year instance property for a student class instance, using the corresponding google sheet student property.
        For an edit param value, prompts the user for input in order to assign the start_year or end_year instance property, and update
        the google sheet.
        """
        STUDENT_DETAILS = SHEET.worksheet('student details')
        student_name_cell = STUDENT_DETAILS.find(self.student_name)
        if assignment == 'initial':
            if not isinstance(student_name_cell, type(None)):
                self.start_year = STUDENT_DETAILS.cell(student_name_cell.row, student_name_cell.col + 2).value
                self.end_year = STUDENT_DETAILS.cell(student_name_cell.row, student_name_cell.col + 3).value

        else:
            if not programme_change:
                current_year = datetime.date.today().year
                academic_year_start_date_this_year = datetime.date(current_year, 9, 27)
                if self.start_year is None or (self.start_year is not None and self.student_current_year()[0] == 'yet to start'):
                    correct = False
                    while not correct:
                        print("Enter a start year; for example 2022.\n")
                        while True:
                            try:
                                user_input = input('->')
                                if not (user_input.isdigit() and len(user_input) == 4):
                                    raise ValueError('Invalid input. Enter a valid year.\n')
                                if datetime.date(int(user_input), 9, 27) < academic_year_start_date_this_year:
                                    raise ValueError('''Invalid input. The start date for the entered year has already past.
Please enter a valid year.''')
                            except ValueError as error:
                                print(f'{error}\n')                     
                            else:
                                break

                        self.start_year = user_input
                        print(f"start year: {self.start_year}")
                        print('Is this correct? Enter 1 for yes, 2 for no.\n')
                        correct = gen_functions.is_this_correct_checker(self.start_year, 'start year')
                    print('')
                    STUDENT_DETAILS.update_cell(student_name_cell.row, student_name_cell.col + 2, self.start_year)
                    print('start year confirmed.\n')
                    time.sleep(0.5)
                    print('Automatically setting student end year...')
                    time.sleep(1.5)
                    if self.study_programme == 'BSc Physics':
                        self.end_year = str(int(self.start_year) + 3)
                    else:
                        self.end_year = str(int(self.start_year) + 4)
                    STUDENT_DETAILS.update_cell(student_name_cell.row, student_name_cell.col + 3, self.end_year)
                    print(f'end year: {self.end_year}. Confirmed.')
                    time.sleep(1.5)
                else:
                    student_current_academic_year = self.student_current_year()[0]
                    print('Student start year:'.center(60))
                    print('')
                    print(f"student current academic year: {student_current_academic_year}.")
                    print("""Cannot edit the student's start year, as they have already
started their programme.""")
                    print('Enter any key to continue.')
                    input('->')
            else:
                if self.study_programme == 'BSc Physics':
                    self.end_year = str(int(self.start_year) + 3)
                else:
                    self.end_year = str(int(self.start_year) + 4)
                STUDENT_DETAILS.update_cell(student_name_cell.row, student_name_cell.col + 3, self.end_year)


class Student(StudentMixin):
    """
    Creates student objects, that have instance properties assigned using a combination of input parameters, and methods from
    the StudentMixin class. The student properties are those found in the student details worksheet of the unigrade-physics google sheet.
    A student object is used to hold the results of user inputs or database queries, during the process of updating the google sheet, and for displaying
    retrieved student information; the various instance methods exist for this purpose.
    """
    def __init__(self, identifier, identifier_type, register=False):
        self.student_name = None
        self.student_id = None
        self.study_programme = None
        self.start_year = None
        self.end_year = None
        self.enrolled_modules = None
        result = self.set_student_identifiers(identifier, identifier_type, register)
        if result is not None:
            print(result)
        if result == 'Student is currently registered.\n':
            self.set_study_programme('initial')
            self.set_year(assignment='initial')

    def register(self, identifier, identifier_type):
        """
        Registers the student instance in the unigrade google sheet.

        Adds the student's details to the google sheet, by first reassigning the instance properties, and
        then updating the google sheet using methods from the StudentMixin class, along with user inputs.

        Args:
            identifier_type (str): has value 'name' or 'ID'.
            identifier (str): equals the student's name or ID depending on the identifier_type value.
        """
        print('starting the registration process:\n')
        self.set_student_identifiers(identifier, identifier_type, True)
        print('')
        self.set_study_programme()
        self.set_year()
        print("Student registered:\n")
        self.retrieve_student_details()
        print('Enter any key to continue.')
        input('->')
        print('')
        self.compulsory_module_enrolment_checker_and_updater()

    def unregister(self):
        """
        Unregisters the student instance from the unigrade google sheet.

        Deletes any rows in the unigrade google sheet containing the student_id instance property value.
        """
        UNIGRADE_WORKSHEETS = SHEET.worksheets()
        for sheet in UNIGRADE_WORKSHEETS:
            if sheet.title != 'module properties':
                student_id_cell = sheet.find(self.student_id)
                if student_id_cell is not None:
                    sheet.delete_rows(student_id_cell.row)
        print('student successfully unregistered\n')
        print('Enter any key to continue.')
        input('->')
    
    def retrieve_student_details(self):
        """
        Retrieves the student details of a student from the unigrade google sheet. Prints the details as a table.
        """
        STUDENT_DETAILS = SHEET.worksheet('student details')
        student_name_cell = STUDENT_DETAILS.find(self.student_name)
        student_details_headings = STUDENT_DETAILS.row_values(1)
        formatted_student_details_headings = []
        for heading in student_details_headings:
            formatted_student_details_headings.append(heading.replace(' ', '\n'))
        student_details = STUDENT_DETAILS.row_values(student_name_cell.row)
        formatted_student_details = []
        for student_detail in student_details:
            formatted_student_details.append(student_detail.replace(' ', '\n'))
        registered_student_details = tabulate([formatted_student_details_headings, formatted_student_details], headers='firstrow', tablefmt='pretty',
                                              stralign='left', numalign='left')
        print(registered_student_details)

    def edit_student_details(self):
        """
        Allows the user to edit the student's mutable details, namely their start year, and study programme under certain conditions.
        
        Performs the editing process using existing student class methods, that through user input first alter the instance
        properties, before then updating the unigrade google sheet.
        """
        print('''A student's study programme and start date, can only be altered
under certain circustances:
1. If the student is not yet in year 3, they may change programme.
2. If the student's start year is still in the future, it may be
deferred.\n''')
        print('Enter any key to continue.')
        input('->')
        print('')
        self.set_study_programme(programme_change=True)
        self.set_year()
        print('Student details successfully updated.')
        time.sleep(2.5)
        gen_functions.clear()
    
    def student_current_year(self):
        """
        Calulates and returns the current academic year the student is in.

        Returns:
                A list of two items. The first an int corresponding to the calculated current student academic year;
                the second a str containing a description prior to the current student academic year.
        """
        current_date = datetime.date.today()
        current_year = datetime.date.today().year
        academic_year_start_date_this_year = datetime.date(current_year, 9, 27)
        academic_year_end_date_student_end_year = datetime.date(int(self.end_year), 6, 10)
        if current_date >= academic_year_end_date_student_end_year:
            student_current_academic_year = 'graduated'
        elif current_date >= academic_year_start_date_this_year:
            student_current_academic_year = (current_year - int(self.start_year)) + 1
        else:
            student_current_academic_year = current_year - int(self.start_year)
        
        if isinstance(student_current_academic_year, int):
            if student_current_academic_year < 1:
                student_current_academic_year = 'yet to start'
        
        return [student_current_academic_year, f"Current academic year: {student_current_academic_year}."]
    
    def retrieve_student_enrolled_module_info(self, year):
        """
        Retrieves information on the enrolled modules of a student for a chosen year, and generates two tables containing it.

        Retrieves data from the unigrade google sheet pertainig to the enrolled modules of a student instance, for a specified year.
        Uses the retrieved data to return a list, containing tables displaying all enrolled module titles
        and associated information for the student, as well as the list of module titles.

        Args:
            year (int): the academic year, to retrieve student enrolled module information for.

        Returns:
                A list, containing two tables containing the module information; and a list of the enrolled module titles for the
                student for this year.
        """
        UNIGRADE_WORKSHEETS = SHEET.worksheets()
        sheet = UNIGRADE_WORKSHEETS[year]

        student_entry_row = sheet.find(self.student_id).row
        # Finds all cells that contain 'X'
        crossed_cells = sheet.findall('X', in_row=student_entry_row)
        crossed_cells_col_index = [x.col for x in crossed_cells]

        module_titles_enrolled = [sheet.cell(1, index).value for index in crossed_cells_col_index]
        formatted_module_titles_enrolled = [title.replace(': ', ':\n') for title in module_titles_enrolled]
        module_info_cohort_year = [sheet.cell(student_entry_row, index + 1).value for index in crossed_cells_col_index]
        module_info_status = [sheet.cell(student_entry_row, index + 2).value for index in crossed_cells_col_index]
        formatted_module_info_status = [status.replace('yet ', 'yet\n') for status in module_info_status]
        module_info_mark = [sheet.cell(student_entry_row, index + 3).value for index in crossed_cells_col_index]
        module_info_grade = [sheet.cell(student_entry_row, index + 4).value for index in crossed_cells_col_index]
        first_table_module_info = list(zip(module_info_cohort_year, formatted_module_info_status))
        second_table_module_info = list(zip(module_info_mark, module_info_grade))

        first_table_content = dict(zip(formatted_module_titles_enrolled, first_table_module_info))
        second_table_content = dict(zip(formatted_module_titles_enrolled, second_table_module_info))
        module_numeric_labels = [label for label in range(1, len(module_titles_enrolled) + 1, 1)]
        first_table_headings = ['Module Title', 'Cohort\nYear', 'Module\nStatus']
        second_table_headings = ['Module Title', 'Mark\n(%)', 'Grade']
        first_table_data = [first_table_headings]
        second_table_data = [second_table_headings]
        label_index = 0
        for key, value in first_table_content.items():
            next_row = [module_numeric_labels[label_index], key, value[0], value[1]]
            first_table_data.append(next_row)
            label_index += 1
        modules_enrolled_info_first_table = tabulate(first_table_data, headers='firstrow', tablefmt='pretty', stralign='left', numalign='left')
        label_index = 0
        for key, value in second_table_content.items():
            next_row = [module_numeric_labels[label_index], key, value[0], value[1]]
            second_table_data.append(next_row)
            label_index += 1
        modules_enrolled_info_second_table = tabulate(second_table_data, headers='firstrow', tablefmt='pretty', stralign='left', numalign='left')

        return [modules_enrolled_info_first_table, modules_enrolled_info_second_table, module_titles_enrolled]
    
    def edit_student_module_info(self, print_info_function, load_and_prepare_module_info_function):
        """
        Allows the user to select to modify the module status and mark for a chosen module for which the student is enrolled.

        First reprints the student's enrolled module information tables; then provides prompts to choose a module and then
        alter the module status and mark, before updating the unigrade google sheet. To be called on a Student instance within
        the view_or_edit_student_module_info_and_grades_interface func of run.py.

        Args:
            print_info_function: The 'print_info' inner function of the 'view_or_edit_student_module_info_and_grades_interface'
                                 func. Prints the student module information tables.
            load_and_prepare_module_info_function: The 'load_and_prepare_module_info' inner function of the
                                                   'view_or_edit_student_module_info_and_grades_interface func'. Generates
                                                   the tables printed by the print_info func.
        
        Returns:
                Returns a str that if set equal to the global next_function_call variable of run.py,
                determines which interface the user sees next.
        
        Raises:
                ValueError: If the student mark input does not contain only numbers, or the number entered is not given to 1dp.
        """
        while True:
            gen_functions.clear()
            print('Reprinting student module info...')
            print('')
            time.sleep(3)
            print_info_function()
            print('')
            print("""Inspect the above tables, then enter a number corresponding
to one of the following options:\n""")
            correct_year_chosen = False
            while not correct_year_chosen:
                option_index = 1
                years_with_enrolled_modules = []
                for key in self.enrolled_modules.keys():
                    if len(self.enrolled_modules[key]) != 0:
                        print(f'{option_index}. modfiy a {key} module')
                        option_index += 1
                        years_with_enrolled_modules.append(key)
                print(f'{option_index}. go back')
                print('')
                chosen_year = False
                while not chosen_year:
                    chosen_year = gen_functions.validate_numeric_input(option_index)
                if int(chosen_year) != option_index:
                    print(f"'modify a {years_with_enrolled_modules[int(chosen_year) - 1]} module' selected.")
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct_year_chosen = gen_functions.is_this_correct_checker(chosen_year, 'number corresponding to one of the following options')
                else:
                    return 'view_or_edit_student_module_info_and_grades_interface'

            print('')
            print(f"""Enter the numeric label corresponding to the module title in the
{years_with_enrolled_modules[int(chosen_year) - 1]} modules tables, for the module you wish to edit for the student:\n""")
            correct_module_chosen = False
            while not correct_module_chosen:
                chosen_module = False
                while not chosen_module:
                    chosen_module = gen_functions.validate_numeric_input(len(self.enrolled_modules[years_with_enrolled_modules[int(chosen_year) - 1]]))
                print(f"'{self.enrolled_modules[years_with_enrolled_modules[int(chosen_year) - 1]][int(chosen_module) - 1]}' module selected.")
                print('Is this correct? Enter 1 for yes, 2 for no.\n')
                correct_module_chosen = gen_functions.is_this_correct_checker(chosen_module, 'label corresponding to the relevant module title')
            
            chosen_module_worksheet = SHEET.worksheet(f'{years_with_enrolled_modules[int(chosen_year) - 1]} modules')
            chosen_module_title_col = chosen_module_worksheet.find(self.enrolled_modules[years_with_enrolled_modules[int(chosen_year) - 1]][int(chosen_module) - 1], 1).col
            student_entry_row = chosen_module_worksheet.find(self.student_id).row
            student_module_info_cell_reference_range = f'{gspread.utils.rowcol_to_a1(student_entry_row, chosen_module_title_col + 1)}:{gspread.utils.rowcol_to_a1(student_entry_row, chosen_module_title_col + 4)}'
            student_module_info = chosen_module_worksheet.batch_get([student_module_info_cell_reference_range])
            table_headings = ['Cohort\nyear', 'Module\nstatus', 'Mark\n(%)', 'Grade']
            student_module_info_table = tabulate([table_headings, student_module_info[0][0]], headers='firstrow', tablefmt='pretty', stralign='left', numalign='left')
            gen_functions.clear()
            print('Student module information:')
            print(student_module_info_table)
            print('')
            cohort_year = (int(self.start_year) + int(years_with_enrolled_modules[int(chosen_year) - 1][-1])) - 1
                
            print('Enter the number corresponding to the current module status for the student:\n')
            module_status_options = ['not yet completed', 'completed']
            for option_index in range(1, 3, 1):
                print(f'{option_index}. {module_status_options[option_index - 1]}')
            print('')
            correct_status = False
            while not correct_status:
                    chosen_status = False
                    while not chosen_status:
                        chosen_status = gen_functions.validate_numeric_input(2)
                    print(f'Module status: {module_status_options[int(chosen_status) - 1]}')
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct_status = gen_functions.is_this_correct_checker(chosen_status, 'number corresponding to the correct module status')

            print('')
            if module_status_options[int(chosen_status) - 1] == 'completed':
                print('''Enter the percentage mark for the student in this module,
as a number between 0-100 to 1dp, for example 56.5.''')
                correct_mark = False
                while not correct_mark:
                    valid_mark = False
                    while not valid_mark:
                            try:
                                valid_mark = input('->')
                                if (valid_mark.count('.') != 1):
                                    raise ValueError('Invalid input: the mark must be given to 1dp, for example 78.8')
                                components = valid_mark.split('.')
                                if not ((1 <= len(components[0]) <= 2) and len(components[1]) == 1):
                                    raise ValueError('Invalid input: Enter a number between 0-100 to 1dp, for example 56.5\n')
                                if not (components[0].isdigit() and components[1].isdigit()):
                                    raise ValueError('Invalid input: Enter a number between 0-100 to 1dp, for example 56.5\n')
                            except ValueError as error:
                                print(f'{error}\n')
                                valid_mark = False                     
                            
                            else:
                                print(f"Mark (%): {valid_mark}")
                                print('Is this correct? Enter 1 for yes, 2 for no.\n')
                                correct_mark = gen_functions.is_this_correct_checker(valid_mark, 'mark')
                valid_mark = float(valid_mark)
                if valid_mark >= 70.0:
                    valid_grade = '1st'
                elif valid_mark >= 60.0:
                    valid_grade = '2:1'
                elif valid_mark >= 50.0:
                    valid_grade = '2:2'
                elif valid_mark >= 40.0:
                    valid_grade = '3rd'
                else:
                    valid_grade = 'fail' 
                
            else:
                valid_mark = '-'
                valid_grade = '-'

            chosen_module_worksheet.batch_update([{'range': student_module_info_cell_reference_range, 'values': [[cohort_year, module_status_options[int(chosen_status) - 1],
                                                                                                                  valid_mark, valid_grade]]}])
            print('Student module information updated.\n')
            student_module_info = chosen_module_worksheet.batch_get([student_module_info_cell_reference_range])
            student_module_info_table = tabulate([table_headings, student_module_info[0][0]], headers='firstrow', tablefmt='pretty', stralign='left', numalign='left')
            print(student_module_info_table)
            print('')
            print('''To modify the status and mark of another module for the same student, enter 1;
or to go back enter 2.''')
            valid_input = False
            while not valid_input:
                valid_input = gen_functions.validate_numeric_input(2)
            if valid_input == '2':
                return 'student_information_top_level_interface'
            else:
                module_info = {}
                modules_enrolled ={}
                load_and_prepare_module_info_function()
        
    def unenrol_student_from_module(self):
        """
        Prompts the user to select an optional module for the student's current academic year, to unenrol the student from.

        First prints tables displaying the student's enrolled optional modules for their current academic year, and that they have
        yet to complete. Once a module is chosen the necessary updates to the unigrade google sheet are performed,
        namely clearing the data cells for this module for this student. User also has the option to switch to enrolling.

        Returns:
                One of several strings, that if set equal to the global next_function_call variable of run.py,
                determines which interface the user sees next.
        """
        student_academic_year = self.student_current_year()[0]
        gen_functions.clear()
        print('Student module unenrolment:\n')
        print('''You can unenrol a student from any optional module on their current
academic year, for which they have yet to complete. This unenrolment
should accompany enrolling a student on another available optional module,
normally within the first month that the module commenced.\n''')
        print('Enter any key to continune.')
        input('->')
        print('')
        print(f"{self.student_current_year()[1]}\n")
        time.sleep(1)

        if student_academic_year in [1,2,3,4]:
            repeat = True
            while repeat:
                this_year_modules_worksheet = SHEET.worksheet(f'year {student_academic_year} modules')
                active_and_compulsory_modules_this_year = academic_module.AcademicModule.retrieve_active_and_compulsory_year_x_modules(student_academic_year, self.study_programme)
                student_currently_enrolled_modules_this_year = self.enrolled_modules[f'year {student_academic_year}']
                student_current_enrolled_optional_modules_this_year = [module for module in student_currently_enrolled_modules_this_year 
                                                                       if (module not in active_and_compulsory_modules_this_year)]
                student_entry_row = this_year_modules_worksheet.find(self.student_id).row
                student_not_completed_enrolled_optional_modules_this_year = []
                for module in student_current_enrolled_optional_modules_this_year:
                    module_status = this_year_modules_worksheet.get(gspread.utils.rowcol_to_a1(student_entry_row, this_year_modules_worksheet.find(module, in_row=1).col + 2))[0][0]
                    if module_status != 'completed':
                        student_not_completed_enrolled_optional_modules_this_year.append(module)
                
                formatted_student_not_completed_enrolled_optional_modules_this_year = [title.replace(': ', ':\n') 
                                                                                       for title in student_not_completed_enrolled_optional_modules_this_year]
                table_headings = [' ', 'Module title']
                table_data = [[label, module_title] for label, module_title in enumerate(formatted_student_not_completed_enrolled_optional_modules_this_year, 1)]
                table_data.insert(0, table_headings)
                labelled_not_completed_enrolled_optional_modules_table = tabulate(table_data, headers='firstrow', tablefmt='pretty', stralign='left', numalign='left')
                print("""Student's currently enrolled and not completed optional modules,
for their current academic year:""")
                time.sleep(1)
                print(labelled_not_completed_enrolled_optional_modules_table)
                time.sleep(2)
                print('')

                if len(student_not_completed_enrolled_optional_modules_this_year) == 0:
                    print('Student is not currently enrolled on any not yet completed optional modules\n')
                    print('Enter a number corresponding to one of the following options:\n')
                    print('1. Enrol the student on an optional module.')
                    print('2. go back')
                    valid_input = False
                    while not valid_input:
                        valid_input = gen_functions.validate_numeric_input(2)
                    if valid_input == '1':
                        returned_next_function_string = self.enrol_student_on_module()
                        return returned_next_function_string
                    else:
                        return 'view_or_edit_student_module_info_and_grades_interface'

                print(f"""Enter the numeric label corresponding to the module title of the module
you wish to unenrol the student from;""")
                print(f'or enter {len(student_not_completed_enrolled_optional_modules_this_year) + 1} to go back.')
                correct_module_chosen = False
                while not correct_module_chosen:
                    chosen_module = False
                    while not chosen_module:
                        chosen_module = gen_functions.validate_numeric_input(len(student_not_completed_enrolled_optional_modules_this_year) + 1)
                    if int(chosen_module) == len(student_not_completed_enrolled_optional_modules_this_year) + 1:
                                    return 'view_or_edit_student_module_info_and_grades_interface'
                    print(f"'Module {student_not_completed_enrolled_optional_modules_this_year[int(chosen_module) - 1]}' selected.")
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct_module_chosen = gen_functions.is_this_correct_checker(chosen_module,
                    f'number corresponding to one of the modules, or the number {len(student_not_completed_enrolled_optional_modules_this_year) + 1} to go back.')
                
                module_info_cell_range_start_col = this_year_modules_worksheet.find(student_not_completed_enrolled_optional_modules_this_year[int(chosen_module) - 1],
                                                                                    in_row=1).col
                module_info_cell_range_start_address = gspread.utils.rowcol_to_a1(student_entry_row, module_info_cell_range_start_col)
                module_info_cell_range_end_address = gspread.utils.rowcol_to_a1(student_entry_row, module_info_cell_range_start_col + 4)
                this_year_modules_worksheet.batch_clear([f'{module_info_cell_range_start_address}:{module_info_cell_range_end_address}'])
                self.enrolled_modules[f'year {student_academic_year}'].remove(student_not_completed_enrolled_optional_modules_this_year[int(chosen_module) - 1])
                
                print(f"Student successfully unenrolled from the module: '{student_not_completed_enrolled_optional_modules_this_year[int(chosen_module) - 1]}'.\n")
                print('Enter a number corresponding to one of the following options:\n')
                print('1. Unenrol the student from another optional module.')
                print('2. Enrol the student on another optional module.')
                print('3. go back')
                valid_input = False
                while not valid_input:
                    valid_input = gen_functions.validate_numeric_input(3)
                if valid_input == '3':
                    return 'view_or_edit_student_module_info_and_grades_interface'
                elif valid_input == '2':
                    returned_next_function_string = self.enrol_student_on_module()
                    return returned_next_function_string

        else:
            print(f"Cannot unenrol the student from any modules, as the student has {student_academic_year}.")
            print('Enter any key to continue.')
            input('->')
            return 'student_information_top_level_interface'    
    
    def enrol_student_on_module(self, auto=False):
        """
        Performs the enrolment of a student automatically on a set of compulsory modules, or a user selected optional module.

        When the auto parameter is True: enrols the student (in the unigrade google sheet) on all active and compulsory
        modules for their current academic year. When the auto parameter is False: prompts the user to select to enrol
        the student instance on one of the optional modules for the student's current academic year, provided they have
        not exceeded their module credit allowance. The method must be called within the
        view_or_edit_student_module_info_and_grades_interface function, or within the unenrol_student_from_module method,
        if the auto parameter is False.

        Args:
            auto (bool): Determines whether the student is automatically enrolled on compulsory modules, or enrolled
            on a user selected optional module; with all modules belonging to the student's current academic year.
        
        Returns:
                One of several strings, that if set equal to the global next_function_call variable of run.py,
                determines which interface the user sees next.
        """
        student_academic_year = self.student_current_year()[0]
        if student_academic_year in [1,2,3,4]:
        
            active_and_compulsory_modules_this_year = academic_module.AcademicModule.retrieve_active_and_compulsory_year_x_modules(student_academic_year, self.study_programme)
            this_year_modules_worksheet = SHEET.worksheet(f'year {student_academic_year} modules')
            student_entry_row = this_year_modules_worksheet.find(self.student_id).row

            if auto:
                for module in active_and_compulsory_modules_this_year:
                    module_cell_col_num = this_year_modules_worksheet.find(module, in_row=1).col
                    batch_update_range = f'{gspread.utils.rowcol_to_a1(student_entry_row, module_cell_col_num)}:{gspread.utils.rowcol_to_a1(student_entry_row, module_cell_col_num + 4)}'
                    batch_update_values = ['X', int(self.start_year) + student_academic_year - 1, 'not yet completed', '-', '-']
                    this_year_modules_worksheet.batch_update([{'range': batch_update_range, 'values': [batch_update_values]}])
                
            else:
                gen_functions.clear()
                print('Student enrolment:\n')
                print(f"""Please note enrolment on optional modules in the unigrade system can only
be performed for modules on the student's current academic year, which
updates at the beginning of each new academic year; the next year
starting on {datetime.date(datetime.date.today().year, 9, 27)}.\n""")
                print('Enter any key to continue.')
                input('->')
                repeat = True
                while repeat:
                    gen_functions.clear()
                    module_properties_worksheet = SHEET.worksheet('module properties')
                    active_modules_this_year = academic_module.AcademicModule.retrieve_active_year_x_modules(student_academic_year, self.study_programme)
                    student_currently_enrolled_modules_this_year = self.enrolled_modules[f'year {student_academic_year}']
                    credit_allowance_optional_modules_col = module_properties_worksheet.find(f'Year {student_academic_year} {self.study_programme} Optional Module Credits Available').col
                    credit_allowance_optional_modules = int(module_properties_worksheet.get(gspread.utils.rowcol_to_a1(2, credit_allowance_optional_modules_col))[0][0])
                    student_current_enrolled_optional_modules_this_year = [module for module in student_currently_enrolled_modules_this_year 
                                                                           if (module not in active_and_compulsory_modules_this_year)]
                    module_credits_dict = academic_module.AcademicModule.retrieve_year_x_module_credits(student_academic_year)
                    
                    student_optional_module_credit_sum = 0
                    for module in student_current_enrolled_optional_modules_this_year:
                        student_optional_module_credit_sum += module_credits_dict[module]
                    available_credits = credit_allowance_optional_modules - student_optional_module_credit_sum
                    print(f'Optional module credits still available for the student: {available_credits}.\n')
                    time.sleep(2)

                    if available_credits > 0:
                        optional_modules_this_year = [module for module in active_modules_this_year if module not in active_and_compulsory_modules_this_year]
                        available_optional_modules_this_year = {key: value for key, value in module_credits_dict.items()
                        if (value <= available_credits and key in optional_modules_this_year and key not in student_current_enrolled_optional_modules_this_year)}
                        formatted_available_optional_modules_this_year = {key.replace(': ', ':\n'): value for key, value in available_optional_modules_this_year.items()}
                        table_data = [[label, module_title, credits] for label, (module_title, credits) in enumerate(formatted_available_optional_modules_this_year.items(), 1)]
                        table_headings = [' ', 'Module Title', 'Credits']
                        table_data.insert(0, table_headings)
                        available_optional_modules_table = tabulate(table_data, headers='firstrow', tablefmt='pretty', stralign='left', numalign='left')
                        print('Remaining available optional modules for the student:')
                        time.sleep(2)
                        print(available_optional_modules_table)
                        time.sleep(2)
                        print('''Enter a number from the table corresponding to the module you wish
to enrol the student on;''')
                        print(f'or enter {len(available_optional_modules_this_year) + 1} to go back.')

                        correct_module = False
                        while not correct_module:
                            valid_input = False
                            while not valid_input:
                                valid_input = gen_functions.validate_numeric_input(len(available_optional_modules_this_year) + 1)
                            if int(valid_input) == len(available_optional_modules_this_year) + 1:
                                return 'view_or_edit_student_module_info_and_grades_interface'
                            print(f"'Module {list(available_optional_modules_this_year.keys())[int(valid_input) - 1]}' selected.")
                            print('Is this correct? Enter 1 for yes, 2 for no.\n')
                            correct_module = gen_functions.is_this_correct_checker(valid_input, 'number corresponding to a module to enrol the student on')

                        module_cell_col_num = this_year_modules_worksheet.find(list(available_optional_modules_this_year.keys())[int(valid_input) - 1], in_row=1).col
                        batch_update_range = f'{gspread.utils.rowcol_to_a1(student_entry_row, module_cell_col_num)}:{gspread.utils.rowcol_to_a1(student_entry_row, module_cell_col_num + 4)}'
                        batch_update_values = ['X', (int(self.start_year) + student_academic_year) - 1, 'not yet completed', '-', '-']
                        this_year_modules_worksheet.batch_update([{'range': batch_update_range, 'values': [batch_update_values]}])
                        self.enrolled_modules[f'year {student_academic_year}'].append(list(available_optional_modules_this_year.keys())[int(valid_input) - 1])
                        print(f"Student successfully enrolled on '{list(available_optional_modules_this_year.keys())[int(valid_input) - 1]}.'\n" )
                        print('Enter a number corresponding to one of the following options:\n')
                        print('1. Enrol the student on another optional module.')
                        print('2. Unenrol the student from an optional module.')
                        print('3. go back.')
                        valid_entry = False
                        while not valid_entry:
                            valid_entry = gen_functions.validate_numeric_input(3)
                        if valid_entry == '2':
                            returned_next_function_string = self.unenrol_student_from_module()
                            return returned_next_function_string
                        elif valid_entry == '3':
                            return 'view_or_edit_student_module_info_and_grades_interface'

                    else:
                        print('''Student is already enrolled on the correct number of optional modules
for this year and this programme.\n''')
                        print('Enter a number corresponding to one of the following options:\n')
                        print('1. Unenrol the student from an optional module.')
                        print('2. go back.')
                        valid_entry = False
                        while not valid_entry:
                            valid_entry = gen_functions.validate_numeric_input(2)
                        if valid_entry == '1':
                            returned_next_function_string = self.unenrol_student_from_module()
                            return returned_next_function_string
                        return 'view_or_edit_student_module_info_and_grades_interface'
        else:
            if auto == False:
                gen_functions.clear()
                print('Student enrolment:\n')
                if student_academic_year == 'yet to start':
                    print(f"""Please note enrolment on optional modules in the unigrade system can only
be performed for modules on the student's current academic year, which
updates at the beginning of each new academic year; the next year
starting on {datetime.date(datetime.date.today().year, 9, 27)}.\n""")
                    print('Enter any key to continue.')
                    input('->')
                    print('')
                print(f'Cannot enrol the student on any modules, as the student has {student_academic_year}.')
                print('Enter any key to continue.')
                input('->')
            return 'student_information_top_level_interface'    

    def compulsory_module_enrolment_checker_and_updater(self):
        """
        Checks whether the student instance is enrolled on all active compulsory modules. Performs enrolment if necessary.
        
        Checks the enrolement status of the active compulsory modules for their current academic year and programme, in the unigrade
        google sheet. Then enrols the student on any active compulsory modules that they are not yet enrolled on.
        """
        print('''Checking and updating the enrolment status of the compulsory modules
for the student's current academic year.
Please wait...''')
        print('')
        time.sleep(2)
        if self.student_current_year()[0] in [1,2,3,4]:
            current_year_enrolled_modules = self.retrieve_student_enrolled_module_info(self.student_current_year()[0])[2]
            if len(current_year_enrolled_modules) == 0:
                self.enrol_student_on_module(True)
        print('''Student is now enrolled on all the required compulsory modules for their
current academic year.''')
        print('Enter any key to continue.')
        input('->')
