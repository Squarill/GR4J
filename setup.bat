@echo off

python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python found!
    python --version
) else (
    echo Python not found!
    echo Please install python 3 or higher and add it to PATH.
    echo https://www.python.org/downloads/
    echo Also, you can install it by executing this command in command prompt.
    echo winget install Python.Python.3.12
    pause
    exit
)

if exist .venv\ (
    echo Virtual environment has been found.
) else (
    echo Virtual environment not found. Creating...
    python -m venv .venv
    echo Virtual environment created successfully.
)

echo Installing requirements...
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% == 0 (
    echo Requirements installed successfully.
) else (
    echo Requirements installation failed.
    pause
    exit
)
echo Requirements installed successfully.
echo Now you can run your code with run.bat through the virtual environment.
pause
exit