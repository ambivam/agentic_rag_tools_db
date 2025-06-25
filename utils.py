
import os
import sys
import hashlib
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="🤖 Agentic RAG Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_custom_css():
    """Create custom CSS for the application"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #007acc;
        margin: 1rem 0;
    }
    
    .query-section {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .response-section {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .source-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #007acc;
    }
    
    .status-success {
        color: #28a745;
    }
    
    .status-error {
        color: #dc3545;
    }
    
    .status-warning {
        color: #ffc107;
    }
    
    .platform-info {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

def get_file_hash(file_content: bytes) -> str:
    """Generate hash for file content"""
    return hashlib.md5(file_content).hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def display_success_message(message: str):
    """Display success message"""
    st.markdown(f'<div class="status-success">✅ {message}</div>', unsafe_allow_html=True)

def display_error_message(message: str):
    """Display error message with platform-specific hints"""
    error_html = f'<div class="status-error">❌ {message}</div>'
    
    # Add Windows-specific troubleshooting hints for common errors
    if sys.platform.startswith('win'):
        if "permission" in message.lower():
            error_html += '''
            <div style="margin-top: 10px; padding: 10px; background-color: #fff3cd; border-radius: 5px;">
                <strong>Windows Troubleshooting:</strong><br>
                • Try running as administrator<br>
                • Check if file/folder is locked by another program<br>
                • Disable antivirus temporarily if it's blocking file operations
            </div>
            '''
        elif "path" in message.lower() or "directory" in message.lower():
            error_html += '''
            <div style="margin-top: 10px; padding: 10px; background-color: #fff3cd; border-radius: 5px;">
                <strong>Windows Path Issues:</strong><br>
                • Avoid paths with special characters<br>
                • Try using shorter path names<br>
                • Check if path length exceeds Windows limits (260 chars)
            </div>
            '''
    
    st.markdown(error_html, unsafe_allow_html=True)

def display_warning_message(message: str):
    """Display warning message"""
    st.markdown(f'<div class="status-warning">⚠️ {message}</div>', unsafe_allow_html=True)

def create_progress_bar(progress: float, text: str = ""):
    """Create a progress bar with text"""
    progress_bar = st.progress(progress)
    if text:
        st.text(text)
    return progress_bar

def format_sources(sources: List[Dict[str, Any]]) -> str:
    """Format source information for display"""
    if not sources:
        return "No sources available"
    
    formatted_sources = []
    for i, source in enumerate(sources, 1):
        source_text = f"**Source {i}:**\n"
        if 'filename' in source:
            source_text += f"📄 File: {source['filename']}\n"
        if 'page' in source:
            source_text += f"📖 Page: {source['page']}\n"
        if 'content' in source:
            content_preview = source['content'][:200] + "..." if len(source['content']) > 200 else source['content']
            source_text += f"📝 Content: {content_preview}\n"
        formatted_sources.append(source_text)
    
    return "\n---\n".join(formatted_sources)

def validate_file_upload(uploaded_file, max_size: int, supported_formats: List[str]) -> tuple:
    """Validate uploaded file with platform-specific error messages"""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size
    if uploaded_file.size > max_size:
        return False, f"File size exceeds maximum limit of {format_file_size(max_size)}"
    
    # Check file format
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in supported_formats:
        return False, f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"
    
    # Platform-specific file name validation
    if sys.platform.startswith('win'):
        # Check for Windows-invalid characters
        invalid_chars = set('<>:"|?*')
        if any(char in uploaded_file.name for char in invalid_chars):
            return False, f"File name contains invalid characters for Windows: {invalid_chars}"
        
        # Check for reserved names
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                         'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 
                         'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        file_base = uploaded_file.name.split('.')[0].upper()
        if file_base in reserved_names:
            return False, f"File name '{uploaded_file.name}' is reserved in Windows"
    
    return True, "File validation successful"

def get_platform_info() -> Dict[str, str]:
    """Get platform-specific information for troubleshooting"""
    return {
        "Platform": sys.platform,
        "Python Version": sys.version.split()[0],
        "Architecture": sys.platform,
        "Working Directory": str(Path.cwd()),
        "User Home": str(Path.home()),
        "Temp Directory": str(Path(os.environ.get('TEMP', '/tmp'))),
        "Path Separator": os.sep,
        "Line Separator": repr(os.linesep)
    }

def display_platform_info():
    """Display platform information in a formatted way"""
    info = get_platform_info()
    info_text = "\n".join([f"{key}: {value}" for key, value in info.items()])
    st.markdown(f'<div class="platform-info">{info_text}</div>', unsafe_allow_html=True)

def check_system_requirements() -> Dict[str, bool]:
    """Check system requirements and return status"""
    requirements = {
        "Python 3.11+": sys.version_info >= (3, 11),
        "Sufficient disk space": True,  # TODO: Implement disk space check
        "Write permissions": True,  # TODO: Implement permission check
    }
    
    # Platform-specific checks
    if sys.platform.startswith('win'):
        requirements["Windows 10+"] = True  # Assume true for now
    
    return requirements

def create_sidebar_info():
    """Create sidebar with application information"""
    with st.sidebar:
        st.markdown("## 🤖 Agentic RAG Assistant")
        st.markdown("---")
        
        st.markdown("### 📋 Features")
        st.markdown("""
        - 🔄 **Agentic Workflows**: Multi-step reasoning
        - 📚 **Multi-format Support**: PDF, Word, Excel, PPT, etc.
        - 🧠 **Smart Chunking**: Intelligent document processing
        - 🔍 **Vector Search**: ChromaDB-powered similarity search
        - 📖 **Source Attribution**: Detailed citations
        - 🎯 **Query Planning**: Strategic question decomposition
        """)
        
        st.markdown("### 📁 Supported Formats")
        st.markdown("""
        - 📄 **Documents**: PDF, DOCX, TXT
        - 📊 **Spreadsheets**: XLSX, CSV
        - 🎨 **Presentations**: PPTX
        - 🌐 **Web**: HTML, XML
        - 💾 **Data**: JSON
        """)
        
        st.markdown("### ⚙️ Configuration")
        st.markdown("""
        - **Model**: GPT-4 Turbo
        - **Embeddings**: text-embedding-3-small
        - **Vector DB**: ChromaDB (Local)
        - **Chunk Size**: 1000 tokens
        """)
        
        # Platform information
        st.markdown("### 💻 System Info")
        platform_name = "Windows" if sys.platform.startswith('win') else "Linux/macOS"
        st.markdown(f"**Platform**: {platform_name}")
        st.markdown(f"**Python**: {sys.version.split()[0]}")
        
        if st.button("Show Detailed System Info"):
            st.session_state.show_platform_info = True

def create_diagnostic_section():
    """Create a diagnostic section for troubleshooting"""
    with st.expander("🔧 System Diagnostics"):
        st.markdown("### Platform Information")
        display_platform_info()
        
        st.markdown("### System Requirements")
        requirements = check_system_requirements()
        for req, status in requirements.items():
            icon = "✅" if status else "❌"
            st.markdown(f"{icon} {req}")
        
        if st.button("Test File Operations"):
            test_file_operations()

def test_file_operations():
    """Test basic file operations for troubleshooting"""
    try:
        # Test directory creation
        test_dir = Path("test_temp_dir")
        test_dir.mkdir(exist_ok=True)
        
        # Test file write
        test_file = test_dir / "test.txt"
        test_file.write_text("Test content", encoding='utf-8')
        
        # Test file read
        content = test_file.read_text(encoding='utf-8')
        
        # Cleanup
        test_file.unlink()
        test_dir.rmdir()
        
        display_success_message("File operations test passed")
        
    except Exception as e:
        display_error_message(f"File operations test failed: {str(e)}")
