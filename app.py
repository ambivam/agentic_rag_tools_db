
from utils import setup_page_config
setup_page_config()  # Must be the first Streamlit command

import streamlit as st
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import custom modules
from config import Config
from utils import (
    create_custom_css, create_sidebar_info,
    display_success_message, display_error_message, display_warning_message,
    validate_file_upload, format_sources, format_file_size,
    create_diagnostic_section, get_platform_info
)
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from enhanced_agentic_workflow import EnhancedAgenticWorkflow
from tools.calculator_tool import CalculatorTool
from tools.search_tool import InternetSearchTool
from tools.database_tools import MySQLTool, MongoDBTool, test_database_connections, MYSQL_AVAILABLE, MONGODB_AVAILABLE

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'documents_processed' not in st.session_state:
        st.session_state.documents_processed = []
    
    if 'vector_store_initialized' not in st.session_state:
        st.session_state.vector_store_initialized = False
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}
    
    if 'show_platform_info' not in st.session_state:
        st.session_state.show_platform_info = False

def check_system_compatibility():
    """Check system compatibility and show warnings if needed"""
    try:
        # Ensure directories exist
        Config.ensure_directories()
        
        # Check Python version
        if sys.version_info < (3, 11):
            st.error(f"⚠️ Python 3.11+ required. Current version: {sys.version.split()[0]}")
            st.stop()
        
        # Platform-specific checks
        if Config.IS_WINDOWS:
            try:
                # Test file operations on Windows
                test_path = Path(Config.VECTOR_DB_PATH) / "test_write.tmp"
                test_path.write_text("test", encoding='utf-8')
                test_path.unlink()
            except PermissionError:
                st.error("❌ Permission error detected. Try running as administrator or moving the project to a different folder.")
                st.info("💡 Windows Tip: Move project to Desktop or Documents folder, or run Command Prompt as Administrator")
            except Exception as e:
                st.warning(f"⚠️ File system test failed: {str(e)}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ System compatibility check failed: {str(e)}")
        if Config.IS_WINDOWS:
            st.info("""
            🪟 **Windows Troubleshooting:**
            1. Run Command Prompt as Administrator
            2. Move project to a simpler path (e.g., C:\\AgenticRAG\\)
            3. Check antivirus software isn't blocking the application
            4. Ensure sufficient disk space is available
            """)
        return False

def main():
    """Main application function"""
    
    # Setup custom CSS
    create_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Check system compatibility
    if not check_system_compatibility():
        st.stop()
    
    # Create sidebar
    create_sidebar_info()
    
    # Show platform info if requested
    if st.session_state.get('show_platform_info', False):
        with st.sidebar:
            st.markdown("### 🔍 Detailed System Info")
            platform_info = get_platform_info()
            for key, value in platform_info.items():
                st.text(f"{key}: {value}")
            if st.button("Hide System Info"):
                st.session_state.show_platform_info = False
                st.experimental_rerun()
    
    # Main header
    st.markdown('<h1 class="main-header">🤖 Agentic RAG Assistant</h1>', unsafe_allow_html=True)
    
    # Platform indicator
    platform_emoji = "🪟" if Config.IS_WINDOWS else "🐧" if Config.IS_LINUX else "🍎"
    platform_name = "Windows" if Config.IS_WINDOWS else "Linux" if Config.IS_LINUX else "macOS"
    st.markdown(f"<div style='text-align: center; margin-bottom: 1rem;'>{platform_emoji} Running on {platform_name}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check OpenAI API key
    if not Config.OPENAI_API_KEY:
        st.error("🔑 Please set your OPENAI_API_KEY in the environment variables or .env file")
        
        # Platform-specific instructions
        if Config.IS_WINDOWS:
            st.info("""
            **Windows Setup:**
            1. Create/edit `.env` file in the project folder
            2. Add: `OPENAI_API_KEY=your_api_key_here`
            3. Restart the application using `run.bat`
            """)
        else:
            st.info("""
            **Linux/macOS Setup:**
            1. Create/edit `.env` file: `nano .env`
            2. Add: `OPENAI_API_KEY=your_api_key_here`
            3. Restart: `streamlit run app.py`
            """)
        
        # Show .env template
        if Path('.env.template').exists():
            with st.expander("📝 View .env Template"):
                template_content = Path('.env.template').read_text()
                st.code(template_content, language='bash')
        
        st.stop()
    
    try:
        # Initialize components
        doc_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        vector_store_manager = VectorStoreManager(
            openai_api_key=Config.OPENAI_API_KEY,
            vector_db_path=Config.VECTOR_DB_PATH
        )
        
        enhanced_workflow = EnhancedAgenticWorkflow(
            openai_api_key=Config.OPENAI_API_KEY,
            vector_store_manager=vector_store_manager,
            search_config=Config.SEARCH_CONFIG,
            database_configs=Config.DATABASE_CONFIGS
        )
        
        # Check if vector store is initialized
        store_info = vector_store_manager.get_store_info()
        if store_info.get("initialized", False):
            st.session_state.vector_store_initialized = True
        
        # Create main tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📁 Document Upload", 
            "🔍 Enhanced Query Interface", 
            "🧮 Calculator Tool",
            "🌐 Search Tool",
            "🗄️ Database Tools",
            "📊 Knowledge Base", 
            "⚙️ Settings",
            "🔧 Diagnostics"
        ])
        
        with tab1:
            handle_document_upload(doc_processor, vector_store_manager)
        
        with tab2:
            handle_enhanced_query_interface(enhanced_workflow, vector_store_manager)
        
        with tab3:
            handle_calculator_tool()
            
        with tab4:
            handle_search_tool()
            
        with tab5:
            handle_database_tools()
        
        with tab6:
            handle_knowledge_base(vector_store_manager)
        
        with tab7:
            handle_settings(vector_store_manager)
            
        with tab8:
            handle_diagnostics()
    
    except Exception as e:
        st.error(f"Application initialization error: {str(e)}")
        
        # Platform-specific error guidance
        if Config.IS_WINDOWS:
            st.info("""
            **Windows Troubleshooting:**
            1. Try running as Administrator
            2. Check antivirus software settings
            3. Verify all dependencies are installed: `pip install -r requirements.txt`
            4. Check the Diagnostics tab for more information
            """)
        else:
            st.info("""
            **Linux/macOS Troubleshooting:**
            1. Check virtual environment: `source venv/bin/activate`
            2. Verify dependencies: `pip install -r requirements.txt`
            3. Check file permissions: `ls -la`
            """)

