@echo off
REM Build script for p1person package (Windows)
REM This script cleans old builds and creates new distribution packages

echo ===================================
echo p1person Package Build Script
echo ===================================
echo.

REM Step 1: Clean old build artifacts
echo Step 1: Cleaning old build artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist p1person.egg-info rmdir /s /q p1person.egg-info
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc >nul 2>&1
del /s /q *.pyo >nul 2>&1
echo [✓] Cleaned
echo.

REM Step 2: Check if build tools are installed
echo Step 2: Checking build tools...
python -c "import build" >nul 2>&1
if errorlevel 1 (
    echo Installing build tools...
    pip install --upgrade build twine
)
echo [✓] Build tools ready
echo.

REM Step 3: Build the package
echo Step 3: Building distributions...
python -m build
if errorlevel 1 (
    echo [✗] Build failed
    exit /b 1
)
echo [✓] Build complete
echo.

REM Step 4: Check the distributions
echo Step 4: Checking distributions...
twine check dist/*
if errorlevel 1 (
    echo [✗] Distribution check failed
    exit /b 1
)
echo [✓] Distributions validated
echo.

REM Step 5: List created files
echo Step 5: Created distribution files:
dir dist
echo.

echo ===================================
echo Build Complete!
echo ===================================
echo.
echo Next steps:
echo   • Test locally: pip install dist\p1person-0.2-py3-none-any.whl
echo   • Upload to TestPyPI: twine upload --repository testpypi dist/*
echo   • Upload to PyPI: twine upload dist/*
echo.

pause
