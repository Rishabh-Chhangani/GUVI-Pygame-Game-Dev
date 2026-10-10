@echo off
setlocal enabledelayedexpansion

REM 1. Change to the repository root reliably
cd /d "%~dp0"

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    exit /b 1
)

REM Check for pytest
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pytest is not installed. Run: pip install -r requirements.txt
    exit /b 1
)

REM 2. Create reports directory
if not exist reports (
    mkdir reports
)

REM 3. Run pytest and generate reports
echo Running pytest and generating coverage reports...
python -m pytest --cov=src --cov-report=term-missing --cov-report=json:reports/coverage.json --junitxml=reports/junit.xml
set PYTEST_EXIT_CODE=%ERRORLEVEL%

REM 4/5. Generate Markdown report
echo.
echo Generating Markdown report and updating history...
python scripts/generate_coverage_md.py
if errorlevel 1 (
    echo [ERROR] Failed to generate Markdown report.
    exit /b 1
)

REM 6. Display generated report paths
echo.
echo --------------------------------------------------
echo [SUCCESS] Reports generated successfully:
echo - Markdown Report : reports\coverage.md
echo - Coverage JSON   : reports\coverage.json
echo - JUnit XML       : reports\junit.xml
echo - History CSV     : reports\coverage_history.csv
echo --------------------------------------------------

REM 7. Return original pytest exit code
exit /b %PYTEST_EXIT_CODE%