def handle_diagnostics():
    """Handle diagnostics and troubleshooting interface"""
    st.subheader("🔧 System Diagnostics")
    
    # System Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💻 Platform Information")
        platform_info = get_platform_info()
        for key, value in platform_info.items():
            st.text(f"{key}: {value}")
    
    with col2:
        st.markdown("### 📊 Application Status")
        st.text(f"Config Path: {Config.VECTOR_DB_PATH}")
        st.text(f"Python Path: {sys.executable}")
        st.text(f"Working Dir: {Path.cwd()}")
        st.text(f"App Directory: {Path(__file__).parent}")
    
    # File Operations Test
    st.markdown("### 🧪 File Operations Test")
    if st.button("Test File Operations"):
        try:
            # Test directory creation
            test_dir = Path("test_diagnostics")
            test_dir.mkdir(exist_ok=True)
            
            # Test file write/read
            test_file = test_dir / "test.txt"
            test_content = "Diagnostic test content"
            test_file.write_text(test_content, encoding='utf-8')
            
            # Test file read
            read_content = test_file.read_text(encoding='utf-8')
            
            # Cleanup
            test_file.unlink()
            test_dir.rmdir()
            
            if read_content == test_content:
                display_success_message("✅ File operations test passed")
            else:
                display_error_message("❌ File content mismatch")
                
        except Exception as e:
            display_error_message(f"❌ File operations test failed: {str(e)}")
    
    # ChromaDB Test
    st.markdown("### 🗃️ ChromaDB Test")
    if st.button("Test ChromaDB Connection"):
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Test ChromaDB initialization
            client = chromadb.PersistentClient(
                path=str(Path(Config.VECTOR_DB_PATH) / "diagnostic_test"),
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
            
            # Test collection creation
            collection = client.create_collection(
                name="diagnostic_test",
                metadata={"test": "true"}
            )
            
            # Cleanup
            client.delete_collection("diagnostic_test")
            
            display_success_message("✅ ChromaDB connection test passed")
            
        except Exception as e:
            display_error_message(f"❌ ChromaDB test failed: {str(e)}")
    
    # Environment Variables
    st.markdown("### 🔐 Environment Variables")
    env_vars = {
        "OPENAI_API_KEY": "✅ Set" if Config.OPENAI_API_KEY else "❌ Not Set",
        "LANGCHAIN_API_KEY": "✅ Set" if Config.LANGCHAIN_API_KEY else "❌ Not Set (Optional)",
        "PATH": "✅ Available" if os.getenv('PATH') else "❌ Missing"
    }
    
    for var, status in env_vars.items():
        st.text(f"{var}: {status}")
    
    # Dependency Check
    st.markdown("### 📦 Dependency Check")
    if st.button("Check Dependencies"):
        dependencies = [
            'streamlit', 'langchain', 'langgraph', 'openai', 
            'chromadb', 'python-dotenv', 'pypdf', 'python-docx'
        ]
        
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                st.text(f"✅ {dep}")
            except ImportError:
                st.text(f"❌ {dep} - Missing")

# [Previous functions remain the same...]
def handle_document_upload(doc_processor: DocumentProcessor, vector_store_manager: VectorStoreManager):
    """Handle document upload interface"""
    
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📁 Upload Documents")
    st.markdown("Upload your documents to build the knowledge base. Supported formats: PDF, DOCX, TXT, CSV, XLSX, PPTX, JSON, HTML, XML")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose files",
        type=Config.SUPPORTED_FORMATS,
        accept_multiple_files=True,
        help=f"Maximum file size: {format_file_size(Config.MAX_FILE_SIZE)}"
    )
    
    if uploaded_files:
        st.write(f"📄 {len(uploaded_files)} file(s) selected")
        
        # Display file information
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📎 {file.name}")
            with col2:
                st.write(f"{format_file_size(file.size)}")
            with col3:
                st.write(f".{file.name.split('.')[-1].upper()}")
        
        # Process files button
        if st.button("🚀 Process Documents", type="primary"):
            process_documents(uploaded_files, doc_processor, vector_store_manager)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display processing status
    if st.session_state.documents_processed:
        st.subheader("📋 Processing History")
        for doc_info in st.session_state.documents_processed[-5:]:  # Show last 5
            with st.expander(f"✅ {doc_info['filename']} - {doc_info['timestamp']}"):
                st.write(f"📊 Chunks created: {doc_info['chunks']}")
                st.write(f"📝 Characters: {doc_info['characters']:,}")
                st.write(f"🔤 Words: {doc_info['words']:,}")

