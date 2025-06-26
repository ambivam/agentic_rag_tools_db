
"""
Database Agent for MySQL and MongoDB operations
"""

import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from tools.database_tools import MySQLTool, MongoDBTool, MYSQL_AVAILABLE, MONGODB_AVAILABLE
from config import Config
import logging

logger = logging.getLogger(__name__)

class DatabaseAgent:
    """Agent specialized in database operations and queries"""
    
    def __init__(self, openai_api_key: str, database_configs: Dict[str, Dict[str, Any]] = None):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=Config.OPENAI_MODEL,
            temperature=0.1
        )
        
        self.database_configs = database_configs or {}
        self.mysql_tool = None
        self.mongodb_tool = None
        self.active_connections = {}
        
        self.agent_name = "Database Agent"
        self.capabilities = [
            "MySQL database operations",
            "MongoDB document operations", 
            "SQL query generation and execution",
            "NoSQL query operations",
            "Database schema analysis",
            "Data retrieval and manipulation"
        ]
        
        # Initialize tools if available
        if MYSQL_AVAILABLE:
            try:
                self.mysql_tool = MySQLTool(self.database_configs.get('mysql', {}))
            except Exception as e:
                logger.warning(f"MySQL tool initialization failed: {str(e)}")
        
        if MONGODB_AVAILABLE:
            try:
                self.mongodb_tool = MongoDBTool(self.database_configs.get('mongodb', {}))
            except Exception as e:
                logger.warning(f"MongoDB tool initialization failed: {str(e)}")
    
    def analyze_request(self, request: str) -> Dict[str, Any]:
        """
        Analyze if the request requires database operations
        
        Args:
            request: User request to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert database analysis agent. Your role is to identify when a user's request involves data that could be efficiently retrieved from a database, even if they don't explicitly mention database terms.

Analyze the request to determine:
1. If it involves structured data typically stored in databases (e.g., user records, geographic data, product info)
2. If it requires data operations (listing, filtering, aggregating, etc.)
3. What type of database would best serve this data (SQL/NoSQL)
4. What tables/collections might contain this data
5. Required permissions and complexity

Consider these patterns that suggest database use:
- Requests for lists or tables of information
- Filtering by specific criteria
- Questions about structured data (countries, products, users, etc.)
- Requests for specific fields or attributes
- Queries involving relationships between data
- Economic queries (GNP, GDP, financial data)
- Ranking or ordering data (top N, highest, lowest)
- Demographic queries (population, statistics)
- Geographic queries (countries, cities, regions)

Respond in JSON format with:
- requires_database: boolean
- operation_type: string (select/insert/update/delete/create/analyze/etc.)
- database_preference: string (mysql/mongodb/either/unknown)
- tables_collections: list of likely table/collection names
- data_requirements: list of fields or requirements
- complexity: string (simple/moderate/complex)
- permissions_needed: list of required permissions
- confidence: float (0-1)
- reasoning: string explaining why this should/shouldn't use a database
"""),
                ("human", "Request: {request}")
            ])
            
            response = self.llm.invoke(
                analysis_prompt.format_messages(request=request)
            )
            
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback analysis with enhanced natural language patterns
                db_keywords = [
                    # Database-specific terms
                    'database', 'sql', 'mysql', 'mongodb', 'select', 'insert', 
                    'update', 'delete', 'query', 'table', 'collection', 'record',
                    'data', 'store', 'retrieve', 'search database', 'db',
                    # List/Table indicators
                    'list', 'show', 'display', 'table', 'all', 'every',
                    # Geographic data
                    'countries', 'cities', 'regions', 'states', 'locations',
                    'capitals', 'population', 'continent', 'india', 'asia',
                    'district', 'state', 'country',
                    # Common data operations
                    'where', 'filter', 'group', 'sort', 'order by', 'find',
                    # Data relationships
                    'related', 'belongs to', 'has', 'with', 'contains',
                    # Aggregations
                    'count', 'total', 'average', 'maximum', 'minimum', 'top', 'highest', 'lowest',
                    # Economic terms
                    'gnp', 'gdp', 'economy', 'economic', 'richest', 'poorest', 'wealth', 'income',
                    'developed', 'developing', 'trillion', 'billion', 'million'
                ]
                
                needs_db = any(keyword in request.lower() for keyword in db_keywords)
                
                analysis = {
                    "requires_database": needs_db,
                    "operation_type": "select" if needs_db else "none",
                    "database_preference": "either" if needs_db else "unknown",
                    "tables_collections": [],
                    "data_requirements": [],
                    "complexity": "moderate" if needs_db else "none",
                    "permissions_needed": ["read"] if needs_db else [],
                    "confidence": 0.7 if needs_db else 0.3,
                    "reasoning": "Fallback analysis based on keyword detection"
                }
            
            logger.info(f"Database analysis: {analysis.get('requires_database', False)}")
            return analysis
            
        except Exception as e:
            logger.error(f"Database analysis error: {str(e)}")
            return {
                "requires_database": False,
                "operation_type": "error",
                "database_preference": "unknown",
                "tables_collections": [],
                "data_requirements": [],
                "complexity": "error",
                "permissions_needed": [],
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}"
            }
    
    def execute_database_operation(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute database operations based on request
        
        Args:
            request: Database operation request
            context: Additional context for the operation
            
        Returns:
            Dictionary containing operation results
        """
        try:
            # Analyze request
            analysis = self.analyze_request(request)
            
            if not analysis.get('requires_database', False):
                return {
                    'success': False,
                    'message': 'Request does not require database operations',
                    'error': 'Not a database operation'
                }
            
            # Ensure database connections
            mysql_connected = False
            mongodb_connected = False
            
            if analysis['database_preference'] in ['mysql', 'either']:
                if self.mysql_tool and 'mysql' not in self.active_connections:
                    mysql_result = self.mysql_tool.connect(self.database_configs.get('mysql', {}))
                    if mysql_result['success']:
                        self.active_connections['mysql'] = mysql_result
                        mysql_connected = True
                else:
                    mysql_connected = 'mysql' in self.active_connections
            
            if analysis['database_preference'] in ['mongodb', 'either']:
                if self.mongodb_tool and 'mongodb' not in self.active_connections:
                    mongodb_result = self.mongodb_tool.connect(self.database_configs.get('mongodb', {}))
                    if mongodb_result['success']:
                        self.active_connections['mongodb'] = mongodb_result
                        mongodb_connected = True
                else:
                    mongodb_connected = 'mongodb' in self.active_connections
            
            # Execute operation based on database type and connection status
            if analysis['database_preference'] == 'mysql':
                if mysql_connected or 'mysql' in self.active_connections:
                    return self._execute_mysql_operation(request, analysis, context)
                else:
                    return {
                        'success': False,
                        'message': 'MySQL connection not available',
                        'error': 'Connection failed or not configured'
                    }
                    
            elif analysis['database_preference'] == 'mongodb':
                if mongodb_connected or 'mongodb' in self.active_connections:
                    return self._execute_mongodb_operation(request, analysis, context)
                else:
                    return {
                        'success': False,
                        'message': 'MongoDB connection not available',
                        'error': 'Connection failed or not configured'
                    }
                    
            else:
                # Try both if no preference
                results = []
                
                if mysql_connected or 'mysql' in self.active_connections:
                    mysql_result = self._execute_mysql_operation(request, analysis, context)
                    if mysql_result['success']:
                        return mysql_result
                    results.append(('MySQL', mysql_result.get('error')))
                
                if mongodb_connected or 'mongodb' in self.active_connections:
                    mongodb_result = self._execute_mongodb_operation(request, analysis, context)
                    if mongodb_result['success']:
                        return mongodb_result
                    results.append(('MongoDB', mongodb_result.get('error')))
                
                if not results:
                    return {
                        'success': False,
                        'message': 'No database connections available',
                        'error': 'Configure and connect to a database first'
                    }
                else:
                    errors = '; '.join([f"{db}: {err}" for db, err in results])
                    return {
                        'success': False,
                        'message': 'Failed to execute on any available database',
                        'error': errors
                    }
                
        except Exception as e:
            logger.error(f"Database operation error: {str(e)}")
            return {
                'success': False,
                'message': 'Database operation failed',
                'error': str(e)
            }
    
    def _execute_mysql_operation(self, request: str, analysis: Dict[str, Any], 
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MySQL database operations"""
        try:
            if not self.mysql_tool:
                return {
                    'success': False,
                    'message': 'MySQL tool not available',
                    'database_type': 'mysql',
                    'error': 'MySQL support not installed or configured'
                }
            
            # Connect to database if not connected
            if 'mysql' not in self.active_connections:
                connection_result = self.mysql_tool.connect()
                if not connection_result['success']:
                    return {
                        'success': False,
                        'message': 'Failed to connect to MySQL database',
                        'database_type': 'mysql',
                        'error': connection_result.get('error', 'Connection failed')
                    }
                self.active_connections['mysql'] = True
            
            operation_type = analysis.get('operation_type', 'select')
            
            # Handle different operation types
            if operation_type in ['select', 'analyze']:
                return self._handle_mysql_query(request, analysis, context)
            elif operation_type == 'insert':
                return self._handle_mysql_insert(request, analysis, context)
            elif operation_type in ['update', 'delete']:
                return self._handle_mysql_modification(request, analysis, context)
            else:
                # Generate and execute SQL query
                sql_query = self._generate_sql_query(request, analysis, context)
                if sql_query:
                    result = self.mysql_tool.execute_query(sql_query)
                    return {
                        'success': result['success'],
                        'message': result['message'],
                        'database_type': 'mysql',
                        'operation_type': operation_type,
                        'query': sql_query,
                        'results': result['results'],
                        'row_count': result['row_count'],
                        'columns': result['columns'],
                        'query_time': result['query_time'],
                        'agent': self.agent_name,
                        'error': result.get('error')
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Could not generate SQL query',
                        'database_type': 'mysql',
                        'operation_type': operation_type,
                        'error': 'SQL generation failed'
                    }
                    
        except Exception as e:
            logger.error(f"MySQL operation error: {str(e)}")
            return {
                'success': False,
                'message': 'MySQL operation failed',
                'database_type': 'mysql',
                'agent': self.agent_name,
                'error': str(e)
            }
    
    def _execute_mongodb_operation(self, request: str, analysis: Dict[str, Any], 
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MongoDB database operations"""
        try:
            if not self.mongodb_tool:
                return {
                    'success': False,
                    'message': 'MongoDB tool not available',
                    'database_type': 'mongodb',
                    'error': 'MongoDB support not installed or configured'
                }
            
            # Connect to database if not connected
            if 'mongodb' not in self.active_connections:
                connection_result = self.mongodb_tool.connect()
                if not connection_result['success']:
                    return {
                        'success': False,
                        'message': 'Failed to connect to MongoDB database',
                        'database_type': 'mongodb',
                        'error': connection_result.get('error', 'Connection failed')
                    }
                self.active_connections['mongodb'] = True
            
            operation_type = analysis.get('operation_type', 'select')
            collections = analysis.get('tables_collections', ['default_collection'])
            collection_name = collections[0] if collections else 'default_collection'
            
            # Handle different operation types
            if operation_type in ['select', 'analyze']:
                query_filter = self._generate_mongodb_query(request, analysis, context)
                result = self.mongodb_tool.find_documents(collection_name, query_filter, limit=20)
                
                return {
                    'success': result['success'],
                    'message': result['message'],
                    'database_type': 'mongodb',
                    'operation_type': operation_type,
                    'collection': collection_name,
                    'query': query_filter,
                    'results': result['documents'],
                    'document_count': result['document_count'],
                    'query_time': result.get('query_time', 0),
                    'agent': self.agent_name,
                    'error': result.get('error')
                }
            elif operation_type == 'insert':
                # Generate document to insert
                document = self._generate_mongodb_document(request, analysis, context)
                if document:
                    result = self.mongodb_tool.insert_document(collection_name, document)
                    return {
                        'success': result['success'],
                        'message': result['message'],
                        'database_type': 'mongodb',
                        'operation_type': operation_type,
                        'collection': collection_name,
                        'inserted_document': document,
                        'inserted_id': result.get('inserted_id'),
                        'agent': self.agent_name,
                        'error': result.get('error')
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Could not generate document to insert',
                        'database_type': 'mongodb',
                        'operation_type': operation_type,
                        'error': 'Document generation failed'
                    }
            else:
                return {
                    'success': False,
                    'message': f'MongoDB operation {operation_type} not implemented',
                    'database_type': 'mongodb',
                    'operation_type': operation_type,
                    'error': 'Operation not supported'
                }
                
        except Exception as e:
            logger.error(f"MongoDB operation error: {str(e)}")
            return {
                'success': False,
                'message': 'MongoDB operation failed',
                'database_type': 'mongodb',
                'agent': self.agent_name,
                'error': str(e)
            }
    
    def _generate_sql_query(self, request: str, analysis: Dict[str, Any], 
                           context: Dict[str, Any] = None) -> Optional[str]:
        """Generate SQL query based on request"""
        try:
            sql_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert SQL query generator for the MySQL World database. Given a user request and analysis, 
generate a safe, efficient SQL query. The World database has these main tables:

- country: Information about countries
  Columns: code, name, continent, region, surfacearea, indepyear, population, lifeexpectancy, gnp, gnpold, localname, governmentform, headofstate, capital, code2

- city: Information about cities
  Columns: id, name, countrycode, district, population

- countrylanguage: Information about languages spoken in countries
  Columns: countrycode, language, isofficial, percentage

Notes:
- The city.id column is referenced by country.capital to indicate a country's capital city
- country.code matches with city.countrycode and countrylanguage.countrycode
- Use simple table aliases without backticks (e.g. FROM country c JOIN city ct)

Follow these guidelines:
1. Generate only SELECT queries unless explicitly requested otherwise
2. Use proper SQL syntax and best practices
3. Include appropriate WHERE clauses for filtering
4. Use LIMIT to prevent excessive results (default 100)
5. Avoid dangerous operations (DROP, TRUNCATE, etc.)
6. Use exact table and column names as shown above

Return only the raw SQL query, no markdown formatting or explanation.
"""),
                ("human", """
User Request: {request}

Analysis: {analysis}

Context: {context}

SQL Query:""")
            ])
            
            response = self.llm.invoke(
                sql_prompt.format_messages(
                    request=request,
                    analysis=json.dumps(analysis, indent=2),
                    context=json.dumps(context or {}, indent=2)
                )
            )
            
            # Clean the SQL query by removing any markdown formatting
            sql_query = response.content
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            # Basic safety check
            dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
            if any(keyword in sql_query.upper() for keyword in dangerous_keywords):
                logger.warning(f"Potentially dangerous SQL query blocked: {sql_query}")
                return None
            
            return sql_query
            
        except Exception as e:
            logger.error(f"SQL generation error: {str(e)}")
            return None
    
    def _generate_mongodb_query(self, request: str, analysis: Dict[str, Any], 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate MongoDB query filter"""
        try:
            mongodb_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert MongoDB query generator. Given a user request and analysis,
generate a MongoDB query filter in JSON format. Follow these guidelines:

1. Create appropriate filter conditions
2. Use MongoDB operators ($eq, $gt, $lt, $in, $regex, etc.)
3. Keep queries safe and efficient
4. Return empty object {} for "find all" queries

Return only the JSON query filter, nothing else.
"""),
                ("human", """
User Request: {request}

Analysis: {analysis}

Context: {context}

MongoDB Query Filter:""")
            ])
            
            response = self.llm.invoke(
                mongodb_prompt.format_messages(
                    request=request,
                    analysis=json.dumps(analysis, indent=2),
                    context=json.dumps(context or {}, indent=2)
                )
            )
            
            try:
                query_filter = json.loads(response.content.strip())
                return query_filter
            except json.JSONDecodeError:
                return {}  # Default to empty filter (find all)
                
        except Exception as e:
            logger.error(f"MongoDB query generation error: {str(e)}")
            return {}
    
    def _generate_mongodb_document(self, request: str, analysis: Dict[str, Any], 
                                  context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Generate MongoDB document for insertion"""
        try:
            doc_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert at generating MongoDB documents. Given a user request,
create a properly structured JSON document for insertion. Include:

1. Relevant fields based on the request
2. Appropriate data types
3. Timestamp fields when appropriate
4. Proper JSON structure

Return only the JSON document, nothing else.
"""),
                ("human", """
User Request: {request}

Analysis: {analysis}

Context: {context}

MongoDB Document:""")
            ])
            
            response = self.llm.invoke(
                doc_prompt.format_messages(
                    request=request,
                    analysis=json.dumps(analysis, indent=2),
                    context=json.dumps(context or {}, indent=2)
                )
            )
            
            try:
                document = json.loads(response.content.strip())
                return document
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            logger.error(f"MongoDB document generation error: {str(e)}")
            return None
    
    def _handle_mysql_query(self, request: str, analysis: Dict[str, Any], 
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle MySQL SELECT queries"""
        # Implementation for specialized MySQL query handling
        sql_query = self._generate_sql_query(request, analysis, context)
        if sql_query:
            result = self.mysql_tool.execute_query(sql_query)
            return {
                'success': result['success'],
                'message': result['message'],
                'database_type': 'mysql',
                'operation_type': 'select',
                'query': sql_query,
                'results': result['results'],
                'row_count': result['row_count'],
                'columns': result['columns'],
                'query_time': result['query_time'],
                'agent': self.agent_name,
                'error': result.get('error'),
                'sources': [{
                    'type': 'database',
                    'name': self.database_configs.get('mysql', {}).get('database', 'mysql'),
                    'table': next(iter(analysis.get('tables_collections', [])), 'unknown'),
                    'query': sql_query,
                    'row_count': result['row_count'],
                    'confidence': 1.0
                }]
            }
        else:
            return {
                'success': False,
                'message': 'Could not generate SQL query',
                'database_type': 'mysql',
                'operation_type': 'select',
                'error': 'SQL generation failed'
            }
    
    def _handle_mysql_insert(self, request: str, analysis: Dict[str, Any], 
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle MySQL INSERT operations"""
        # For now, delegate to general SQL generation
        return self._execute_mysql_operation(request, analysis, context)
    
    def _handle_mysql_modification(self, request: str, analysis: Dict[str, Any], 
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle MySQL UPDATE/DELETE operations"""
        # For now, delegate to general SQL generation with extra safety
        return self._execute_mysql_operation(request, analysis, context)
    
    def get_database_info(self, database_type: str = 'both') -> Dict[str, Any]:
        """Get information about available databases"""
        info = {
            'mysql': {'available': MYSQL_AVAILABLE, 'connected': False, 'info': None},
            'mongodb': {'available': MONGODB_AVAILABLE, 'connected': False, 'info': None}
        }
        
        # MySQL info
        if database_type in ['mysql', 'both'] and self.mysql_tool and 'mysql' in self.active_connections:
            try:
                mysql_info = self.mysql_tool.get_table_info()
                info['mysql']['connected'] = True
                info['mysql']['info'] = mysql_info
            except Exception as e:
                info['mysql']['error'] = str(e)
        
        # MongoDB info
        if database_type in ['mongodb', 'both'] and self.mongodb_tool and 'mongodb' in self.active_connections:
            try:
                mongodb_info = self.mongodb_tool.get_collection_info()
                info['mongodb']['connected'] = True
                info['mongodb']['info'] = mongodb_info
            except Exception as e:
                info['mongodb']['error'] = str(e)
        
        return info
    
    def disconnect_all(self) -> Dict[str, Any]:
        """Disconnect from all databases"""
        results = {}
        
        if self.mysql_tool and 'mysql' in self.active_connections:
            results['mysql'] = self.mysql_tool.disconnect()
            if results['mysql']['success']:
                del self.active_connections['mysql']
        
        if self.mongodb_tool and 'mongodb' in self.active_connections:
            results['mongodb'] = self.mongodb_tool.disconnect()
            if results['mongodb']['success']:
                del self.active_connections['mongodb']
        
        return results
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        capabilities = self.capabilities.copy()
        
        if not MYSQL_AVAILABLE:
            capabilities = [cap for cap in capabilities if 'MySQL' not in cap]
        
        if not MONGODB_AVAILABLE:
            capabilities = [cap for cap in capabilities if 'MongoDB' not in cap]
        
        return capabilities
