import gspread
from os import system
import time
import sys


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
