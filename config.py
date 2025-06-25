
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the Enhanced Agentic RAG application"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = "https://api.openai.com/v1"
    OPENAI_MODEL = "gpt-4-1106-preview"
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Langchain Configuration
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "enhanced-agentic-rag-app")
    
    # Vector Database Configuration - Cross-platform path handling
    VECTOR_DB_PATH = str(Path(__file__).parent / "vector_store")
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Search Tool Configuration
    SEARCH_CONFIG = {
        'serpapi_key': os.getenv("SERPAPI_API_KEY"),
        'google_api_key': os.getenv("GOOGLE_API_KEY"),
        'google_cse_id': os.getenv("GOOGLE_CSE_ID"),
        'default_provider': 'duckduckgo',
        'max_results': 10,
        'timeout': 10
    }
    
    # Database Configuration
    DATABASE_CONFIGS = {
        'mysql': {
            'host': os.getenv("MYSQL_HOST", "localhost"),
            'port': int(os.getenv("MYSQL_PORT", "3306")),
            'user': os.getenv("MYSQL_USER", "root"),
            'password': os.getenv("MYSQL_PASSWORD", ""),
            'database': os.getenv("MYSQL_DATABASE", ""),
            'charset': 'utf8mb4',
            'autocommit': True,
            'pool_name': 'agentic_rag_pool',
            'pool_size': 5
        },
        'mongodb': {
            'host': os.getenv("MONGODB_HOST", "localhost"),
            'port': int(os.getenv("MONGODB_PORT", "27017")),
            'username': os.getenv("MONGODB_USERNAME"),
            'password': os.getenv("MONGODB_PASSWORD"),
            'database': os.getenv("MONGODB_DATABASE", "agentic_rag"),
            'auth_source': os.getenv("MONGODB_AUTH_SOURCE", "admin"),
            'connection_timeout': 10000,
            'server_selection_timeout': 5000
        }
    }
    
    # Agent Configuration
    AGENT_CONFIG = {
        'enable_calculator': os.getenv("ENABLE_CALCULATOR", "true").lower() == "true",
        'enable_search': os.getenv("ENABLE_SEARCH", "true").lower() == "true", 
        'enable_database': os.getenv("ENABLE_DATABASE", "true").lower() == "true",
        'enable_rag': os.getenv("ENABLE_RAG", "true").lower() == "true",
        'coordination_strategy': os.getenv("COORDINATION_STRATEGY", "auto"),
        'max_agents_per_query': int(os.getenv("MAX_AGENTS_PER_QUERY", "4"))
    }
    
    # File Upload Configuration
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    SUPPORTED_FORMATS = [
        "pdf", "docx", "txt", "csv", "xlsx", "pptx", 
        "json", "html", "xml", "doc", "xls", "ppt"
    ]
    
    # UI Configuration
    PAGE_TITLE = "🤖 Enhanced Agentic RAG Assistant"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    
    # Platform-specific configurations
    IS_WINDOWS = sys.platform.startswith('win')
    IS_LINUX = sys.platform.startswith('linux')
    IS_MACOS = sys.platform.startswith('darwin')
    
    @classmethod
    def get_data_directory(cls) -> Path:
        """Get platform-appropriate data directory"""
        if cls.IS_WINDOWS:
            # Use %APPDATA% on Windows
            base_dir = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            return base_dir / 'AgenticRAG'
        else:
            # Use ~/.local/share on Linux/macOS
            base_dir = Path.home() / '.local' / 'share'
            return base_dir / 'agentic-rag'
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist with proper permissions"""
        try:
            # Create vector store directory
            vector_path = Path(cls.VECTOR_DB_PATH)
            vector_path.mkdir(parents=True, exist_ok=True)
            
            # Create data directory
            data_dir = cls.get_data_directory()
            data_dir.mkdir(parents=True, exist_ok=True)
            
            return True
        except PermissionError as e:
            if cls.IS_WINDOWS:
                raise PermissionError(
                    f"Permission denied creating directories. Try running as administrator or "
                    f"check folder permissions: {str(e)}"
                )
            else:
                raise PermissionError(f"Permission denied creating directories: {str(e)}")
        except Exception as e:
            raise Exception(f"Error creating directories: {str(e)}")
    
    @classmethod
    def validate_openai_key(cls):
        """Validate OpenAI API key is set"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        return True
    
    @classmethod
    def get_platform_info(cls) -> dict:
        """Get platform-specific information"""
        return {
            "platform": sys.platform,
            "is_windows": cls.IS_WINDOWS,
            "is_linux": cls.IS_LINUX,
            "is_macos": cls.IS_MACOS,
            "python_version": sys.version,
            "vector_db_path": cls.VECTOR_DB_PATH,
            "data_directory": str(cls.get_data_directory())
        }
