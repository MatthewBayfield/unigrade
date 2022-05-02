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
                        ID_input = input('->')
                        if not (ID_input.isdigit() and len(ID_input) == 9):
                            print("""Invalid ID, please check you have entered the student's ID correctly:\n
                            it should contain 9 digits and nothing else.\n""")
                        elif ID_input in used_ids_str:
                            print("This ID belongs to an already registered student, please check you have entered the student's ID correctly.\n")
                        else:
                            valid_input = is_this_correct_checker(ID_input, 'Student ID:')
                    self.student_id = valid_input
                else:
                    self.student_id = identifier
                    print('''Now enter the student's full name separated by a comma;\nfor example: John,Smith.\n''')
                    valid_input = False
                    while not valid_input:
                        valid_input = validate_student_name_input()
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
            while not correct:
                print("For MSci Physics enter 1.\n")
                print("For BSc Physics enter 2.\n")
                user_options = {'1': 'MSci Physics', '2': 'BSc Physics'}
                valid_input = False
                while not valid_input:
                    valid_input = validate_numeric_input(2)
                self.study_programme = user_options[valid_input]
                print(f"{self.student_name} programme: {self.study_programme}")
                print('Is this correct? Enter 1 for yes, 2 for no.\n')
                correct = is_this_correct_checker(self.study_programme, 'programme')
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
                    user_input = input('->')
                    if not (user_input.isdigit() and len(user_input) == 4):
                        print('Invalid input.\n')
                    elif point == 'end' and (int(user_input) - int(self.start_year))  not in (3, 4):
                        print('Invalid input; the end year must be 3 or 4 years later than the start year.' )
                        print(f'student start year: {self.start_year}.')
                    else:
                        valid_input = True
                if point == 'start':
                    self.start_year = user_input
                    print(f" start year: {self.start_year}")
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct = is_this_correct_checker(self.start_year, 'start year')
                else:
                    self.end_year = user_input
                    print(f"end year: {self.end_year}")
                    print('Is this correct? Enter 1 for yes, 2 for no.\n')
                    correct = is_this_correct_checker(self.end_year, 'end year')
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
        if result == 'Student currently registered.\n':
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
        print("Student registered.\n")

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


def validate_numeric_input(number_of_options):
    '''
    Prompts user input. Tests whether the user input is in the valid range of integers, as determined by the number_of_options parameter.
    If it is not it raises an exception. Returns a boolean.
    '''
    try:
        user_selected_option = input("->")
        if user_selected_option in [f"{x}" for x in range(1, number_of_options + 1)]:
            return user_selected_option
        else:
            raise ValueError(f'Invalid input. Please enter an integer in the range 1-{number_of_options}.')
    except ValueError as error:
        print(f"{error}\n")
        return False


def is_this_correct_checker(user_input, user_input_description):
    """
    Called after a user input to prompt the user for further input to confirm whether they are happy with their input.
    Returns a boolean, or the user input value, which will also be used to evaluate to a boolean within the function
    in which this function is called.
    """
    while True:
        valid_input = validate_numeric_input(2)
        if valid_input:
            if valid_input == '1':
                return user_input
            else:
                print(f'Enter the correct {user_input_description}:\n')
                return False


def validate_student_name_input():
    """
    Prompts a user for input. Checks whether a 'student name' user input is valid. Returns a boolean, or the student name input, which will also
    be used to evaluate to a boolean within the function in which this function is called.
    """
    try:
        full_name = input('->')
        names = full_name.split(',')
        if full_name.count(',') != 1:
            raise ValueError('''Invalid input. Please enter a first, and last name separated with a comma;\nfor example: John,Paul,Smith.''')
        elif not (names[0].isalpha() and names[1].isalpha() and names[2].isalpha()):
            raise ValueError('Invalid input. Please use only standard alphabetic characters.')
        else:
            student_name = ""
            for name in names:
                student_name += name.capitalize()
                student_name += " "
            print(f"Student name: {student_name} ")
            print('is this correct? Enter 1 for yes, 2 for no.\n')
            return is_this_correct_checker(student_name, 'student name')
    except ValueError as error:
        print(f"{error}\n")
        return False
