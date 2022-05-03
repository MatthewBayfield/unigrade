from os import system
import gspread
from google.oauth2.service_account import Credentials
import sys
sys.path.insert(1, '/workspace/unigrade/classes')
import student

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('unigrade-physics')


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


def validate_numeric_input(number_of_options):
    '''
    Prompts user input. Tests whether the user input is in the valid range of integers, as determined by the number_of_options parameter.
    If it is not it raises an exception. Returns a boolean,  or the user input value, which will also
    be used to evaluate to a boolean within the function in which this function is called.
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


def student_information_top_level_interface():
    """
    Displays the top-level student information terminal interface to the user.
    Prompts the user to select to alter student registration, or to view/edit existing student information, as well as 'go back' or 'exit' the program.
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
    print("To view or edit information about an existing student, enter 1.\n")
    print("To register or unregister a student in the system enter 2.\n")
    print('''To go back a step, return to the initial interface,\nor exit the program; enter 3,4 and 5 respectively.\n''')
    valid_input = False
    while (not valid_input):
        valid_input = validate_numeric_input(5)


def register_student(registration_status, new_student_object, valid_entry, user_options, user_options_index):
    """
    Registers a student in the unigrade google sheet, by invoking the student class methods,
    on the new_student_object param. Should only be called within the
    student_registration_interface function.
    """
    if registration_status != 'Student is currently registered':
        new_student_object.register(valid_entry, user_options[user_options_index])
        global next_function_call
        next_function_call = 'student_registration_interface'
    else:
        print('Student is already registered.\n')
        next_function([['1', 'unregister the student'], ['2', 'go_back']])


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
        valid_input = validate_numeric_input(7)


def validate_student_name_input():
    """
    Prompts a user for input. Checks whether a 'student name' user input is valid. Returns a boolean, or the student name input, which will also
    be used to evaluate to a boolean within the function in which this function is called.
    """
    try:
        full_name = input('->')
        names = full_name.split(',')
        if full_name.count(',') != 1:
            raise ValueError('''Invalid input. Please enter a first, and last name separated with a comma;\nfor example: John,Smith.''')
        elif not (names[0].isalpha() and names[1].isalpha()):
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
        valid_input = validate_numeric_input(len(option_pair_list)) 
    
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


def main():
    """
    Runs and controls program execution.
    """
    global FUNCTION_DICTIONARY
    FUNCTION_DICTIONARY = {'top_level_interface': top_level_interface, 'student_information_top_level_interface': student_information_top_level_interface,
                           'modules_interface': modules_interface, 'exit_the_program': sys.exit, 'go_back' : go_back}
    
    global FUNCTION_USER_DESCRIPTION_DICTIONARY
    FUNCTION_USER_DESCRIPTION_DICTIONARY = {'top_level_interface': 'return to the top program interface',
                                        'student_information_top_level_interface': 'view or add/edit student information',
                                        'modules_interface': 'view module information and statistics', 'exit_the_program': 'exit the unigrade program',
                                        'go_back': 'go back'}
    
    global last_function_call
    last_function_call = ''
    global next_function_call
    next_function_call = 'top_level_interface'
    while True:
        FUNCTION_DICTIONARY[next_function_call]()


main()