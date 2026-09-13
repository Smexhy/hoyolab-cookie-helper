@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
python -c "import sys; raise SystemExit(sys.version_info < (3, 9))" >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
    py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 9))" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD goto :no_python

if not exist ".venv\Scripts\python.exe" (
    echo Preparing the helper...
    %PYTHON_CMD% -m venv .venv || goto :failed
)

echo Installing the pinned dependency...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt || goto :failed

if /I "%~1"=="--test" goto :test

".venv\Scripts\python.exe" get_cookie.py
set "RESULT=%errorlevel%"
echo.
pause
exit /b %RESULT%

:test
".venv\Scripts\python.exe" -m unittest discover -s tests
exit /b %errorlevel%

:no_python
echo Python 3.9 or newer was not found.
echo Install Python from https://www.python.org/downloads/
echo Then close this window and run this file again.
echo.
if /I "%~1"=="--test" exit /b 1
pause
exit /b 1

:failed
echo.
echo Setup failed. Read the error above, then see README.md.
echo.
if /I "%~1"=="--test" exit /b 1
pause
exit /b 1
