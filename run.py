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


def display_top_level_interface():
    """
    Displays the top-level interface, after clearing the console. The user is prompted to choose one of two options: either view module information, or view and or edit/add student information
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
            selected_option = input("->")
            if selected_option == '1':
                print('Loading module interface.')
                break
            elif selected_option == '2':
                print('Loading student information interface.')
                break
            else:
                raise ValueError('Invalid input. Please enter either 1 or 2.')
        except ValueError as error:
            print(f"{error}\n")


display_top_level_interface()
