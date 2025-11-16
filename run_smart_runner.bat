@echo off
ECHO Starting the Smart Runner script with full paths...

REM Activate the virtual environment using its full path
ECHO Activating virtual environment...
call "D:\employee_form\venv\Scripts\activate.bat"

REM Run the Python script using the full path to python.exe AND the script
ECHO Running the Python script...
"D:\employee_form\venv\Scripts\python.exe" "D:\employee_form\smart_runner.py"

ECHO Script finished.
pause