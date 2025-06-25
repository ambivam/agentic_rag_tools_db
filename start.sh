
#!/bin/bash

# Linux/macOS startup script for Agentic RAG Assistant

echo "========================================"
echo "    Starting Agentic RAG Assistant"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    if [ -f ".env.template" ]; then
        echo "Copying .env.template to .env..."
        cp .env.template .env
        echo "Please edit .env file and add your API keys, then run this script again"
        exit 1
    else
        echo "Please create .env file with your API keys"
        exit 1
    fi
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Checking configuration..."
python -c "from config import Config; Config.ensure_directories(); print('✓ Configuration OK')" || {
    echo "ERROR: Configuration check failed"
    exit 1
}

echo
echo "Starting Streamlit application..."
echo "The application will open in your default browser"
echo "Press Ctrl+C to stop the application"
echo

# Start Streamlit
streamlit run app.py --server.headless false

echo
echo "Application stopped."