def process_documents(uploaded_files, doc_processor: DocumentProcessor, vector_store_manager: VectorStoreManager):
    """Process uploaded documents"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(uploaded_files)
    all_documents = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        progress_bar.progress((i + 0.5) / total_files)
        
        # Validate file
        is_valid, message = validate_file_upload(
            uploaded_file, 
            Config.MAX_FILE_SIZE, 
            Config.SUPPORTED_FORMATS
        )
        
        if not is_valid:
            display_error_message(f"File {uploaded_file.name}: {message}")
            continue
        
        try:
            # Process document
            documents = doc_processor.process_file(uploaded_file)
            all_documents.extend(documents)
            
            # Store processing info
            doc_info = {
                'filename': uploaded_file.name,
                'chunks': len(documents),
                'characters': sum(len(doc.page_content) for doc in documents),
                'words': sum(len(doc.page_content.split()) for doc in documents),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.documents_processed.append(doc_info)
            
            display_success_message(f"Processed {uploaded_file.name}: {len(documents)} chunks created")
            
        except Exception as e:
            display_error_message(f"Error processing {uploaded_file.name}: {str(e)}")
        
        progress_bar.progress((i + 1) / total_files)
    
    # Add to vector store
    if all_documents:
        status_text.text("Adding documents to vector store...")
        success = vector_store_manager.add_documents(all_documents, show_progress=False)
        
        if success:
            st.session_state.vector_store_initialized = True
            display_success_message(f"Successfully added {len(all_documents)} document chunks to knowledge base!")
        else:
            display_error_message("Failed to add documents to vector store")
    
    progress_bar.progress(1.0)
    status_text.text("Processing complete!")
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()

from agentic_workflow import AgenticWorkflow

def handle_query_interface(agentic_workflow: AgenticWorkflow, vector_store_manager: VectorStoreManager):
    """Handle query interface"""
    
    st.markdown('<div class="query-section">', unsafe_allow_html=True)
    st.subheader("🔍 Ask Questions")
    
    # Check if vector store is initialized
    if not st.session_state.vector_store_initialized:
        st.warning("📚 Please upload and process documents first before asking questions.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Query input
    query = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="Ask anything about your uploaded documents...",
        help="Ask detailed questions about the content in your documents. The AI will analyze your query and provide comprehensive answers with source citations."
    )
    
    # Query options
    col1, col2 = st.columns([3, 1])
    with col1:
        search_depth = st.selectbox(
            "Search Depth:",
            options=["Standard", "Deep", "Comprehensive"],
            help="Standard: 5 sources, Deep: 8 sources, Comprehensive: 12 sources"
        )
    
    with col2:
        if st.button("🔍 Ask Question", type="primary"):
            if query.strip():
                process_query(query, agentic_workflow, search_depth)
            else:
                display_warning_message("Please enter a question")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💬 Chat History")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.expander(f"Q: {chat['query'][:50]}... - {chat['timestamp']}"):
                st.markdown(f"**Question:** {chat['query']}")
                st.markdown(f"**Answer:** {chat['response']}")
                if chat.get('sources'):
                    st.markdown("**Sources:**")
                    for j, source in enumerate(chat['sources'][:3]):  # Show top 3 sources
                        st.markdown(f"- {source.get('filename', 'Unknown')} (Score: {source.get('similarity_score', 0):.3f})")

def process_query(query: str, agentic_workflow: AgenticWorkflow, search_depth: str):
    """Process user query"""
    
    # Show processing status
    with st.spinner("🤖 Analyzing your question and searching through documents..."):
        
        # Determine search parameters
        k_map = {"Standard": 5, "Deep": 8, "Comprehensive": 12}
        
        # Run agentic workflow
        results = agentic_workflow.run_workflow(query)
        
        if results["success"]:
            # Display response
            st.markdown('<div class="response-section">', unsafe_allow_html=True)
            st.subheader("🎯 Answer")
            st.markdown(results["response"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display sources
            if results["sources"]:
                st.subheader("📚 Sources")
                for i, source in enumerate(results["sources"]):
                    with st.expander(f"📄 Source {i+1}: {source.get('filename', 'Unknown')} (Relevance: {source.get('similarity_score', 0):.3f})"):
                        st.markdown(f"**File:** {source.get('filename', 'Unknown')}")
                        st.markdown(f"**Relevance Score:** {source.get('similarity_score', 0):.3f}")
                        st.markdown(f"**Content Preview:**")
                        st.text(source.get('content', 'No content available'))
            
            # Display analysis info
            if results.get("analysis"):
                with st.expander("🔍 Query Analysis Details"):
                    analysis = results["analysis"]
                    if "query_type" in analysis:
                        st.write(f"**Query Type:** {analysis.get('query_type', 'Unknown')}")
                    if "complexity" in analysis:
                        st.write(f"**Complexity:** {analysis.get('complexity', 'Unknown')}")
                    if "search_results_count" in results:
                        st.write(f"**Sources Searched:** {results['search_results_count']}")
            
            # Store in chat history
            chat_entry = {
                'query': query,
                'response': results["response"],
                'sources': results["sources"],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.chat_history.append(chat_entry)
            
            display_success_message("Question answered successfully!")
            
        else:
            display_error_message(f"Error processing query: {results.get('error', 'Unknown error')}")

def handle_knowledge_base(vector_store_manager: VectorStoreManager):
    """Handle knowledge base interface"""
    
    st.subheader("📊 Knowledge Base Status")
    
    # Get store information
    store_info = vector_store_manager.get_store_info()
    
    if store_info.get("initialized", False):
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Total Documents", store_info.get("total_documents", 0))
        
        with col2:
            st.metric("🔢 Total Embeddings", store_info.get("total_embeddings", 0))
        
        with col3:
            st.metric("📁 Unique Files", store_info.get("unique_files", 0))
        
        with col4:
            avg_chunk_size = store_info.get("total_documents", 0)
            st.metric("📋 Avg Chunk Size", f"{Config.CHUNK_SIZE}")
        
        # Display files
        if store_info.get("files"):
            st.subheader("📁 Files in Knowledge Base")
            for file in store_info["files"]:
                st.write(f"📎 {file}")
        
        # Search functionality
        st.subheader("🔍 Search Knowledge Base")
        search_query = st.text_input("Search documents:", placeholder="Enter search terms...")
        
        if search_query:
            with st.spinner("Searching..."):
                results = vector_store_manager.similarity_search(search_query, k=5)
                
                if results:
                    st.write(f"Found {len(results)} relevant documents:")
                    for i, (doc, score) in enumerate(results):
                        with st.expander(f"Result {i+1} - {doc.metadata.get('filename', 'Unknown')} (Score: {score:.3f})"):
                            st.write(f"**Content:**")
                            st.text(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                            st.write(f"**Metadata:** {doc.metadata}")
                else:
                    st.info("No relevant documents found.")
    
    else:
        st.info("📚 Knowledge base is empty. Please upload documents first.")

def handle_settings(vector_store_manager: VectorStoreManager):
    """Handle settings interface"""
    
    st.subheader("⚙️ Application Settings")
    
    # Configuration display
    st.subheader("🔧 Current Configuration")
    
    config_data = {
        "OpenAI Model": Config.OPENAI_MODEL,
        "Embedding Model": Config.OPENAI_EMBEDDING_MODEL,
        "Chunk Size": Config.CHUNK_SIZE,
        "Chunk Overlap": Config.CHUNK_OVERLAP,
        "Max File Size": format_file_size(Config.MAX_FILE_SIZE),
        "Supported Formats": ", ".join(Config.SUPPORTED_FORMATS),
        "Platform": f"{'Windows' if Config.IS_WINDOWS else 'Linux' if Config.IS_LINUX else 'macOS'}",
        "Vector DB Path": Config.VECTOR_DB_PATH
    }
    
    for key, value in config_data.items():
        st.write(f"**{key}:** {value}")
    
    st.markdown("---")
    
    # Danger zone
    st.subheader("⚠️ Danger Zone")
    st.warning("These actions are irreversible!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Knowledge Base", type="secondary"):
            if st.session_state.get('confirm_clear', False):
                success = vector_store_manager.clear_vector_store()
                if success:
                    st.session_state.vector_store_initialized = False
                    st.session_state.documents_processed = []
                    st.session_state.chat_history = []
                    display_success_message("Knowledge base cleared successfully!")
                else:
                    display_error_message("Failed to clear knowledge base")
                st.session_state.confirm_clear = False
            else:
                st.session_state.confirm_clear = True
                st.error("Click again to confirm clearing the knowledge base")
    
    with col2:
        if st.button("🔄 Reset Application", type="secondary"):
            if st.session_state.get('confirm_reset', False):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()
            else:
                st.session_state.confirm_reset = True
                st.error("Click again to confirm resetting the application")
    
    # Environment variables
    st.subheader("🔐 Environment Variables")
    st.write("**OPENAI_API_KEY:** " + ("✅ Set" if Config.OPENAI_API_KEY else "❌ Not Set"))
    st.write("**LANGCHAIN_API_KEY:** " + ("✅ Set" if Config.LANGCHAIN_API_KEY else "❌ Not Set (Optional)"))

def handle_enhanced_query_interface(enhanced_workflow, vector_store_manager):
    """Handle enhanced query interface with multi-agent processing"""
    st.subheader("🔍 Enhanced Multi-Agent Query Interface")
    
    # Check if vector store is ready
    store_info = vector_store_manager.get_store_info()
    if not store_info.get("initialized", False):
        st.warning("⚠️ Please upload and process documents first in the Document Upload tab.")
        return
    
    # Agent status display
    with st.expander("🤖 Agent Status", expanded=False):
        agent_status = enhanced_workflow.get_agent_status()
        
        cols = st.columns(4)
        for i, (agent_name, status) in enumerate(agent_status.items()):
            with cols[i % 4]:
                if status.get('available', False):
                    st.success(f"✅ **{agent_name.title()} Agent**")
                    st.caption(f"Capabilities: {len(status.get('capabilities', []))}")
                else:
                    st.error(f"❌ **{agent_name.title()} Agent**")
                    st.caption(f"Error: {status.get('error', 'Unknown')}")
    
    # Query input
    st.markdown("### Ask Your Question")
    query = st.text_area(
        "Enter your query (supports documents, calculations, web search, database operations):",
        height=100,
        placeholder="Examples:\n- Summarize the main points from the uploaded documents\n- Calculate 15% of 2500 plus convert 5 feet to meters\n- Search for latest AI developments\n- Find information about machine learning in the database"
    )
    
    # Advanced options
    with st.expander("🎛️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            max_agents = st.slider("Max Agents per Query", 1, 4, 3)
            enable_search = st.checkbox("Enable Web Search", value=True)
        with col2:
            enable_database = st.checkbox("Enable Database Query", value=True)
            enable_calculator = st.checkbox("Enable Calculator", value=True)
    
    # Query processing
    if st.button("🚀 Process Query", type="primary", disabled=not query):
        if query:
            with st.spinner("🤖 Processing with multiple agents..."):
                try:
                    # Prepare context
                    context = {
                        'max_agents': max_agents,
                        'enabled_agents': {
                            'search': enable_search,
                            'database': enable_database,
                            'calculator': enable_calculator
                        },
                        'ui_context': 'streamlit_interface'
                    }
                    
                    # Get chat history from session state
                    chat_history = st.session_state.get('chat_history', [])
                    
                    # Process query with enhanced workflow
                    result = enhanced_workflow.run_enhanced_workflow(
                        query=query,
                        chat_history=chat_history,
                        context=context
                    )
                    
                    if result.get('success', False):
                        # Display results
                        st.markdown("### 🎯 Response")
                        st.markdown(result['response'])
                        
                        # Agent execution summary
                        if result.get('active_agents'):
                            st.markdown("### 🤖 Agent Execution Summary")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Active Agents", len(result['active_agents']))
                            with col2:
                                st.metric("Confidence Score", f"{result.get('confidence', 0):.2%}")
                            with col3:
                                st.metric("Sources Found", len(result.get('sources', [])))
                            
                            # Active agents display
                            st.markdown("**Active Agents:**")
                            for agent in result['active_agents']:
                                st.markdown(f"<span style='background-color: #f0f2f6; padding: 0.2rem 0.6rem; border-radius: 0.8rem; font-size: 0.8rem;'>🤖 {agent.title()}</span>", unsafe_allow_html=True)
                        
                        # Sources
                        if result.get('sources'):
                            st.markdown("### 📚 Sources")
                            with st.expander(f"View {len(result['sources'])} Sources"):
                                for i, source in enumerate(result['sources'], 1):
                                    st.markdown(f"**Source {i}** ({source.get('agent', 'Unknown Agent')})")
                                    if 'filename' in source:
                                        st.markdown(f"📄 **File:** {source['filename']}")
                                    if 'content_preview' in source:
                                        st.markdown(f"**Preview:** {source['content_preview'][:200]}...")
                                    if 'relevance_score' in source:
                                        st.progress(source['relevance_score'])
                                    st.markdown("---")
                        
                        # Agent responses detail
                        if result.get('agent_responses'):
                            with st.expander("🔍 Detailed Agent Responses"):
                                for agent_name, agent_response in result['agent_responses'].items():
                                    if agent_response.get('success', False):
                                        st.success(f"✅ **{agent_name.title()} Agent**")
                                        if 'message' in agent_response:
                                            st.markdown(f"**Message:** {agent_response['message']}")
                                        if 'confidence' in agent_response:
                                            st.markdown(f"**Confidence:** {agent_response['confidence']:.2%}")
                                    else:
                                        st.error(f"❌ **{agent_name.title()} Agent**")
                                        st.markdown(f"**Error:** {agent_response.get('error', 'Unknown error')}")
                                    st.markdown("---")
                        
                        # Update chat history
                        if 'chat_history' not in st.session_state:
                            st.session_state.chat_history = []
                        
                        st.session_state.chat_history.append({
                            'query': query,
                            'response': result['response'],
                            'timestamp': datetime.now().isoformat(),
                            'agents_used': result.get('active_agents', []),
                            'confidence': result.get('confidence', 0)
                        })
                        
                        display_success_message("✅ Query processed successfully!")
                        
                    else:
                        st.error(f"❌ Query processing failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
    
    # Chat history
    if st.session_state.get('chat_history'):
        st.markdown("### 💬 Recent Queries")
        with st.expander(f"View {len(st.session_state.chat_history)} Recent Queries"):
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
                st.markdown(f"**Query {i}:** {chat['query'][:100]}...")
                st.markdown(f"**Agents:** {', '.join(chat.get('agents_used', []))}")
                st.markdown(f"**Confidence:** {chat.get('confidence', 0):.2%}")
                st.markdown("---")

def handle_calculator_tool():
    """Handle calculator tool interface"""
    st.subheader("🧮 Calculator Tool")
    
    try:
        calculator = CalculatorTool()
        
        # Display supported functions
        with st.expander("📖 Supported Functions"):
            functions = calculator.get_supported_functions()
            for func in functions:
                st.markdown(f"• {func}")
        
        # Calculator input
        st.markdown("### Calculator Input")
        calc_input = st.text_area(
            "Enter mathematical expression or word problem:",
            height=100,
            placeholder="Examples:\n- 15 * 25 + sqrt(144)\n- convert 5 feet to meters\n- sin(45 degrees)\n- Calculate 15% tip on $125"
        )
        
        col1, col2 = st.columns(2)
        
        if col1.button("🧮 Calculate", type="primary", disabled=not calc_input):
            if calc_input:
                with st.spinner("Calculating..."):
                    result = calculator.calculate(calc_input)
                    
                    if result.get('success', False):
                        st.markdown("### 🎯 Result")
                        
                        # Display formatted result
                        formatted_result = result.get('formatted_result', str(result.get('result', 'No result')))
                        st.success(f"**Result:** {formatted_result}")
                        
                        # Display calculation details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Calculation Type", result.get('type', 'Unknown'))
                        with col2:
                            if isinstance(result.get('result'), dict) and 'value' in result['result']:
                                st.metric("Numeric Value", f"{result['result']['value']:.6g}")
                            elif isinstance(result.get('result'), (int, float)):
                                st.metric("Numeric Value", f"{result['result']:.6g}")
                        
                        # Additional details for unit conversions
                        if result.get('type') == 'unit_conversion' and isinstance(result.get('result'), dict):
                            st.markdown("### 🔄 Conversion Details")
                            conv_result = result['result']
                            st.markdown(f"**From:** {conv_result.get('original_value')} {conv_result.get('from_unit')}")
                            st.markdown(f"**To:** {conv_result.get('value'):.6g} {conv_result.get('to_unit')}")
                            st.markdown(f"**Category:** {conv_result.get('category', 'Unknown')}")
                        
                    else:
                        st.error(f"❌ Calculation failed: {result.get('error', 'Unknown error')}")
        
        if col2.button("🗑️ Clear"):
            st.rerun()
        
        # Example calculations
        st.markdown("### 📝 Example Calculations")
        examples = [
            "25 * 4 + 100",
            "sqrt(16) + sin(30)",
            "convert 100 fahrenheit to celsius",
            "15% of 250",
            "log(1000)"
        ]
        
        selected_example = st.selectbox("Choose an example:", [""] + examples)
        if selected_example and st.button("Use Example"):
            st.session_state.example_calc = selected_example
            st.rerun()
        
    except Exception as e:
        st.error(f"❌ Calculator tool error: {str(e)}")

def handle_search_tool():
    """Handle search tool interface"""
    st.subheader("🌐 Internet Search Tool")
    
    try:
        search_tool = InternetSearchTool(Config.SEARCH_CONFIG)
        
        # Display supported features
        with st.expander("🔍 Search Features"):
            features = search_tool.get_supported_features()
            for feature in features:
                st.markdown(f"• {feature}")
        
        # Search configuration
        with st.expander("⚙️ Search Configuration"):
            col1, col2 = st.columns(2)
            with col1:
                num_results = st.slider("Number of Results", 1, 20, 5)
                provider = st.selectbox("Search Provider", ["auto", "duckduckgo", "serpapi", "fallback"])
            with col2:
                st.markdown("**API Keys Status:**")
                if Config.SEARCH_CONFIG.get('serpapi_key'):
                    st.success("✅ SerpAPI Key Available")
                else:
                    st.warning("⚠️ SerpAPI Key Not Set")
        
        # Search input
        st.markdown("### Search Query")
        search_query = st.text_area(
            "Enter your search query:",
            height=80,
            placeholder="Examples:\n- Latest developments in artificial intelligence\n- Python programming best practices\n- Climate change research 2024"
        )
        
        if st.button("🔍 Search", type="primary", disabled=not search_query):
            if search_query:
                with st.spinner("Searching the internet..."):
                    search_results = search_tool.search(
                        query=search_query,
                        num_results=num_results,
                        provider=provider
                    )
                    
                    if search_results.get('success', False):
                        results = search_results.get('results', [])
                        
                        st.markdown("### 🎯 Search Results")
                        
                        # Search summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Results Found", len(results))
                        with col2:
                            st.metric("Provider Used", search_results.get('provider', 'Unknown'))
                        with col3:
                            avg_relevance = sum(r.get('relevance_score', 0) for r in results) / len(results) if results else 0
                            st.metric("Avg Relevance", f"{avg_relevance:.2f}")
                        
                        # Display results
                        for i, result in enumerate(results, 1):
                            with st.expander(f"📄 Result {i}: {result.get('title', 'No Title')[:80]}..."):
                                st.markdown(f"**Source:** {result.get('source', 'Unknown')}")
                                st.markdown(f"**URL:** {result.get('url', 'No URL')}")
                                st.markdown(f"**Type:** {result.get('type', 'Unknown')}")
                                
                                if result.get('snippet'):
                                    st.markdown("**Content:**")
                                    st.markdown(result['snippet'])
                                
                                # Metadata
                                metadata = result.get('metadata', {})
                                if metadata:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"**Relevance:** {result.get('relevance_score', 0):.3f}")
                                    with col2:
                                        st.markdown(f"**Confidence:** {metadata.get('confidence', 0):.3f}")
                        
                        # Store results in session state
                        st.session_state.search_results = results
                        st.session_state.search_query = search_query
                    
                    else:
                        st.error(f"❌ Search failed: {search_results.get('error', 'Unknown error')}")
            
        # Generate summary (outside the search button block)
        if 'search_results' in st.session_state and st.session_state.search_results:
            if st.button("📋 Generate Summary"):
                with st.spinner("Generating summary..."):
                    summary = search_tool.summarize_results(
                        st.session_state.search_results,
                        st.session_state.search_query
                    )
                    
                    st.markdown("### 📝 Search Summary")
                    st.markdown(summary.get('summary', 'No summary available'))
                    
                    if summary.get('key_points'):
                        st.markdown("**Key Points:**")
                        for point in summary['key_points'][:5]:
                            st.markdown(f"• {point.get('text', '')}")
                    
                    else:
                        st.error(f"❌ Search failed: {search_results.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Search tool error: {str(e)}")

def handle_database_tools():
    """Handle database tools interface"""
    st.subheader("🗄️ Database Tools")
    
    # Database availability check
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🐬 MySQL")
        if MYSQL_AVAILABLE:
            st.success("✅ MySQL Support Available")
        else:
            st.error("❌ MySQL Support Not Available")
            st.markdown("Install with: `pip install mysql-connector-python`")
    
    with col2:
        st.markdown("### 🍃 MongoDB")
        if MONGODB_AVAILABLE:
            st.success("✅ MongoDB Support Available")
        else:
            st.error("❌ MongoDB Support Not Available")
            st.markdown("Install with: `pip install pymongo`")
    
    # Database configuration
    st.markdown("### ⚙️ Database Configuration")
    
    db_tab1, db_tab2 = st.tabs(["MySQL Config", "MongoDB Config"])
    
    with db_tab1:
        if MYSQL_AVAILABLE:
            st.markdown("**MySQL Connection Settings:**")
            mysql_config = {
                'host': st.text_input("Host", value=Config.DATABASE_CONFIGS['mysql']['host']),
                'port': st.number_input("Port", value=Config.DATABASE_CONFIGS['mysql']['port']),
                'user': st.text_input("Username", value=Config.DATABASE_CONFIGS['mysql']['user']),
                'password': st.text_input("Password", type="password"),
                'database': st.text_input("Database", value=Config.DATABASE_CONFIGS['mysql']['database'])
            }
            
            if st.button("🔌 Test MySQL Connection"):
                if mysql_config['password']:  # Only test if password provided
                    with st.spinner("Testing MySQL connection..."):
                        try:
                            mysql_tool = MySQLTool(mysql_config)
                            result = mysql_tool.connect()
                            
                            if result['success']:
                                st.success(f"✅ Connected to MySQL: {result['server_version']}")
                                mysql_tool.disconnect()
                            else:
                                st.error(f"❌ Connection failed: {result['error']}")
                        except Exception as e:
                            st.error(f"❌ Connection error: {str(e)}")
                else:
                    st.warning("Please enter database password to test connection")
        else:
            st.info("MySQL support not available. Install the required package to use MySQL features.")
    
    with db_tab2:
        if MONGODB_AVAILABLE:
            st.markdown("**MongoDB Connection Settings:**")
            mongodb_config = {
                'host': st.text_input("Host", value=Config.DATABASE_CONFIGS['mongodb']['host'], key="mongo_host"),
                'port': st.number_input("Port", value=Config.DATABASE_CONFIGS['mongodb']['port'], key="mongo_port"),
                'username': st.text_input("Username", value=Config.DATABASE_CONFIGS['mongodb'].get('username', ''), key="mongo_user"),
                'password': st.text_input("Password", type="password", key="mongo_pass"),
                'database': st.text_input("Database", value=Config.DATABASE_CONFIGS['mongodb']['database'], key="mongo_db")
            }
            
            if st.button("🔌 Test MongoDB Connection"):
                with st.spinner("Testing MongoDB connection..."):
                    try:
                        mongodb_tool = MongoDBTool(mongodb_config)
                        result = mongodb_tool.connect()
                        
                        if result['success']:
                            st.success(f"✅ Connected to MongoDB: {result['server_version']}")
                            mongodb_tool.disconnect()
                        else:
                            st.error(f"❌ Connection failed: {result['error']}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
        else:
            st.info("MongoDB support not available. Install the required package to use MongoDB features.")
    
    # Database operations
    if MYSQL_AVAILABLE or MONGODB_AVAILABLE:
        st.markdown("### 💾 Database Operations")
        
        db_operation = st.selectbox(
            "Choose Operation:",
            ["Select Data", "Insert Data", "Update Data", "Delete Data", "Show Tables/Collections"]
        )
        
        if db_operation == "Select Data":
            col1, col2 = st.columns(2)
            with col1:
                table_name = st.text_input("Table/Collection Name", placeholder="users")
            with col2:
                limit = st.number_input("Limit Results", min_value=1, max_value=100, value=10)
            
            query_filter = st.text_area(
                "Query Filter (JSON for MongoDB, WHERE clause for MySQL):",
                placeholder='{"status": "active"} or WHERE status = "active"'
            )
            
            if st.button("📊 Execute Query"):
                st.info("Database query execution would be implemented here with proper connection handling.")
        
        elif db_operation == "Show Tables/Collections":
            if st.button("📋 Show Database Structure"):
                st.info("Database structure display would be implemented here.")
    
    # Sample queries
    st.markdown("### 📝 Sample Queries")
    with st.expander("View Sample Database Queries"):
        st.markdown("""
        **MySQL Examples:**
        - `SELECT * FROM users LIMIT 10`
        - `SELECT name, email FROM customers WHERE status = 'active'`
        - `INSERT INTO products (name, price) VALUES ('Laptop', 999.99)`
        
        **MongoDB Examples:**
        - Find all: `{}`
        - Filter: `{"status": "active", "age": {"$gte": 18}}`
        - Insert: `{"name": "John", "email": "john@example.com"}`
        """)

if __name__ == "__main__":
    main()
