@echo off
REM Setup script for p1person - Windows version
REM Installs dependencies and runs initial configuration

echo =================================================
echo p1person - PingOne Custom Attribute Manager
echo Setup Script v0.2 (Windows)
echo =================================================
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo X ERROR: Python is not installed
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo + Python found: %PYTHON_VERSION%
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo X ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo + Virtual environment created
) else (
    echo + Virtual environment already exists
)
echo.

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo X ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo X ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo + Dependencies installed
echo.

REM Run tests
echo Running unit tests...
python test_p1person.py
set TEST_RESULT=%ERRORLEVEL%
echo.

if %TEST_RESULT% equ 0 (
    echo + All tests passed
    echo.
    echo =================================================
    echo Setup Complete!
    echo =================================================
    echo.
    echo To use p1person:
    echo   1. Activate the virtual environment:
    echo      venv\Scripts\activate.bat
    echo.
    echo   2. Run p1person:
    echo      python p1person.py -n  # Initial setup
    echo      python p1person.py -h  # Show help
    echo.
    echo   3. When done, deactivate:
    echo      deactivate
    echo.
    pause
) else (
    echo X Some tests failed
    echo Please review the errors above
    echo.
    pause
    exit /b 1
)
