from os import system
import gspread
import decorated_gspread_methods


def validate_numeric_input(number_of_options):
    '''
    Validates numeric user inputs: checks that a user enters an integer belonging to a specified range of integers.

    Prompts user input. Tests whether the user input is in the valid range of integers, as determined by the number_of_options parameter.

    Args:
        number_of_options (int): determines the size of the range of integers, where the step is one.
    
    Returns:
        Returns a False boolean if the user input is invalid, or the user input value for a valid input.

    Raises:
        ValueError: if the user input is not an integer belonging to the valid range of integers.

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
    Validates student name user inputs: checks the input is in the correct format, and only contains alphabetic characters.

    Prompts a user for input. Checks whether a 'student name' user input is valid.

    Returns:
        Returns a False boolean if the user input is invalid, or the user input value for a valid input.

    Raises:
        ValueError: if the user input is not in the correct format, or does not contain only alphabetic characters.

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
    Prompts the user for input in response to being asked to enter '1' for 'yes', '2' for 'no, to confirm their input is correct.

    Called after a user input to prompt the user for further input to confirm whether the input they entered is correct.
    Returns a boolean, or the user input value

    Args:
        user_input: the user input the user was asked to confirm is correct.
        user_input_description (str): a description of the user input, that is printed as part of a string to the user
        if they do not confirm their input, that instructs them to enter the correct input.

    Returns:
        Returns a False boolean if the user does not confirm their input, or the confirmed user input value if they do.
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
            filtered_name_words = [word.lower() for word in filtered_name_words]
            for word_index in range(0, len(filtered_name_words), 1):
                if filtered_name_words[word_index] not in ['of', 'the', 'and']:
                    filtered_name_words[word_index] = filtered_name_words[word_index].capitalize()  
            return f"{' '.join(filtered_name_words)}"


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
    Updates the border formatting of a worksheet in a google sheet. In particular it gives all cells a black border.
    
    This function should be called when new rows or columns are added to the worksheet in the google sheet.
    Uses the gspread batch_update API method.

    Args:
        google_sheet: a gspread Spreadsheet class instance.
           worksheet: a gspread Worksheet class instance, where the worksheet belongs to the spreadsheet.
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
    Effectively clears the terminal.
    
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
    