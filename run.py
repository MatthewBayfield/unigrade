from os import system
import gspread
from google.oauth2.service_account import Credentials
import sys
import time
import modules.classes.student as student
import modules.classes.academic_module as academic_module
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


def top_level_interface():
    """
    Displays the top-level interface, after clearing the console.
    The user is prompted to choose one of two options: either view module information, or view and or edit/add student information.
    """
    gen_functions.clear()
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
    gen_functions.clear()
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
    next_function([['1', 'view_or_edit_student_details_interface'], ['2', 'student_registration_interface'], ['3', 'view_or_edit_student_module_info_and_grades_interface'],
                   ['4', 'top_level_interface'], ['5', 'exit_the_program']])


def register_student(registration_status, new_student_object, valid_entry, user_options, user_options_index):
    """
    Registers a student in the unigrade google sheet, by invoking the student class methods,
    on the new_student_object param. Should only be called within the student_registration_interface function.
    """
    if registration_status != 'Student is currently registered.\n':
        new_student_object.register(valid_entry, user_options[user_options_index])
        global next_function_call
        next_function_call = 'go_back'
    else:
        print('Student is currently registered.\n')
        next_function([['1', 'unregister_student'], ['2', 'go_back']])


def unregister_student(registration_status, new_student_object, valid_entry, user_options, user_options_index):
    """
    Unregisters a student in the unigrade google sheet, by invoking the student class methods, on the new_student_object param.
    Should only be called within the student_registration_interface function --- unused params allow the function to be called
    within this function .
    """
    if registration_status == 'Student is currently registered.\n':
        new_student_object.unregister()
        global next_function_call
        next_function_call = 'go_back'
    else:
        print('Student is already not registered.\n')
        next_function([['1', 'register_student'], ['2', 'go_back']])


def student_registration_interface():
    """
    Displays the student registration interface to the user. Prompts the user to input a student's name or ID, then
    confirms whether the student is currently registered in the unigrade google sheet, before allowing the user to register or unregister a
    student by perfoming the registration process.
    """
    gen_functions.clear()
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
    Prompts the user to input a student's name or ID, for a query within the unigrade google sheet.
    If the student is not registered, the user is given the option of registering the student. If the student
    is registered, their details are displayed in a table printed to the terminal. The user is then able to edit
    the mutable details if they desire, which are then updated in the unigrade google sheet.
    """
    gen_functions.clear()
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
                valid_input = False
                print("Enter a number to edit student details, or to go back :\n")
                options = ["Alter the student's study programme, and their start and end year", 'go back']
                for i in range(0, 2, 1):
                    print(f"{i+1}: {options[i]}")
                print('')
                while not valid_input:
                    valid_input = gen_functions.validate_numeric_input(2)
                if valid_input == '2':
                    next_function_call = 'go_back'
                    break
                elif valid_input == '1':
                    new_student_object.edit_student_details()


def view_or_edit_student_module_info_and_grades_interface():
    """
    Allows a user to view a registered student's enrolled module information, by printing the information, including tables,
    to the terminal. The user is then given options to update a student's module status and mark, as well an enrol/unenrol
    on/from an optional module on their current academic year.
    """
    gen_functions.clear()
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
            if next_function_call == 'register_student':
                FUNCTION_DICTIONARY[next_function_call](registration_status, new_student_object, input_student_identifier, identifier_types_list, input_identifier_type_index)
                next_function_call = 'student_information_top_level_interface'
        else:
            time.sleep(2.0)
            new_student_object.compulsory_module_enrolment_checker_and_updater()
            module_info = {}
            modules_enrolled ={}
            def load_and_prepare_module_information():
                gen_functions.clear()
                print('Loading student details, module information and grades...')
                nonlocal module_info
                for year in range(1, 5, 1):
                    print(f'Loading year {year} enrolled module information...')
                    time.sleep(2)
                    module_info[f'year {year}'] = new_student_object.retrieve_student_enrolled_module_info(year)
                    print(f'year {year} enrolled module information loaded.')
                    time.sleep(2)

                nonlocal modules_enrolled
                for key, value in module_info.items():
                    modules_enrolled.update({key: value[2]})
                new_student_object.enrolled_modules = modules_enrolled

            load_and_prepare_module_information()
            def print_info():
                gen_functions.clear()
                print("Student's details:")
                time.sleep(1)
                new_student_object.retrieve_student_details()
                time.sleep(1)
                print('')
                print(new_student_object.student_current_year()[1])
                print('')
                time.sleep(2)
                print("Module information for all the student's currently enrolled modules:")
                time.sleep(2)
                print('')
                if list(modules_enrolled.values()) == [[], [], [], []]:
                    print('Student is not enrolled on any modules.')
                else:
                    for key, value in module_info.items():
                        if value[2] != []:
                            print(f'{key} modules:\n')
                            time.sleep(1.1)
                            print(str('Module status table:').center(60))
                            time.sleep(1.1)
                            print(value[0])
                            time.sleep(1.1)
                            print('')
                            print(str('Module grades table:').center(60))
                            time.sleep(1.1)
                            print(value[1])
                            print('')
                            time.sleep(1.1)
            print_info()
            time.sleep(1)
            print('''Inspect the above tables, and then enter a number corresponding to one of the
following options:\n''')
            print("1. Update the student's module status and mark for a module.")
            print("""2. View the available optional module credits left for a student in their
