
@echo off
echo ========================================
echo    Agentic RAG Assistant Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; print(f'Python {sys.version}'); exit(0 if sys.version_info >= (3, 11) else 1)"
if %errorlevel% neq 0 (
    echo ERROR: Python 3.11+ is required
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Creating .env file template...
if not exist .env (
    (
        echo # Agentic RAG Assistant Environment Variables
        echo # Copy this file to .env and fill in your API keys
        echo.
        echo # Required: OpenAI API Key
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Optional: Langchain Configuration
        echo LANGCHAIN_API_KEY=your_langchain_api_key_here
        echo LANGCHAIN_TRACING_V2=true
        echo LANGCHAIN_PROJECT=agentic-rag-app
    ) > .env.template
    echo Created .env.template file
    echo Please copy .env.template to .env and add your API keys
) else (
    echo .env file already exists
)

echo.
echo Creating vector store directory...
if not exist vector_store mkdir vector_store

echo.
echo ========================================
echo         Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Run: run.bat
echo.
echo For manual startup:
echo 1. venv\Scripts\activate.bat
echo 2. streamlit run app.py
echo.
pause
