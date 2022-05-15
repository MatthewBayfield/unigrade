from os import system
import gspread
import time
import sys


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
            for i in range(0, len(names), 1):
                if i != (len(names) - 1):
                    student_name += names[i].capitalize()
                    student_name += " "
                else:
                    student_name += names[i].capitalize()

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


def update_sheet_borders(worksheet, google_sheet):
    """
    Updates the border formatting of a worksheet, supplied as a paramater, in a google sheet. In particular it gives all cells a black border.
    This function will be called when new rows or columns are added to the google sheet.
    Uses gspread batch_update API method. 
    """
    borders_update_body = {
        "requests": [
            {
                "updateBorders": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": 0,
                        "startColumnIndex": 0

                    },
                    "top": {
                        "style": "SOLID",
                        "width": 1,
                        "color": {
                            "red": 0,
                            "green": 0,
                            "blue": 0,
                            "alpha": 1
                        }
                    },
                    "bottom": {
                        "style": "SOLID",
                        "width": 1,
                        "color": {
                            "red": 0,
                            "green": 0,
                            "blue": 0,
                            "alpha": 1
                        }
                    },
                    "left": {
                        "style": "SOLID",
                        "width": 1,
                        "color": {
                            "red": 0,
                            "green": 0,
                            "blue": 0,
                            "alpha": 1
                        }
                    },
                    "right": {
                        "style": "SOLID",
                        "width": 1,
                        "color": {
                            "red": 0,
                            "green": 0,
                            "blue": 0,
                            "alpha": 1
                        }
                    },
                    "innerVertical": {
                        "style": "SOLID",
                        "width": 1,
                        "color": {
                            "red": 0,
                            "green": 0,
                            "blue": 0,
                            "alpha": 1
                        }
                    },
                    "innerHorizontal": {
                        "style": "SOLID",
                        "width": 1,
                        "color": {
                            "red": 0,
                            "green": 0,
                            "blue": 0,
                            "alpha": 1
                        }
                    }
                    
                } 
            }
        ]
    }
    google_sheet.batch_update(borders_update_body)


def gspread_api_error_exception_handling(gspread_method_or_request):
    """
    Decorator function that handles the processing of gspread 'APIError' exceptions that occur as part of a request in a called function or method.
    If a 'resource exhausted error' occurs, due to exceeding the google sheet API request rate of 60 requests per minute per user,
    then the request is repeated until successful, which should occur when upto 60 seconds have passed. The user is displayed
    a timer updating them of the maximum time left for loading. For any other form of API error,
    an error message is printed, and the program terminated.
    """
    def inner(*params, **kparams):
        time_left = 60
        while True:
            try:
                result = gspread_method_or_request(*params, **kparams)
                time_left = 60
            except gspread.exceptions.APIError as error:
                if error.args[0]['code'] == 429:
                    system('clear')
                    print('Loading...')
                    print(f'Max time left: {time_left}s')
                    time_left -= 1
                    time.sleep(1.0)
                    
                else:
                    print('''ERROR ENCOUNTERED: There seems to be a problem accessing the unigrade google sheet. The program will now terminate.
    Please try running the program again, and try to complete the desired action again. If the error persists try again later.\n''')
                    print('Enter any key to initiate exiting the unigrade program.')
                    input('->')
                    system('clear')
                    print('Quitting the unigrade program...')
                    time.sleep(3.0)
                    system('clear')
                    sys.exit()
                    
            else:
                return result
    return inner