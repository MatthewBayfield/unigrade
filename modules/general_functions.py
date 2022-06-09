from os import system
import gspread
import decorated_gspread_methods


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


def validate_module_title_input(component):
    """
    Prompts the user to input a module code or module name for a module, and validates the input.

    Args:
        component (str): Has the value 'code' or 'name'. Determines which input is requested.
    
    Returns:
        In the absence of exceptions, returns a formatted form of the requested input.
    
    Raises:
        ValueError: if non-alphanumeric characters are used in the module code or module name.
    """
    if component == 'code':
        try:
            code = input('->')
            if not code.isalnum():
                raise ValueError('Invalid input. Please use only standard alphanumeric characters in the module code.')
        except ValueError as error:
            print(f"{error}\n")
        else:
            return f"{code.upper()}"
    
    if component == 'name':
        try:
            name = input('->')
            name_words = name.split(',')
            filtered_name_words = list(filter(lambda word: word != '', name_words))
            for word in filtered_name_words:
                if not word.isalnum():
                    raise ValueError('Invalid input. Please use only standard alphanumeric characters in the module name.')
        except ValueError as error:
            print(f"{error}\n")
        else:
            return f"{' '.join(filtered_name_words).title()}"


def validate_module_credits_input():
    """
    Prompts the user to input the module credits for a module and validates the input.

    Returns:
        In the absence of exceptions, returns the input.

    Raises:
        ValueError: if the credits input is not a number.
        ValueError: if the credits input is not divisable by 15.
    """
    try:
        num_of_credits = input('->')
        if not num_of_credits.isdigit():
            raise ValueError('Invalid input. The credits must be a number, that is a multiple of 15.')
        if int(num_of_credits) % 15 != 0:
            raise ValueError('Invalid input. The number of credits must be a multiple of 15.')
    except ValueError as error:
        print(f'{error}\n')
    else:
        return num_of_credits


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


def clear():
    """
    Clears the visible portion of the terminal, and then prints empty rows as well as a
    'top of terminal banner' to visually separate future printed content, from the scrollback
    history.
    """
    system('clear')
    print('\n' * 24)
    print('-----------------------------------------------------------------')
    print('                            TOP')
    print('-----------------------------------------------------------------')
    print('\n' * 24)
    system('clear')
    