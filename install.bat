
@echo off
echo ========================================
echo   Quick Install - Agentic RAG Assistant
echo ========================================
echo.

REM Quick install script for users who just want to get started

echo Installing Python packages...
pip install streamlit langchain langgraph openai chromadb python-dotenv pypdf python-docx openpyxl python-pptx beautifulsoup4 lxml pandas numpy tiktoken sentence-transformers typing-extensions pydantic sqlalchemy

if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    echo Try running: setup.bat for a more thorough installation
    pause
    exit /b 1
)

echo.
echo Creating .env template...
if not exist .env (
    (
        echo OPENAI_API_KEY=your_openai_api_key_here
    ) > .env
    echo Created .env file - please edit it and add your OpenAI API key
)

echo.
echo ========================================
echo     Quick Install Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Run: streamlit run app.py
echo.
pause
