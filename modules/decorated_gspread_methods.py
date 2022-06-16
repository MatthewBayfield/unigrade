import gspread
import time
import sys
from os import system


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


def gspread_api_error_exception_handling(gspread_method_or_request):
    """
    Decorator function that handles the processing of gspread 'APIError' exceptions that occur as part of a request in a method.

    If a 'resource exhausted error' occurs, due to exceeding the google sheet API request rate of 60 requests per minute per user,
    then the request is repeated until successful, which should occur when up to 60 seconds have passed. The user is displayed
    a timer updating them of the maximum time left for loading. For any other form of API error or gspread error,
    an error message is printed, and the program terminated.

    Args:
        gspread_method_or_request: any gspread method that uses the google sheets API.

    Returns:
            The decorated gspread method.
    
    Raises:
        gspread.exceptions.APIError: if a google sheets API error, including the 'resource exhausted error' occurs.
        gspread.exceptions.GSpreadException: if any non-API related gspread error occurs.
    """
    def inner(*params, **kparams):
        time_left = 60
        while True:
            try:
                result = gspread_method_or_request(*params, **kparams)
                time_left = 60
            except gspread.exceptions.APIError as error:
                if error.args[0]['code'] == 429:
                    clear()
                    print('Loading...')
                    print(f'Max time left: {time_left}s')
                    time_left -= 1
                    time.sleep(1.0)

                else:
                    print('''ERROR ENCOUNTERED: There seems to be a problem accessing
the unigrade google sheet, and or performing the requested actions.
The program will now terminate. Please try running the program again,
and try to complete the desired action again.
If the error persists try again later.\n''')
                    print('Enter any key to initiate exiting the unigrade program.')
                    input('->')
                    clear()
                    print('Quitting the unigrade program...')
                    time.sleep(3.0)
                    clear()
                    sys.exit()
                    
            except gspread.exceptions.GSpreadException:
                print('''ERROR ENCOUNTERED: There seems to be a problem accessing
the unigrade google sheet, and or performing the requested actions.
The program will now terminate. Please try running the program again,
and try to complete the desired action again.
If the error persists try again later.\n''')
                print('Enter any key to initiate exiting the unigrade program.')
                input('->')
                clear()
                print('Quitting the unigrade program...')
                time.sleep(3.0)
                clear()
                sys.exit()
               
            else:
                return result
    return inner


# Decorated gspread methods of interest. Executed when imported as part of this module.
gspread.worksheet.Worksheet.find = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.find)
gspread.worksheet.Worksheet.findall = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.findall)
gspread.worksheet.Worksheet.cell = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.cell) 
gspread.worksheet.Worksheet.update_cell = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.update_cell)
gspread.worksheet.Worksheet.col_values = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.col_values)
gspread.worksheet.Worksheet.add_rows = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.add_rows)
gspread.worksheet.Worksheet.delete_rows = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.delete_rows)
gspread.worksheet.Worksheet.row_values = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.row_values)
gspread.worksheet.Worksheet.get = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.get)
gspread.worksheet.Worksheet.batch_get = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.batch_get)
gspread.worksheet.Worksheet.batch_update = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.batch_update)
gspread.worksheet.Worksheet.batch_clear = gspread_api_error_exception_handling(gspread.worksheet.Worksheet.batch_clear)
gspread.spreadsheet.Spreadsheet.worksheet = gspread_api_error_exception_handling(gspread.spreadsheet.Spreadsheet.worksheet)
gspread.spreadsheet.Spreadsheet.worksheets = gspread_api_error_exception_handling(gspread.spreadsheet.Spreadsheet.worksheets)
gspread.spreadsheet.Spreadsheet.batch_update = gspread_api_error_exception_handling(gspread.spreadsheet.Spreadsheet.batch_update)
gspread.utils.rowcol_to_a1 = gspread_api_error_exception_handling(gspread.utils.rowcol_to_a1)
