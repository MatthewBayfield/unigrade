import sys
import os
import gspread
from google.oauth2.service_account import Credentials
from tabulate import tabulate
import datetime
student_dir = os.path.dirname(__file__)
general_functions_dir = os.path.join(student_dir, '..')
sys.path.insert(1, general_functions_dir)
import general_functions as gen_functions


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('unigrade-physics')

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
                self.student_id = STUDENT_DETAILS.cell(student_identifier_cell.row, student_identifier_cell.col -1).value
            else:
                self.student_name = STUDENT_DETAILS.cell(student_identifier_cell.row, student_identifier_cell.col +1).value
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
                                raise ValueError("""Invalid ID, please check you have entered the student's ID correctly:\n
                                it should contain 9 digits and nothing else.\n""")
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

                next_empty_row_number = len(used_ids_str) + 1
                STUDENT_DETAILS.update_cell(next_empty_row_number + 1, 2, self.student_name)
                STUDENT_DETAILS.update_cell(next_empty_row_number + 1, 1, self.student_id)
            else:
                return 'Student not registered.\n'

    def set_study_programme(self, assignment='edit',):
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

    def set_year(self, point, assignment='edit'):
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
                if point == 'start':
                    self.start_year = STUDENT_DETAILS.cell(student_name_cell.row, student_name_cell.col + 2).value
                else:
                    self.end_year = STUDENT_DETAILS.cell(student_name_cell.row, student_name_cell.col + 3).value

        else:
            correct = False
            while not correct:
                print(f"Enter a {point} year; for example 2022.\n")
                valid_input = False
                while not valid_input:
                    try:
                        user_input = input('->')
                        if not (user_input.isdigit() and len(user_input) == 4):
                            raise ValueError('Invalid input. Enter a valid year.\n')
                        elif point == 'end' and (int(user_input) - int(self.start_year))  not in (3, 4):
                            raise ValueError(f'Invalid input; the end year must be 3 or 4 years later than the start year.\nStudent start year: {self.start_year}.')
                    except ValueError as error:
                        print(f'{error}\n')                     
                    else:
                        valid_input = True
                if point == 'start':
                    self.start_year = user_input
                    print(f" start year: {self.start_year}")
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct = gen_functions.is_this_correct_checker(self.start_year, 'start year')
                else:
                    self.end_year = user_input
                    print(f"end year: {self.end_year}")
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct = gen_functions.is_this_correct_checker(self.end_year, 'end year')
            if point == 'start':
                STUDENT_DETAILS.update_cell(student_name_cell.row, student_name_cell.col + 2, self.start_year)
            else:
                STUDENT_DETAILS.update_cell(student_name_cell.row, student_name_cell.col + 3, self.end_year)
            print('year confirmed.\n')


class Student(StudentMixin):
    """
    Creates student objects, that have instance properties assigned using a combination of input parameters, and methods from
    the StudentMixin class. The student properties are those found in the student details worksheet of the unigrade-physics google sheet.
    A student object is used to hold the results of user inputs or database queries, during the process of updating the google sheet, and for displaying
    retrieved student information; the various instance methods exist for this purpose.
    """
    def __init__(self, identifier, identifier_type, register=False):
        result = self.set_student_identifiers(identifier, identifier_type, register)
        if result is not None:
            print(result)
        if result == 'Student is currently registered.\n':
            self.set_study_programme('initial')
            self.set_year('start', 'initial')
            self.set_year('end', 'initial')

    def register(self, identifier, identifier_type):
        """
        Adds the student, as well as the student's details, associated with the student object to the unigrade-physics
        google sheet: First sets the instance properties, then updates the google sheet;
        using methods from the StudentMixin class, along with user inputs.
        """
        print('starting the registration process:\n')
        self.set_student_identifiers(identifier, identifier_type, True)
        self.set_study_programme()
        self.set_year('start')
        self.set_year('end')
        print("Student registered:\n")
        self.retrieve_student_details()
        print('Enter any key to continue.')
        input('->')

    def unregister(self):
        """
        Deletes any rows in the unigrade-physics google sheet containing
        the student object's associated student_id instance property.
        """
        UNIGRADE_WORKSHEETS = SHEET.worksheets()
        for sheet in UNIGRADE_WORKSHEETS:
            student_id_cell = sheet.find(self.student_id)
            if student_id_cell is not None:
                sheet.delete_rows(student_id_cell.row)
        print('student successfully unregistered\n')
        print('Enter any key to continue.')
        input('->')
    
    def retrieve_student_details(self):
        """
        Retrieves the student details of a student from the unigrade google sheet. Prints the details as a table using
        the tabulate module.
        """
        STUDENT_DETAILS = SHEET.worksheet('student details')
        student_name_cell = STUDENT_DETAILS.find(self.student_name)
        registered_student_details = tabulate([STUDENT_DETAILS.row_values(1), STUDENT_DETAILS.row_values(student_name_cell.row)], headers='firstrow', tablefmt='grid')
        print(registered_student_details)

    def edit_student_details(self):
        """
        Prompts the user for input to select to edit the student's mutable details,
        or to go back. Performs the editing process using existing student class methods, that
        through user input first alter the instance properties, before then updating the google sheet.
        """
        valid_input = False
        print("Enter a number to edit student details, or to go back :\n")
        options = ["Alter the student's study programme, and their start and end year", 'go back']
        for i in range(0, 2, 1):
            print(f"{i+1}: {options[i]}")
        print('')
        while not valid_input:
            valid_input = gen_functions.validate_numeric_input(2)
        if valid_input == '2':
            return 'go_back'
        elif valid_input == '1':
            self.set_study_programme()
            self.set_year('start')
            self.set_year('end')
    
    def student_current_year(self):
        """
        Calulates, prints and returns the current academic year the student is in, using information
        from the unigrade google sheet, stored in the student class instance properties.
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
                print('Current academic year: yet to start.')
                return 'yet to start'
        
        print(f"Current academic year: {student_current_academic_year}.")
        return student_current_academic_year