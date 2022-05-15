from os import system
import gspread
from google.oauth2.service_account import Credentials
import sys
import time
import modules.classes.student as student
import modules.general_functions as gen_functions
import modules.decorated_gspread_methods

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
    print('''ERROR ENCOUNTERED: There seems to be a problem accessing the unigrade google sheet. The unigrade program will now terminate.
Please try running the program again. If the error persists try again later.\n''')
    print('Enter any key to initiate exiting the unigrade program.')
    input('->')
    system('clear')
    print('Quitting the unigrade program...')
    time.sleep(3.0)
    system('clear')
    sys.exit()


def top_level_interface():
    """
    Displays the top-level interface, after clearing the console.
    The user is prompted to choose one of two options: either view module information, or view and or edit/add student information.
    """
    system('clear')
    print("""
         _    _  _   _  _____  _____  _____             _____   ______ 
        | |  | || \ | ||_   _|/ ____||  __ \     /\    |  __ \ |  ____|
        | |  | ||  \| |  | | | |  __ | |__) |   /  \   | |  | || |__   
        | |  | || . ` |  | | | | |_ ||  _  /   / /\ \  | |  | ||  __|  
        | |__| || |\  | _| |_| |__| || | \ \  / ____ \ | |__| || |____ 
         \____/ |_| \_||_____|\_____||_|  \_\/_/    \_\|_____/ |______|
    \n""")
    next_function([['1', 'modules_interface'], ['2', 'student_information_top_level_interface'], ['3', 'exit_the_program']])


def student_information_top_level_interface():
    """
    Displays the top-level student information terminal interface to the user.
    Prompts the user to select to alter student registration, or to view/edit existing student information,
    as well as 'return to the top program interface' or 'exit' the program.
    """
    system('clear')
    print("""
                      ___  _             _            _   
                     / __|| |_  _  _  __| | ___  _ _ | |_ 
                     \__ \|  _|| || |/ _` |/ -_)| ' \|  _|
                     |___/ \__| \_,_|\__,_|\___||_||_|\__|
                                                          
            ___         __                         _    _            
           |_ _| _ _   / _| ___  _ _  _ __   __ _ | |_ (_) ___  _ _  
            | | | ' \ |  _|/ _ \| '_|| '  \ / _` ||  _|| |/ _ \| ' \ 
           |___||_||_||_|  \___/|_|  |_|_|_|\__,_| \__||_|\___/|_||_|
                                                                             
    \n""")
    global last_function_call
    last_function_call = 'student_information_top_level_interface'
    next_function([['1', 'view_or_edit_student_details_interface'], ['2', 'student_registration_interface'], ['3', 'top_level_interface'], ['4', 'exit_the_program']])


def register_student(registration_status, new_student_object, valid_entry, user_options, user_options_index):
    """
    Registers a student in the unigrade google sheet, by invoking the student class methods,
    on the new_student_object param. Should only be called within the
    student_registration_interface function.
    """
    if registration_status != 'Student is currently registered.\n':
        new_student_object.register(valid_entry, user_options[user_options_index])
        global next_function_call
        next_function_call = 'student_registration_interface'
    else:
        print('Student is currently registered.\n')
        next_function([['1', 'unregister_student'], ['2', 'go_back']])


def unregister_student(registration_status, new_student_object, valid_entry, user_options, user_options_index):
    """
    Unregisters a student in the unigrade google sheet, by invoking the student class methods,
    on the new_student_object param. Should only be called within the
    student_registration_interface function; unused params allow the function to be called within this function .
    """
    if registration_status == 'Student is currently registered.\n':
        new_student_object.unregister()
        global next_function_call
        next_function_call = 'student_registration_interface'
    else:
        print('Student is already not registered.\n')
        next_function([['1', 'register_student'], ['2', 'go_back']])