current academic year, and enrol the student on an optional module.""")
            print("""3. View the student's currently enrolled optional modules for their current
academic year, and unenrol the student from an optional module .""")
            print('4. Go back.')
            valid_input = False
            while not valid_input:
                valid_input = gen_functions.validate_numeric_input(4)
            if valid_input == '1':
                next_function_call = new_student_object.edit_student_module_info(print_info, load_and_prepare_module_information)
            elif valid_input == '2':
                next_function_call = new_student_object.enrol_student_on_module()
            elif valid_input == '3':
                next_function_call = new_student_object.unenrol_student_from_module()
            else:
                next_function_call = 'student_information_top_level_interface'


def modules_interface():
    """
    Displays the modules terminal interface to the user. Provides options to the user.
    
    Prompts the user to select to add a new module to or edit an existing module in the unigrade google sheet;
    to view module statistics; or to 'go back' or 'exit' the program.
    """
    gen_functions.clear()
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
    next_function([['1', 'add_module_interface'], ['2', 'edit_module_properties_interface'], ['3', 'top_level_interface'],
                   ['4', 'exit_the_program']])
    global last_function_call
    last_function_call = 'modules_interface'


def set_subset_of_module_properties(module_year):
    """
    Allows the user to assign/reassign all mutable module properties of a module.

    Requests user inputs in order to set a subset of all the module properties.

    Args:
        module_year (int): The academic year on which the module is taught.

    Returns:
        A list containing the assigned/reassigned mutable properties. 
    """
    correct_activity = False
    while not correct_activity:
        print('Is the module currently being taught?')
        print('Enter 1 for yes, 2 for no.')
        valid_input = False
        while not valid_input:
            valid_input = gen_functions.validate_numeric_input(2)
        activity = True if valid_input == '1' else False
        print(f"Module is being taught: {activity}. ")
        print('is this correct? Enter 1 for yes, 2 for no.')
        correct_activity = gen_functions.is_this_correct_checker(valid_input, 'module activity')
    print('')

    study_programmes = ['MSci Physics', 'BSc Physics']
    availability = {}
    compulsory_status = {}
    for programme in study_programmes:
        if module_year!= 4:
            correct_availability = False
            while not correct_availability:
                print(f'Is the module available on the {programme} programme?')
                print('Enter 1 for yes, 2 for no.')
                valid_input = False
                while not valid_input:
                    valid_input = gen_functions.validate_numeric_input(2)
                availability[f'{programme}'] = True if valid_input == '1' else False
                print(f"Module available on {programme}:", f"{availability[programme]}.")
                print('is this correct? Enter 1 for yes, 2 for no.')
                correct_availability = gen_functions.is_this_correct_checker(valid_input, 'availability')
                print('')
        else:
            availability[f'{programme}'] = True if programme == 'MSci Physics' else False
        

        if availability[programme]:
            correct_compulsory_status = False
            while not correct_compulsory_status:
                print(f'Is the module compulsory on the {programme} programme?')
                print('Enter 1 for yes, 2 for no.')
                valid_input = False
                while not valid_input:
                    valid_input = gen_functions.validate_numeric_input(2)
                compulsory_status[f'{programme}'] = True if valid_input == '1' else False
                print(f"Module compulsory on {programme}:", f"{compulsory_status[programme]}.")
                print('is this correct? Enter 1 for yes, 2 for no.')
                correct_compulsory_status = gen_functions.is_this_correct_checker(valid_input, 'compulsory status')
                print('')
        else:
            compulsory_status[f'{programme}'] = False

    print('Enter the number of credits the module is worth; this should be a multiple of 15.\n')
    correct_credits = False
    while not correct_credits:
        valid_credits = False
        while not valid_credits:
            valid_credits = gen_functions.validate_module_credits_input()
        print(f'Module credits: {valid_credits}')
        print('is this correct? Enter 1 for yes, 2 for no.')
        correct_credits = gen_functions.is_this_correct_checker(valid_credits, 'number of credits the module is worth')
    
    return [activity, availability, compulsory_status, int(valid_credits)]


def add_module_interface(module_title=None):
    """
    Executes the process of adding a new module to the unigrade google sheet.

    First prompts the user to enter a valid module title, and then checks that this module does not already exist.
    (If the module already exists, the user is given the option of editing its module properties.)
    The user is then prompted to enter valid module properties for the new module. A new AcademicModule instance
    object is then initialised using these properties as parameters. The add_module method is then called on the object.
    
    Args:
        module_title (str): An optional parameter, that when passed has a value equal to a valid module title.
                            It should be passed in a function call inside the edit_module_properties_interface.
    """
    gen_functions.clear()
    print('Commencing add a module:\n')
    print('Do you want to continue? 1 for yes, 2 for no.')
    valid_input = False
    while not valid_input:
        valid_input = gen_functions.validate_numeric_input(2)
    if valid_input == '2':
        next_function([['1', 'go_back'],['2', 'top_level_interface'], ['3', 'exit_the_program']])
        return
    else:
        if module_title is None:
            correct_title = False
            while not correct_title:
                print('')
                print('Enter the module code, for example PHAS0019.\n')
                correct_code = False
                while not correct_code:
                    valid_code = False
                    while not valid_code:
                            valid_code = gen_functions.validate_module_title_input('code')
                    print(f"Module code: {valid_code} ")
                    print('is this correct? Enter 1 for yes, 2 for no.\n')
                    correct_code = gen_functions.is_this_correct_checker(valid_code, 'module code')
                print('')
                print('Enter the module name, with each word in the name separated by a comma; for example Planetary,Science.\n')
                correct_name = False
                while not correct_name:
                    valid_name = False
                    while not valid_name:
                            valid_name = gen_functions.validate_module_title_input('name')
                    print(f"Module name: {valid_name} ")
                    print('is this correct? Enter 1 for yes, 2 for no.')
                    correct_name = gen_functions.is_this_correct_checker(valid_name, 'module name')
                valid_title = f'{valid_code}: {valid_name}'
                print('')
                print(f'Module title: {valid_title}')
                print('is this correct? Enter 1 for yes, 2 for no.')
                correct_title = gen_functions.is_this_correct_checker(valid_title, 'module title')

            MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
            if MODULE_PROPERTIES_WORKSHEET.find(valid_title):
                print('')
                print('A module with this module title already exists.\n')
                print('Enter a number corresponding to one of the following options:')
                print('1. Edit/View this modules properties.')
                print('2. Go back')
                valid_input = False
                while not valid_input:
                    valid_input = gen_functions.validate_numeric_input(2)
                if valid_input == '1':
                    edit_module_properties_interface(valid_title)
                global next_function_call
                next_function_call = 'go_back'
                return
        else:
            valid_title = module_title

        print('')
        print('Enter the academic year on which the module is to be taught, thus a number 1-4.')
        correct_year = False
        while not correct_year:
            valid_year = False
            while not valid_year:
                valid_year = gen_functions.validate_numeric_input(4)
            print(f"Module year: {valid_year} ")
            print('is this correct? Enter 1 for yes, 2 for no.')
            correct_year = gen_functions.is_this_correct_checker(valid_year, 'module year')
        print('')

        module_properties_subset = set_subset_of_module_properties(int(valid_year))
        
        
        new_module_object = academic_module.AcademicModule(int(valid_year), valid_title, module_properties_subset[1], module_properties_subset[3],
                                           module_properties_subset[2], module_properties_subset[0])
        print('')
        print('Adding module to the unigrade google sheet...')
        new_module_object.add_module()
        print('Module successfully added.')
        time.sleep(1)
        print('Enter any key to continue.')
        input('->')


def edit_module_properties_interface(module_title=None):
    """
    Executes the process of editing the mutable properties of a module in the unigrade google sheet.

    First prompts the user to enter a valid module title, and then checks the module exists in
    the google sheet. (If the module does not exist, the user is given the option to add the module.)
    The module properties for the module are then retrieved and printed to the terminal, and the user
    can confirm to edit the properties. A new AcademicModule instance object is then initialised using
    these properties as parameters. The edit_module_properties method is then called on the object.

    Args:
        module_title (str): An optional parameter, that when passed has a value equal to a valid module title.
                            It should be passed in a function call inside the add_module_interface.
    """
    gen_functions.clear()
    print('Commencing view/edit module properties:', '\n')
    print('Do you want to continue? 1 for yes, 2 for no.')
    valid_input = False
    while not valid_input:
        valid_input = gen_functions.validate_numeric_input(2)
    if valid_input == '2':
        next_function([['1', 'go_back'],['2', 'top_level_interface'], ['3', 'exit_the_program']])
        return
    else:
        if module_title is None:
            correct_title = False
            while not correct_title:
                print('')
                print('Enter the module code, for example PHAS0019.\n')
                correct_code = False
                while not correct_code:
                    valid_code = False
                    while not valid_code:
                            valid_code = gen_functions.validate_module_title_input('code')
                    print(f"Module code: {valid_code} ")
                    print('is this correct? Enter 1 for yes, 2 for no.\n')
                    correct_code = gen_functions.is_this_correct_checker(valid_code, 'module code')
                print('')
                print('Enter the module name, with each word in the name separated by a comma; for example Planetary,Science.\n')
                correct_name = False
                while not correct_name:
                    valid_name = False
                    while not valid_name:
                            valid_name = gen_functions.validate_module_title_input('name')
                    print(f"Module name: {valid_name} ")
                    print('is this correct? Enter 1 for yes, 2 for no.')
                    correct_name = gen_functions.is_this_correct_checker(valid_name, 'module name')
                valid_title = f'{valid_code}: {valid_name}'
                print('')
                print(f'Module title: {valid_title}')
                print('is this correct? Enter 1 for yes, 2 for no.')
                correct_title = gen_functions.is_this_correct_checker(valid_title, 'module code and name')
            title_exists = False
            for year in [1, 2, 3, 4]:
                module_year_modules_sheet = SHEET.worksheet(f'year {year} modules')
                if module_year_modules_sheet.find(valid_title, in_row=1):
                    title_exists = True
                    break
            if not title_exists:
                print('')
                print('No module with this title exists in the unigrade google sheet.\n')
                print('Enter a number corresponding to one of the following options:')
                print('1. Add this module.')
                print('2. Go back.')
                valid_input = False
                while not valid_input:
                    valid_input = gen_functions.validate_numeric_input(2)
                if valid_input == '1':
                    add_module_interface(valid_title)
                global next_function_call
                next_function_call = 'go_back'
                return
        else:
            valid_title = module_title
    
        MODULE_PROPERTIES_WORKSHEET = SHEET.worksheet('module properties')
        module_title_entry_cell = MODULE_PROPERTIES_WORKSHEET.find(f'{valid_title}')
        module_properties_batch_get_range = f"{gspread.utils.rowcol_to_a1(module_title_entry_cell.row, module_title_entry_cell.col + 1)}:{gspread.utils.rowcol_to_a1(module_title_entry_cell.row, module_title_entry_cell.col + 6)}"
        module_properties = MODULE_PROPERTIES_WORKSHEET.batch_get([module_properties_batch_get_range], major_dimension='ROWS')[0][0]
        module_properties_descriptors = ['Module currently active', 'Available on MSci Physics','Compulsory on MSci Physics',
                                            'Available on BSc Physics', 'Compulsory on BSc Physics', 'Module credits']
        module_year = int(MODULE_PROPERTIES_WORKSHEET.cell(1, module_title_entry_cell.col).value.split(' ')[1])
        print('')                                  
        print(f"'{valid_title}' current module properties:".center(60))
        print('')
        print(f'Module year: {module_year}')
        for property_num in range(0, len(module_properties) - 1, 1):
            property_value = 'YES' if module_properties[property_num] == 'X' else 'NO'
            print(f'{module_properties_descriptors[property_num]}:', f'{property_value}')
        print(f'{module_properties_descriptors[len(module_properties) - 1]}:', f'{module_properties[len(module_properties) - 1]}')
        print('')
        print('Enter 1 to edit the mutable module properties, or enter 2 to go back.')
        valid_input = False
        while not valid_input:
            valid_input = gen_functions.validate_numeric_input(2)
        if valid_input == '2':
            next_function_call = 'go_back'
            return
        module_properties_subset = set_subset_of_module_properties(module_year)
        new_module_object = academic_module.AcademicModule(module_year, valid_title, module_properties_subset[1], module_properties_subset[3],
                                        module_properties_subset[2], module_properties_subset[0])
        print('')
        print('Updating module properties in the unigrade google sheet...')
        new_module_object.edit_module_properties()
        print('Module properties successfully updated.')
        time.sleep(1)
        print('Enter any key to continue.')
        input('->')


def next_function(option_pair_list):
    """
    Prints a list of indexed options, provided using the option_pair_list param - a list of 2-item lists, to the user,
    each featuring a description. Then prompts the user for input. Uses the user_input to select which function to
    call next, where the function to be called matches the selected description.
    """
    print("Enter a number corresponding to one of the following options:\n")
    for option_pair in option_pair_list:
        print(f"{option_pair[0]}: {FUNCTION_USER_DESCRIPTION_DICTIONARY[option_pair[1]]}.")

    print('')
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
    gen_functions.clear()
    print('Quitting the unigrade program...')
    time.sleep(3.0)
    gen_functions.clear()
    sys.exit()


def main():
    """
    Runs and controls program execution.
    """
    global FUNCTION_DICTIONARY
    FUNCTION_DICTIONARY = {'top_level_interface': top_level_interface, 'student_information_top_level_interface': student_information_top_level_interface,
                           'modules_interface': modules_interface, 'student_registration_interface': student_registration_interface,
                            'register_student': register_student, 'unregister_student': unregister_student, 
                            'view_or_edit_student_details_interface': view_or_edit_student_details_interface,
                            'view_or_edit_student_module_info_and_grades_interface': view_or_edit_student_module_info_and_grades_interface,
                            'add_module_interface': add_module_interface, 'edit_module_properties_interface': edit_module_properties_interface,
                            'exit_the_program': exit_the_program, 'go_back' : go_back}
    
    global FUNCTION_USER_DESCRIPTION_DICTIONARY
    FUNCTION_USER_DESCRIPTION_DICTIONARY = {'top_level_interface': 'return to the top program interface',
                                        'student_information_top_level_interface': 'view or add/edit student information',
                                        'modules_interface': 'view module information and statistics','student_registration_interface': 'register or unregister a student',                                        'register_student': 'register the student',
                                        'unregister_student': 'unregister the student', 'view_or_edit_student_details_interface': 'view and edit student details',
                                        'view_or_edit_student_module_info_and_grades_interface': 'view/edit student module information, including grades and enrolment status',
                                        'add_module_interface': 'add a new module', 'edit_module_properties_interface': 'update the module properties of an existing module',
                                        'exit_the_program': 'exit the unigrade program', 'go_back': 'go back'}
    global last_function_call
    last_function_call = ''
    global next_function_call
    next_function_call = 'top_level_interface'
    while True:
        FUNCTION_DICTIONARY[next_function_call]()


main()