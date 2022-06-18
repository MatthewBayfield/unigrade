# Testing

Testing was performed throughout the development of the unigrade program, and took two forms, namely manual testing,
and the use of python linters.

## Manual testing 

This primarily involved testing the program in the terminal, by running the code and observing the outcomes,
and was also supplemented by the use of targeted print and break statements to determine the flow control, as well as
also by interpreting any exceptions raised. Additionally the effects on the unigrade google sheet were inspected,
to ensure the functionality of the code was as expected. Finally the deployed version of the program in the heroku 
mock terminal was tested by testing all the possible paths through the program as well all of the intended functionality,
and essentially trying to break it; for example entering all types of input combinations, both invalid and valid,
to ensure the input validation methods worked as desired, and that there were no circumstances that led to the program
failing to perform its desired activities.

### Manual testing detected issues

Here are some of the more prominent issues/bugs that were discovered using manual testing, and their fixes:

- In order to access, retrieve, and update information contained in the unigrade google sheet, the 
google sheets API accessed using the gspread imported module was used. However I discovered that through
the raised APIError exception 'resource exhausted', that the google sheets API has a request rate limit of
60 requests per minute per user. Consequently the various gspread methods acting on the unigrade sheet would
raise exceptions if this rate was exceeded. In order to handle these exceptions and still be able to complete
the desired requests, I created a gspread method decorator, that handles the exception by continously retrying
the request until it is successful, whilst displaying to the user a timer indicating the max time left for loading.
The decorator was applied to all gspread methods used.

- I noticed in the heroku version of the program, that the narrower terminal width, caused issues with the display of
some printed strings and also tables with many columns, causing the table to be cut off, and the strings wrapped
inappropriately. To solve this, for the strings: I used multiline strings and wrapped the strings manually; for
the tables: I first split them up where possible in to two separate tables displayed one after another, as well as
reformatting the contents, for example wrapping the table content, and adjusting the text justification.

- Sometimes information displayed to the terminal, including loading/update/confirmation messages and other information
of interest to the user, would not be displayed long enough for the user to read before the terminal was cleared or the
next function started. This was solved using a combination of pausing the program using the sleep function of the time
module, that would also stagger outputs, alongside using user inputs to prompt the user to continue when ready. Both of
these solutions also solved the similar issue of too much information being printed at once,
causing the terminal to scroll rapidly, making it easy for the user to miss new information,
 and confuse it with information from the past. The sleep function would make tracking outputs easier by causing
 them to be staggered.
 
- During student registration or when altering student details, it was possible to set the start year of a student,
to a year in the past, and to adjust the start year of a student who had already started their course. The code was
edited to raise a user input exception if the year was in the past, and a user was prevented from changing the
start year unless the student is yet to start, with user feedback now given.

- During the editing of a student's details, it was possible to change the study programme of a student
who is in their 3rd year academic year, which is not in-keeping with the desired functionality of the unigrade program.
This was fixed by altering the code logic, in particular adding an additional if condition to assess the student's
current year, and thus determine the flow accordingly.

- When performing a specific batch_get request, I was not always getting the range of cells expected. It turned out
the way I was generatinng part of the batch_get range in A1 notation, that involved extracting the column letter using
the index syntax on the string, failed for columns designated with two letters as opposed to one. This was fixed by
using the slice syntax on the string.

- When registering a student it was possible to register a student with a unique ID or name, but with a non-unique
  name or ID. This led to confusion, and also caused some of the other code functionality to not work properly,
  as effectively there were duplicate student names or ID's with different ID's and names. Fixed by adding an extra layer
  of input validation where each student identifier was checked for its uniqueness, rather than just the first one entered.

      
### Python Linters

Both the flake8 and PEP8 online linter were used. These helped to identify any minor syntax/style errors in my code,
such as trailing whitespaces, extra blank lines, missing space around operators, as well as 'lines too long' warnings.

The current program is free of any significant errors, with the only warnings remaining being of the type
'line too long'. Best efforts have been made to minimise the width of lines to under 79 characters, however
this was not always possible, or necessarily preferable in my opinion for the readability of the program code.

[return to README.md](README.md)