from os import system
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
    print("To view module information and statistics, enter 1.\n")
    print("To view or add/edit student information enter 2.\n")
    while True:
        try:
            user_selected_option = input("->")
            if user_selected_option in ('1', '2'):
                user_selected_options['user_selected_option1'] = user_selected_option
                break
            raise ValueError('Invalid input. Please enter either 1 or 2.')
        except ValueError as error:
            print(f"{error}\n")


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
    while True:
        try:
            user_selected_option = input("->")
            if user_selected_option in ('1', '2', '3', '4', '5'):
                user_selected_options['user_selected_option2'] = user_selected_option
                break
            raise ValueError('Invalid input. Please enter either 1,2,3,4, or 5')
        except ValueError as error:
            print(f"{error}\n")


def main():
    """
    Runs and controls program execution.
    """
    interface_level = 0
    global user_selected_options
    user_selected_options = {}
    while True:
        if interface_level == 0:
            top_level_interface()
            interface_level += 1
        user_selected_option1 = user_selected_options['user_selected_option1']
        if user_selected_option1 == '1':
            break
        elif user_selected_option1 == '2':
            if interface_level == 1:
                student_information_top_level_interface()
                interface_level += 1
        break


main()
