
@echo off
echo ========================================
echo    Starting Agentic RAG Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found
    echo Please create .env file with your API keys
    echo You can copy .env.template to .env and edit it
    echo.
    if exist .env.template (
        echo Found .env.template - copying to .env...
        copy .env.template .env
        echo Please edit .env file and add your API keys, then run this script again
    )
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking configuration...
python -c "from config import Config; Config.ensure_directories(); print('✓ Configuration OK')"
if %errorlevel% neq 0 (
    echo ERROR: Configuration check failed
    pause
    exit /b 1
)

echo.
echo Starting Streamlit application...
echo The application will open in your default browser
echo Press Ctrl+C to stop the application
echo.

REM Start Streamlit with Windows-friendly settings
streamlit run app.py --server.headless false --server.enableCORS false --server.enableXsrfProtection false
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start the application
    echo Common issues:
    echo 1. Missing API key in .env file
    echo 2. Port 8501 already in use
    echo 3. Missing dependencies
    echo.
    pause
    exit /b 1
)

echo.
echo Application stopped.
pause
