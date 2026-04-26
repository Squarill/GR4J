@echo off

if exist .venv\ (
    echo Virtual environment has been found.
) else (
    echo Virtual environment not found. Creating...
    python -m venv .venv
    echo Virtual environment created successfully.
)

echo Running the script...
.venv\Scripts\python main.py
echo Script executed successfully.
pause
exit