def student_registration_interface():
    """
    Displays the student registration interface to the user. Prompts the user to input a student's name or ID, then
    confirms whether the student is currently registered in the unigrade google sheet, before allowing the user to register or unregister a
    student by perfoming the registration process.
    """
    system('clear')
    print('Student Registration:', '\n')
    print('Do you want to continue? 1 for yes, 2 for no',)
    valid_input = False
    while not valid_input:
        valid_input = gen_functions.validate_numeric_input(2)
    
    if valid_input == '2':
        next_function([['1', 'go_back'],['2', 'top_level_interface'], ['3', 'exit_the_program']])
    else:
        valid_entry, user_options, user_options_index, new_student_object = registration_status_checker()
        next_function([['1', 'register_student'], ['2', 'unregister_student'], ['3', 'top_level_interface'], ['4', 'exit_the_program']])
        
        while next_function_call in ('register_student', 'unregister_student'):
            registration_status = new_student_object.set_student_identifiers(valid_entry, user_options[user_options_index])
            if next_function_call in ('register_student', 'unregister_student'):
                FUNCTION_DICTIONARY[next_function_call](registration_status, new_student_object, valid_entry, user_options, user_options_index)
      

def registration_status_checker():
    """
    Checks whether a student identified by their student ID or student name, provided by user input,
    is registered in the unigrade google sheet. Prints to the terminal the result.
    Returns the valid input value and its identifier type, and the new student object.
    """
    print("To enter the student's name, enter 1; or 2 for their student ID.\n")
    user_options = {'1': 'name', '2': 'ID'}
    valid_input = False
    while not valid_input:
        valid_input = gen_functions.validate_numeric_input(2)

    if valid_input == '1':
        print('''Enter the  student's full name separated by a comma;\nfor example: John,Smith.\n''')
        valid_entry = False
        while not valid_entry:
            valid_entry = gen_functions.validate_student_name_input()
        user_options_index = '1'
    else:
        print('Enter the 9 digit student ID of the student.\n')
        valid_entry = False
        while not valid_entry:
            try:
                ID_input = input('->')
                if not (ID_input.isdigit() and len(ID_input) == 9):
                    raise ValueError("""Invalid ID, please check you have entered the student's ID correctly: it should contain 9 digits and nothing else.\n""")
            except ValueError as error:
                print(f"{error}\n")
            else:
                print(f"Student ID: {ID_input} ")
                print('is this correct? Enter 1 for yes, 2 for no.\n')
                valid_entry = gen_functions.is_this_correct_checker(ID_input, 'Student ID:')
                user_options_index = '2'

    new_student_object = student.Student(valid_entry, user_options[user_options_index])
    return [valid_entry, user_options, user_options_index, new_student_object]


def view_or_edit_student_details_interface():
    """
    Prompts the user to input a student's name or ID, which is searched for within the unigrade google sheet.
    If the student is not registered, the user is given the option of registering the student. If the student
    is registered, their details are displayed in a table printed to the terminal. The user is then able to edit
    the mutable details if they desire, which are then updated in the unigrade google sheet.
    """
    system('clear')
    print('Student Details:', '\n')
    print('Do you want to continue? 1 for yes, 2 for no',)
    valid_input = False
    while not valid_input:
        valid_input = gen_functions.validate_numeric_input(2)
    if valid_input == '2':
        next_function([['1', 'go_back'],['2', 'top_level_interface'], ['3', 'exit_the_program']])
    else:
        global next_function_call
        input_student_identifier, identifier_types_list, input_identifier_type_index, new_student_object = registration_status_checker()
        registration_status = new_student_object.set_student_identifiers(input_student_identifier, identifier_types_list[input_identifier_type_index])
        if registration_status == 'Student not registered.\n':
            next_function([['1', 'register_student'], ['2', 'go_back']])
            global next_function_call
            if next_function_call == 'register_student':
                FUNCTION_DICTIONARY[next_function_call](registration_status, new_student_object, input_student_identifier, identifier_types_list, input_identifier_type_index)

        else:
            while True:
                new_student_object.retrieve_student_details()
                returned_next_function_call = new_student_object.edit_student_details()
                if returned_next_function_call == 'go_back':
                    next_function_call = 'go_back'
                    break


