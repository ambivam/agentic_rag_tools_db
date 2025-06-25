# 🤖 Enhanced Agentic RAG Assistant

A sophisticated **multi-agent AI system** that combines Retrieval-Augmented Generation (RAG) with specialized agents for **mathematical calculations**, **web search**, **database operations**, and **document analysis**. Built with cutting-edge technologies including Langchain, Langgraph, OpenAI GPT-4, FAISS vector database, and Streamlit.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## 📋 Table of Contents

- [🌟 Key Features](#-key-features)
- [🏗️ Technology Stack](#️-technology-stack)
- [🚀 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [📖 Usage Guide](#-usage-guide)
- [🤖 Multi-Agent Architecture](#-multi-agent-architecture)
- [🛠️ Advanced Tools](#️-advanced-tools)
- [📄 File Format Support](#-file-format-support)
- [🔌 API Integration](#-api-integration)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

## 🌟 Key Features

### 🤖 Multi-Agent Intelligence System
- **Calculator Agent**: Advanced mathematical operations, unit conversions, formula evaluation
- **Search Agent**: Real-time web search with multiple providers (DuckDuckGo, SerpAPI, Google)
- **Database Agent**: MySQL and MongoDB operations with intelligent query generation
- **RAG Agent**: Enhanced document-based question answering with improved context synthesis
- **Coordinator Agent**: Smart agent orchestration and task distribution

### 🔄 Advanced Agentic Workflows
- **Multi-Agent Coordination**: Intelligent routing of queries to appropriate specialized agents
- **Parallel Processing**: Simultaneous execution of multiple agents for complex queries
- **Context Integration**: Seamless synthesis of results from different agent types
- **Confidence Scoring**: Advanced quality metrics and reliability assessment
- **Dynamic Planning**: Adaptive query analysis and execution strategy optimization

### 🧮 Calculator Tool Capabilities
- **Basic Arithmetic**: Addition, subtraction, multiplication, division, exponents
- **Advanced Functions**: Square root, trigonometry, logarithms, factorial
- **Unit Conversions**: Length, weight, temperature, volume conversions
- **Mathematical Constants**: Pi, e, tau with high precision calculations
- **Word Problems**: Natural language mathematical problem solving

### 🌐 Internet Search Integration
- **Multiple Providers**: DuckDuckGo (default), SerpAPI, Google Custom Search
- **Real-time Results**: Current information retrieval and analysis
- **Result Ranking**: Intelligent relevance scoring and source verification
- **Summary Generation**: Automatic synthesis of search results
- **Source Attribution**: Detailed citation and credibility assessment

### 🗄️ Database Operations
- **MySQL Support**: Full CRUD operations with intelligent SQL generation
- **MongoDB Integration**: Document operations with NoSQL query optimization
- **Connection Management**: Secure connection pooling and error handling
- **Schema Analysis**: Automatic table/collection structure discovery
- **Query Optimization**: AI-powered query generation and validation

### 📚 Enhanced Document Support
- **PDF Documents**: Full text extraction with page attribution
- **Microsoft Office**: Word (DOCX), Excel (XLSX), PowerPoint (PPTX)
- **Text Files**: Plain text, CSV, JSON
- **Web Formats**: HTML, XML
- **Legacy Formats**: DOC, XLS, PPT

### 🎯 Advanced Features
- **FAISS Vector Database**: High-performance similarity search and clustering
- **Cross-Platform Support**: Windows, Linux, and macOS compatibility
- **Streamlit UI**: Interactive web interface with 8 comprehensive tabs
- **Real-time Processing**: Live document processing and query handling
- **Error Recovery**: Robust error handling and system diagnostics

## 🏗️ Technology Stack

### Core Frameworks
- **Streamlit** (1.28.1) - Interactive web application framework
- **Langchain** (0.1.0) - LLM application development framework
- **Langgraph** (0.0.26) - Multi-agent workflow orchestration
- **OpenAI** (1.10.0+) - GPT-4 language model integration

### Vector Database & Embeddings
- **FAISS** (1.7.4) - Facebook AI Similarity Search for vector operations
- **Sentence Transformers** (2.2.2) - State-of-the-art sentence embeddings

### Document Processing
- **PyPDF** (3.17.1) - PDF document processing
- **python-docx** (1.1.0) - Microsoft Word document handling
- **openpyxl** (3.1.2) - Excel spreadsheet processing
- **python-pptx** (0.6.23) - PowerPoint presentation processing
- **BeautifulSoup4** (4.12.2) - HTML/XML parsing

### Database Support
- **SQLAlchemy** (2.0.23) - SQL toolkit and ORM
- **mysql-connector-python** (8.2.0) - MySQL database connectivity
- **pymongo** (4.6.0) - MongoDB database operations

### Mathematical & Scientific Computing
- **SymPy** (1.12) - Symbolic mathematics
- **SciPy** (1.11.4) - Scientific computing
- **NumPy** (1.24.3) - Numerical computing
- **Pandas** (2.1.4) - Data manipulation and analysis

### Web & Search Tools
- **Requests** (2.31.0) - HTTP library for web requests
- **urllib3** (2.1.0) - HTTP client library

## 🚀 Installation

### Prerequisites
- **Python 3.11+** (Required)
- **Git** (for cloning the repository)
- **OpenAI API Key** or **AbacusAI API Key**

### Quick Start

#### Option 1: Automated Installation (Windows)
```bash
# Clone the repository
git clone https://github.com/your-username/agentic-rag-app.git
cd agentic-rag-app

# Run automated setup (Windows)
setup.bat
```

#### Option 2: Manual Installation (All Platforms)

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/agentic-rag-app.git
cd agentic-rag-app
```

2. **Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Set Up Environment Variables**
```bash
# Copy the environment template
cp .env.template .env

# Edit .env file with your API keys
nano .env  # Linux/macOS
notepad .env  # Windows
```

5. **Run the Application**
```bash
# Windows
run.bat

# Linux/macOS
streamlit run app.py
```

### Docker Installation (Optional)
```bash
# Build Docker image
docker build -t agentic-rag-app .

# Run container
docker run -p 8501:8501 -v $(pwd)/.env:/app/.env agentic-rag-app
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# Required: OpenAI/AbacusAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
# OR
ABACUSAI_API_KEY=your_abacusai_api_key_here

# Optional: Langchain Tracing (for debugging)
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=enhanced-agentic-rag-app

# Optional: Search API Keys
SERPAPI_API_KEY=your_serpapi_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id

# Optional: MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name

# Optional: MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_DATABASE=agentic_rag
MONGODB_AUTH_SOURCE=admin

# Optional: Agent Configuration
ENABLE_CALCULATOR=true
ENABLE_SEARCH=true
ENABLE_DATABASE=true
ENABLE_RAG=true
COORDINATION_STRATEGY=auto
MAX_AGENTS_PER_QUERY=4
```

### API Key Setup

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to `.env` file: `OPENAI_API_KEY=sk-...`

#### AbacusAI API Key (Alternative)
1. Visit [AbacusAI Platform](https://abacus.ai/)
2. Generate API key from dashboard
3. Add to `.env` file: `ABACUSAI_API_KEY=your_key`

#### Search API Keys (Optional)
- **SerpAPI**: [Get API Key](https://serpapi.com/)
- **Google Custom Search**: [Setup Guide](https://developers.google.com/custom-search/v1/introduction)

## 📖 Usage Guide

### Starting the Application

1. **Activate Virtual Environment**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

2. **Launch Application**
```bash
# Windows (using batch file)
run.bat

# Linux/macOS
streamlit run app.py
```

3. **Access Web Interface**
Open your browser and navigate to: `http://localhost:8501`

### User Interface Overview

The application features 8 comprehensive tabs:

#### 📁 Tab 1: Document Upload
- **Purpose**: Upload and process documents for RAG
- **Supported Formats**: PDF, DOCX, TXT, CSV, XLSX, PPTX, JSON, HTML, XML
- **Features**:
  - Drag-and-drop file upload
  - Batch processing
  - Real-time processing status
  - Document chunking and embedding

**Usage Example**:
1. Click "Browse files" or drag documents into the upload area
2. Select chunking parameters (size: 1000, overlap: 200)
3. Click "Process Documents"
4. Monitor processing progress in real-time

#### 🔍 Tab 2: Enhanced Query Interface
- **Purpose**: Main chat interface with multi-agent coordination
- **Features**:
  - Natural language queries
  - Automatic agent selection
  - Source attribution
  - Confidence scoring

**Usage Examples**:
```
"What is the main topic discussed in the uploaded documents?"
"Calculate the compound interest for $10,000 at 5% for 3 years"
"Search for the latest news about artificial intelligence"
"Show me all users from the database where age > 25"
```

#### 🧮 Tab 3: Calculator Tool
- **Purpose**: Advanced mathematical computations
- **Capabilities**:
  - Basic arithmetic operations
  - Scientific functions
  - Unit conversions
  - Word problem solving

**Usage Examples**:
```
"Calculate sqrt(144) + log(100)"
"Convert 100 fahrenheit to celsius"
"What is the area of a circle with radius 5 meters?"
"If I invest $1000 at 8% annual interest, what will it be worth in 5 years?"
```

#### 🌐 Tab 4: Search Tool
- **Purpose**: Real-time web search and information retrieval
- **Providers**: DuckDuckGo (default), SerpAPI, Google Custom Search
- **Features**:
  - Multi-provider search
  - Result summarization
  - Source verification

**Usage Examples**:
```
"Latest developments in quantum computing"
"Current weather in New York"
"Best practices for machine learning in 2024"
```

#### 🗄️ Tab 5: Database Tools
- **Purpose**: Database operations and queries
- **Supported**: MySQL, MongoDB
- **Features**:
  - Natural language to SQL/NoSQL conversion
  - Schema exploration
  - CRUD operations

**Usage Examples**:
```
"Show all tables in the database"
"Find users who registered in the last 30 days"
"Create a new table for storing product information"
"Update the price of product with ID 123 to $29.99"
```

#### 📊 Tab 6: Knowledge Base
- **Purpose**: Explore and manage processed documents
- **Features**:
  - Document statistics
  - Vector store information
  - Search within knowledge base
  - Document management

#### ⚙️ Tab 7: Settings
- **Purpose**: Application configuration
- **Features**:
  - Agent enable/disable
  - Model parameters
  - Database connections
  - API key management

#### 🔧 Tab 8: Diagnostics
- **Purpose**: System health and troubleshooting
- **Features**:
  - System compatibility checks
  - API connectivity tests
  - Performance metrics
  - Error logs

## 🤖 Multi-Agent Architecture

### Agent Hierarchy

```
┌─────────────────────────────────────┐
│           Coordinator Agent         │
│     (Orchestrates all agents)       │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│   RAG   │ │Calculator│ │ Search  │ │Database │
│ Agent   │ │  Agent   │ │ Agent   │ │ Agent   │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Agent Descriptions

#### 🎯 Coordinator Agent
- **Role**: Central orchestrator and decision maker
- **Responsibilities**:
  - Query analysis and intent detection
  - Agent selection and task distribution
  - Response synthesis and quality assurance
  - Error handling and fallback strategies

#### 📚 RAG Agent
- **Role**: Document-based question answering
- **Capabilities**:
  - Semantic search through document embeddings
  - Context-aware response generation
  - Source attribution and citation
  - Multi-document synthesis

#### 🧮 Calculator Agent
- **Role**: Mathematical computations and analysis
- **Capabilities**:
  - Arithmetic and algebraic operations
  - Scientific and statistical calculations
  - Unit conversions and constants
  - Mathematical word problem solving

#### 🌐 Search Agent
- **Role**: Real-time information retrieval
- **Capabilities**:
  - Multi-provider web search
  - Result ranking and filtering
  - Information synthesis
  - Fact verification

#### 🗄️ Database Agent
- **Role**: Database operations and management
- **Capabilities**:
  - Natural language to SQL/NoSQL conversion
  - Schema analysis and exploration
  - CRUD operations
  - Query optimization

### Workflow Process

1. **Query Reception**: User submits query through interface
2. **Intent Analysis**: Coordinator analyzes query type and complexity
3. **Agent Selection**: Determines which agents are needed
4. **Parallel Execution**: Agents work simultaneously on their tasks
5. **Response Synthesis**: Coordinator combines agent outputs
6. **Quality Assurance**: Validates response accuracy and completeness
7. **Final Formatting**: Presents unified response to user

## 🛠️ Advanced Tools

### Calculator Tool Features

#### Basic Operations
```python
# Arithmetic
"Calculate 15 * 23 + 45"
"What is 2^10?"
"Find the square root of 256"

# Percentages
"What is 15% of 200?"
"Increase 100 by 25%"
```

#### Advanced Functions
```python
# Trigonometry
"Calculate sin(30 degrees)"
"What is the cosine of π/4?"

# Logarithms
"Find log base 10 of 1000"
"Calculate natural log of e^3"

# Statistics
"Calculate the mean of [1, 2, 3, 4, 5]"
"Find standard deviation of the dataset"
```

#### Unit Conversions
```python
# Temperature
"Convert 32°F to Celsius"
"What is 100°C in Fahrenheit?"

# Distance
"Convert 5 miles to kilometers"
"How many meters in 2.5 kilometers?"

# Weight
"Convert 150 pounds to kilograms"
"What is 75 kg in pounds?"
```

### Search Tool Configuration

#### Provider Setup
```python
# DuckDuckGo (No API key required)
search_config = {
    'default_provider': 'duckduckgo',
    'max_results': 10
}

# SerpAPI (Requires API key)
search_config = {
    'serpapi_key': 'your_serpapi_key',
    'default_provider': 'serpapi'
}

# Google Custom Search (Requires API key + CSE ID)
search_config = {
    'google_api_key': 'your_google_api_key',
    'google_cse_id': 'your_cse_id',
    'default_provider': 'google'
}
```

### Database Tool Operations

#### MySQL Operations
```sql
-- Schema exploration
"Show me all tables in the database"
"Describe the structure of the users table"

-- Data queries
"Find all users with age greater than 25"
"Show the top 10 products by sales"

-- Data modification
"Insert a new user with name 'John' and age 30"
"Update the email for user ID 123"
```

#### MongoDB Operations
```javascript
// Collection exploration
"List all collections in the database"
"Show the structure of the products collection"

// Document queries
"Find all documents where status is 'active'"
"Get users who registered in the last month"

// Document operations
"Insert a new product document"
"Update the price field for product ID 'abc123'"
```

## 📄 File Format Support

### Supported Document Types

| Format | Extension | Description | Features |
|--------|-----------|-------------|----------|
| PDF | `.pdf` | Portable Document Format | Text extraction, page attribution |
| Word | `.docx`, `.doc` | Microsoft Word documents | Full text, formatting preservation |
| Excel | `.xlsx`, `.xls` | Microsoft Excel spreadsheets | Multiple sheets, data extraction |
| PowerPoint | `.pptx`, `.ppt` | Microsoft PowerPoint | Slide content, speaker notes |
| Text | `.txt` | Plain text files | Direct content processing |
| CSV | `.csv` | Comma-separated values | Structured data import |
| JSON | `.json` | JavaScript Object Notation | Structured data processing |
| HTML | `.html`, `.htm` | Web pages | Content extraction, link parsing |
| XML | `.xml` | Extensible Markup Language | Structured data parsing |

### Processing Features

#### Text Extraction
- **PDF**: Advanced text extraction with page numbers
- **Office Documents**: Content, headers, footers, metadata
- **Web Formats**: Clean text extraction, link preservation

#### Chunking Strategy
- **Configurable Size**: Default 1000 characters
- **Overlap**: Default 200 characters for context preservation
- **Smart Splitting**: Sentence and paragraph boundary respect

#### Metadata Preservation
- **Source Attribution**: File name, page numbers, sections
- **Processing Timestamps**: Upload and processing times
- **Content Statistics**: Word count, character count, chunk count

## 🔌 API Integration

### OpenAI Integration

#### Model Configuration
```python
# Primary model for complex reasoning
model = "gpt-4-1106-preview"
temperature = 0.1
max_tokens = 4000

# Embedding model for vector operations
embedding_model = "text-embedding-3-small"
```

#### AbacusAI Integration
```python
# Alternative API endpoint
base_url = "https://apps.abacus.ai/v1"
api_key = "your_abacusai_api_key"
```

### Search API Integration

#### SerpAPI Configuration
```python
import serpapi

client = serpapi.Client(api_key="your_serpapi_key")
results = client.search({
    "engine": "google",
    "q": "your search query",
    "num": 10
})
```

#### Google Custom Search
```python
from googleapiclient.discovery import build

service = build("customsearch", "v1", 
                developerKey="your_api_key")
results = service.cse().list(
    q="your query",
    cx="your_cse_id",
    num=10
).execute()
```

### Database Integration

#### MySQL Connection
```python
import mysql.connector

config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'database': 'your_database',
    'charset': 'utf8mb4',
    'autocommit': True
}

connection = mysql.connector.connect(**config)
```

#### MongoDB Connection
```python
from pymongo import MongoClient

client = MongoClient(
    host='localhost',
    port=27017,
    username='your_username',
    password='your_password',
    authSource='admin'
)

database = client['your_database']
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Installation Issues

**Problem**: `pip install` fails with dependency conflicts
```bash
# Solution: Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

**Problem**: Python version compatibility
```bash
# Check Python version
python --version

# Required: Python 3.11+
# Install from: https://www.python.org/downloads/
```

#### 2. API Key Issues

**Problem**: "Invalid API key" error
```bash
# Check .env file exists and contains:
OPENAI_API_KEY=sk-your-actual-key-here

# Verify key format:
# OpenAI keys start with 'sk-'
# AbacusAI keys have different format
```

**Problem**: API quota exceeded
```bash
# Check your API usage at:
# OpenAI: https://platform.openai.com/usage
# AbacusAI: https://abacus.ai/dashboard
```

#### 3. Database Connection Issues

**Problem**: MySQL connection failed
```bash
# Check MySQL service is running
# Windows: services.msc -> MySQL
# Linux: sudo systemctl status mysql
# macOS: brew services list | grep mysql

# Verify credentials in .env file
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
```

**Problem**: MongoDB connection timeout
```bash
# Check MongoDB service
# Windows: services.msc -> MongoDB
# Linux: sudo systemctl status mongod
# macOS: brew services list | grep mongodb

# Test connection
mongo --host localhost:27017
```

#### 4. File Processing Issues

**Problem**: Large file upload fails
```bash
# Check file size limit (200MB default)
# Split large files or increase limit in config.py
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
```

**Problem**: Unsupported file format
```bash
# Check supported formats in config.py
SUPPORTED_FORMATS = [
    "pdf", "docx", "txt", "csv", "xlsx", 
    "pptx", "json", "html", "xml"
]
```

#### 5. Vector Store Issues

**Problem**: FAISS index corruption
```bash
# Delete and rebuild vector store
rm -rf vector_store/
# Re-upload documents through UI
```

**Problem**: Embedding generation fails
```bash
# Check OpenAI API key and quota
# Verify internet connection
# Try smaller document chunks
```

#### 6. Platform-Specific Issues

**Windows Issues**:
```bash
# Permission errors
# Run Command Prompt as Administrator
# Move project to simpler path (C:\AgenticRAG\)

# Path length issues
# Enable long path support in Windows
# Use shorter folder names
```

**Linux/macOS Issues**:
```bash
# Permission errors
chmod +x start.sh
sudo chown -R $USER:$USER /path/to/project

# Missing system dependencies
sudo apt-get install python3-dev  # Ubuntu/Debian
brew install python@3.11          # macOS
```

### Performance Optimization

#### Memory Usage
```bash
# Monitor memory usage
# Reduce chunk size for large documents
CHUNK_SIZE = 500  # Smaller chunks

# Limit concurrent processing
MAX_AGENTS_PER_QUERY = 2
```

#### Response Speed
```bash
# Use faster embedding model
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"

# Reduce search results
max_results = 5

# Enable caching
ENABLE_CACHE = true
```

### Debug Mode

Enable detailed logging:
```python
# Add to .env file
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=debug-session
LOG_LEVEL=DEBUG
```

View logs:
```bash
# Check application logs
tail -f streamlit.log
tail -f app_test.log

# Check system logs
# Windows: Event Viewer
# Linux: journalctl -f
# macOS: Console.app
```

## 🤝 Contributing

We welcome contributions to the Enhanced Agentic RAG Assistant! Here's how you can help:

### Development Setup

1. **Fork the Repository**
```bash
git clone https://github.com/your-username/agentic-rag-app.git
cd agentic-rag-app
```

2. **Create Development Environment**
```bash
python -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
dev-env\Scripts\activate     # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

3. **Install Pre-commit Hooks**
```bash
pre-commit install
```

### Code Style Guidelines

- **Python**: Follow PEP 8 style guide
- **Documentation**: Use Google-style docstrings
- **Type Hints**: Include type annotations
- **Testing**: Write unit tests for new features

### Contribution Types

#### 🐛 Bug Reports
- Use GitHub Issues
- Include system information
- Provide reproduction steps
- Attach relevant logs

#### ✨ Feature Requests
- Describe the use case
- Explain expected behavior
- Consider implementation approach
- Discuss potential impacts

#### 🔧 Code Contributions
- Create feature branch
- Write comprehensive tests
- Update documentation
- Submit pull request

### Pull Request Process

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**
- Write clean, documented code
- Add/update tests
- Update documentation

3. **Test Changes**
```bash
# Run tests
python -m pytest tests/

# Run linting
flake8 .
black .
isort .
```

4. **Submit Pull Request**
- Clear description of changes
- Link related issues
- Include test results
- Request review

### Development Guidelines

#### Adding New Agents
```python
# 1. Create agent class in agents/
class NewAgent:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(openai_api_key=openai_api_key)
    
    def process(self, query: str) -> Dict[str, Any]:
        # Implementation
        pass

# 2. Register in coordinator_agent.py
self.available_agents['new_agent'] = NewAgent(openai_api_key)

# 3. Add UI tab in app.py
def handle_new_agent_tool():
    # UI implementation
    pass
```

#### Adding New Tools
```python
# 1. Create tool class in tools/
class NewTool:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass

# 2. Register in agent
from tools.new_tool import NewTool
self.new_tool = NewTool(config)
```

#### Testing Guidelines
```python
# Unit tests
def test_calculator_agent():
    agent = CalculatorAgent(api_key="test")
    result = agent.calculate("2 + 2")
    assert result["answer"] == 4

# Integration tests
def test_full_workflow():
    workflow = EnhancedAgenticWorkflow(api_key="test")
    result = workflow.process("Calculate 10 * 5")
    assert "50" in result["response"]
```

### Documentation Standards

- **README**: Keep updated with new features
- **Docstrings**: Document all public methods
- **Comments**: Explain complex logic
- **Examples**: Provide usage examples

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

```
MIT License

Copyright (c) 2024 Enhanced Agentic RAG Assistant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Credits and Acknowledgments

### Core Technologies
- **[Langchain](https://langchain.com/)** - LLM application framework
- **[Langgraph](https://langchain-ai.github.io/langgraph/)** - Multi-agent workflow orchestration
- **[OpenAI](https://openai.com/)** - GPT-4 language model
- **[FAISS](https://faiss.ai/)** - Vector similarity search
- **[Streamlit](https://streamlit.io/)** - Web application framework

### Libraries and Dependencies
- **[Sentence Transformers](https://www.sbert.net/)** - Sentence embeddings
- **[SymPy](https://www.sympy.org/)** - Symbolic mathematics
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** - HTML/XML parsing
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation
- **[NumPy](https://numpy.org/)** - Numerical computing

### Special Thanks
- OpenAI team for GPT-4 and embedding models
- Langchain community for the excellent framework
- FAISS team at Facebook AI Research
- Streamlit team for the intuitive web framework
- All contributors and beta testers

---

## 📞 Support and Contact

### Getting Help
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-username/agentic-rag-app/issues)
- **Discussions**: [Community discussions](https://github.com/your-username/agentic-rag-app/discussions)
- **Documentation**: [Wiki pages](https://github.com/your-username/agentic-rag-app/wiki)

### Community
- **Discord**: [Join our community](https://discord.gg/your-invite)
- **Twitter**: [@AgenticRAG](https://twitter.com/AgenticRAG)
- **LinkedIn**: [Project Page](https://linkedin.com/company/agentic-rag)

### Professional Support
For enterprise support, custom development, or consulting services, please contact:
- **Email**: support@agentic-rag.com
- **Website**: [https://agentic-rag.com](https://agentic-rag.com)

---

**⭐ If you find this project helpful, please consider giving it a star on GitHub!**

**🚀 Ready to get started? Follow the [Installation Guide](#-installation) above!**
