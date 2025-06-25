
# 🪟 Windows Setup Guide for Agentic RAG Assistant

This guide provides detailed Windows-specific setup instructions for the Agentic RAG Assistant.

## 🔧 Prerequisites

### 1. Python Installation
- **Required Version**: Python 3.11 or higher
- **Download**: [python.org](https://python.org/downloads/windows/)
- **Installation Tips**:
  - ✅ Check "Add Python to PATH" during installation
  - ✅ Check "Install pip" option
  - ✅ Choose "Install for all users" if you have admin rights

### 2. System Requirements
- **Operating System**: Windows 10 or Windows 11
- **RAM**: Minimum 4GB (Recommended: 8GB+)
- **Storage**: 2GB free space
- **Internet**: Required for AI model access

## 🚀 Installation Methods

### Method 1: Automatic Setup (Recommended)

1. **Download the Project**
   - Extract all files to `C:\AgenticRAG\` (avoid long paths)

2. **Run Setup Script**
   - Double-click `setup.bat`
   - The script will automatically:
     - Check Python installation
     - Create virtual environment
     - Install all dependencies
     - Create configuration template

3. **Configure API Key**
   - Open `.env` file with Notepad
   - Replace `your_openai_api_key_here` with your actual API key
   - Save the file

4. **Start Application**
   - Double-click `run.bat`
   - Application will open in your browser

### Method 2: Manual Setup

1. **Open Command Prompt**
   ```cmd
   # Navigate to project directory
   cd C:\AgenticRAG
   ```

2. **Create Virtual Environment**
   ```cmd
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   ```cmd
   venv\Scripts\activate.bat
   ```

4. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```cmd
   copy .env.template .env
   notepad .env
   ```

6. **Run Application**
   ```cmd
   streamlit run app.py
   ```

### Method 3: PowerShell Setup

1. **Open PowerShell as Administrator**
   ```powershell
   # Enable script execution (if needed)
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

   # Navigate to project
   cd C:\AgenticRAG

   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Install dependencies
   pip install -r requirements.txt

   # Configure and run
   Copy-Item .env.template .env
   streamlit run app.py
   ```

## 🔧 Troubleshooting

### Common Windows Issues

#### 1. "Python is not recognized as an internal or external command"

**Cause**: Python not in system PATH

**Solutions**:
- Reinstall Python and check "Add to PATH"
- Manually add Python to PATH:
  1. Search "Environment Variables" in Windows
  2. Click "Environment Variables"
  3. Add Python installation path to PATH

#### 2. Permission Denied Errors

**Cause**: Insufficient permissions

**Solutions**:
- Run Command Prompt as Administrator
- Move project to user directory (Desktop, Documents)
- Change folder permissions:
  ```cmd
  icacls "C:\AgenticRAG" /grant %USERNAME%:F /T
  ```

#### 3. Virtual Environment Activation Fails

**Cause**: PowerShell execution policy

**Solutions**:
- Use Command Prompt instead of PowerShell
- Enable PowerShell scripts:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

#### 4. Package Installation Fails

**Cause**: Network issues or package conflicts

**Solutions**:
- Update pip:
  ```cmd
  python -m pip install --upgrade pip
  ```
- Clear pip cache:
  ```cmd
  pip cache purge
  pip install -r requirements.txt --no-cache-dir
  ```
- Use alternative package source:
  ```cmd
  pip install -r requirements.txt -i https://pypi.org/simple/
  ```

#### 5. Antivirus Blocking Installation

**Cause**: Windows Defender or antivirus software

**Solutions**:
- Add project folder to Windows Defender exclusions
- Temporarily disable real-time protection
- Use Windows Security exclusions:
  1. Open Windows Security
  2. Go to Virus & threat protection
  3. Add exclusion for project folder

#### 6. Port Already in Use

**Cause**: Another application using port 8501

**Solutions**:
- Use different port:
  ```cmd
  streamlit run app.py --server.port 8502
  ```
- Find and kill process:
  ```cmd
  netstat -ano | findstr :8501
  taskkill /PID <process_id> /F
  ```

#### 7. Long Path Issues

**Cause**: Windows path length limitations

**Solutions**:
- Move project to shorter path (e.g., `C:\RAG\`)
- Enable long path support (Windows 10 1607+):
  1. Open Group Policy Editor (gpedit.msc)
  2. Navigate to Computer Configuration > Administrative Templates > System > Filesystem
  3. Enable "Enable Win32 long paths"

## 🔍 Verification Steps

### Check Installation
```cmd
# Verify Python
python --version

# Verify pip
pip --version

# Check virtual environment
venv\Scripts\activate.bat
python -c "import streamlit; print('Streamlit OK')"
python -c "import chromadb; print('ChromaDB OK')"
python -c "import langchain; print('Langchain OK')"
```

### Test Application
1. Start application: `streamlit run app.py`
2. Open browser to `http://localhost:8501`
3. Check all tabs load without errors
4. Test file upload with a small PDF
5. Verify vector store creation in `vector_store` folder

## 📝 Configuration Files

### .env File Format
```
OPENAI_API_KEY=sk-your-actual-api-key-here
LANGCHAIN_API_KEY=your_langchain_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agentic-rag-app
```

### Custom Configuration
Edit `config.py` for advanced settings:
- Vector database path
- Chunk size and overlap
- File size limits
- Supported file formats

## 🚀 Performance Optimization

### Windows-Specific Tips
1. **Use SSD**: Store project on SSD drive
2. **Increase Virtual Memory**: Set appropriate page file size
3. **Windows Defender**: Add project folder to exclusions
4. **Close Background Apps**: Free up RAM for processing
5. **Update Windows**: Ensure latest Windows updates installed

### Hardware Recommendations
- **CPU**: Intel i5/AMD Ryzen 5 or better
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: SSD preferred, 10GB free space
- **Network**: Stable internet for AI model access

## 🆘 Getting Help

### Built-in Diagnostics
- Use Settings tab → System Diagnostics
- Check Platform Information
- Run File Operations Test

### Log Files
- Check console output for error messages
- Streamlit logs available in command prompt
- ChromaDB logs in vector_store directory

### Common Error Messages
- **"ModuleNotFoundError"**: Virtual environment not activated
- **"API key not found"**: Check .env file configuration
- **"Permission denied"**: Run as administrator or check permissions
- **"Port in use"**: Another application using the port

For additional help, check the main README.md troubleshooting section.