def modules_interface():
    """
    Displays the modules terminal interface to the user.
    Prompts the user to select to view a list of year 1, year 2, year 3, or year 4 module titles; or 'go back' or 'exit' the program.
    """
    system('clear')
    print("""
                      __  __          _        _          
                     |  \/  | ___  __| | _  _ | | ___  ___
                     | |\/| |/ _ \/ _` || || || |/ -_)(_-<
                     |_|  |_|\___/\__,_| \_,_||_|\___|/__/
                                                          
            ___         __                         _    _            
           |_ _| _ _   / _| ___  _ _  _ __   __ _ | |_ (_) ___  _ _  
            | | | ' \ |  _|/ _ \| '_|| '  \ / _` ||  _|| |/ _ \| ' \ 
           |___||_||_||_|  \___/|_|  |_|_|_|\__,_| \__||_|\___/|_||_|
    \n""")
    print('''To view a list of year 1, year 2, year 3, or year 4 module titles;\nenter 1,2,3, or 4 respectively.\n''')
    print('''To go back a step, return to the initial interface,\nor exit the program; enter 5,6 and 7 respectively.\n''')
    valid_input = False
    while (not valid_input):
        valid_input = gen_functions.validate_numeric_input(7)


def view_or_edit_student_module_info_and_grades():
    """
    """
    system('clear')
    print('Student module information and grades:', '\n')
    print('Do you want to continue? 1 for yes, 2 for no',)
    valid_input = False
    while not valid_input:
        valid_input = gen_functions.validate_numeric_input(2)
    if valid_input == '2':
        next_function([['1', 'go_back'],['2', 'top_level_interface'], ['3', 'exit_the_program']])
    else:
        global next_function_call
        input_student_identifier, identifier_types_list, input_identifier_type_index, new_student_object = registration_status_checker()
        registration_status = new_student_object.set_student_identifiers(input_student_identifier, identifier_types_list[input_identifier_type_index])
        if registration_status == 'Student not registered.\n':
            next_function([['1', 'register_student'], ['2', 'go_back']])
            global next_function_call
            if next_function_call == 'register_student':
                FUNCTION_DICTIONARY[next_function_call](registration_status, new_student_object, input_student_identifier, identifier_types_list, input_identifier_type_index)
        else:
            pass



def next_function(option_pair_list):
    """
    Prints a list of indexed options, provided using the option_pair_list param - a list of 2-item lists, to the user,
    each featuring a description. Then prompts the user for input. Uses the user_input to select which function to
    call next, where the function to be called matches the selected description.
    """
    print("Enter a number corresponding to one of the following options:\n")
    for option_pair in option_pair_list:
        print(f"{option_pair[0]}: {FUNCTION_USER_DESCRIPTION_DICTIONARY[option_pair[1]]}.")

    print('\n')
    valid_input = False
    while (not valid_input):
        valid_input = gen_functions.validate_numeric_input(len(option_pair_list)) 
    
    for option_pair in option_pair_list:
        if valid_input in option_pair:
                    global next_function_call
                    next_function_call = option_pair[1]
                    return FUNCTION_DICTIONARY[next_function_call]


def go_back():
    """
    Allows the user to cancel the current function called, in particular its action, and returns ths user
    to the previous function called.
    """
    global next_function_call
    global last_function_call

    next_function_call = last_function_call


def exit_the_program():
    """
    When called clears the terminal, informs the user the program is quitting, pauses,
    before clearing the terminal again, and terminating the program.
    """
    system('clear')
    print('Quitting the unigrade program...')
    time.sleep(3.0)
    system('clear')
    sys.exit()


def main():
    """
    Runs and controls program execution.
    """
    global FUNCTION_DICTIONARY
    FUNCTION_DICTIONARY = {'top_level_interface': top_level_interface, 'student_information_top_level_interface': student_information_top_level_interface,
                           'modules_interface': modules_interface, 'student_registration_interface': student_registration_interface,
                            'register_student': register_student, 'unregister_student': unregister_student, 
                            'view_or_edit_student_details_interface': view_or_edit_student_details_interface, 'exit_the_program': exit_the_program, 'go_back' : go_back}
    
    global FUNCTION_USER_DESCRIPTION_DICTIONARY
    FUNCTION_USER_DESCRIPTION_DICTIONARY = {'top_level_interface': 'return to the top program interface',
                                        'student_information_top_level_interface': 'view or add/edit student information',
                                        'modules_interface': 'view module information and statistics','student_registration_interface': 'register or unregister a student',                                        'register_student': 'register the student',
                                        'unregister_student': 'unregister the student', 'view_or_edit_student_details_interface': 'view and edit student details',
                                        'exit_the_program': 'exit the unigrade program',
                                        'go_back': 'go back'}
    global last_function_call
    last_function_call = ''
    global next_function_call
    next_function_call = 'top_level_interface'
    while True:
        FUNCTION_DICTIONARY[next_function_call]()


main()