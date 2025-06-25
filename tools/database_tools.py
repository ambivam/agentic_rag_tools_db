
"""
Database tools for MySQL and MongoDB connectivity
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# Optional imports with fallback
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    PyMongoError = Exception

class MySQLTool:
    """MySQL database connectivity and operations tool"""
    
    def __init__(self, config: Dict[str, Any] = None):
        if not MYSQL_AVAILABLE:
            raise ImportError("MySQL support not available. Install with: pip install mysql-connector-python")
        
        self.config = config or {}
        self.connection = None
        self.cursor = None
        self.connection_pool = {}
        
        # Default connection settings
        self.default_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': '',
            'charset': 'utf8mb4',
            'autocommit': True,
            'pool_name': 'default_pool',
            'pool_size': 5
        }
    
    def connect(self, connection_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Connect to MySQL database
        
        Args:
            connection_config: Database connection configuration
            
        Returns:
            Dictionary containing connection status and metadata
        """
        try:
            config = {**self.default_config, **(connection_config or {}), **self.config}
            
            logger.info(f"Connecting to MySQL database: {config['host']}:{config['port']}")
            
            # Create connection with pool
            self.connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                charset=config['charset'],
                autocommit=config['autocommit'],
                pool_name=config['pool_name'],
                pool_size=config['pool_size']
            )
            
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Test connection
            self.cursor.execute("SELECT VERSION()")
            version = self.cursor.fetchone()
            
            return {
                'success': True,
                'message': 'Connected to MySQL successfully',
                'server_version': version['VERSION()'] if version else 'Unknown',
                'database': config['database'],
                'host': config['host'],
                'port': config['port'],
                'connection_time': datetime.now().isoformat(),
                'error': None
            }
            
        except MySQLError as e:
            logger.error(f"MySQL connection error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to connect to MySQL',
                'server_version': None,
                'database': None,
                'host': None,
                'port': None,
                'connection_time': None,
                'error': str(e)
            }
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Execute SQL query
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Dictionary containing query results and metadata
        """
        try:
            if not self.connection or not self.cursor:
                return {
                    'success': False,
                    'message': 'No active database connection',
                    'results': [],
                    'row_count': 0,
                    'columns': [],
                    'query_time': 0,
                    'error': 'Connection not established'
                }
            
            start_time = time.time()
            
            logger.info(f"Executing MySQL query: {query[:100]}...")
            
            # Execute query
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            query_time = time.time() - start_time
            
            # Determine query type
            query_type = query.strip().upper().split()[0]
            
            if query_type == 'SELECT':
                results = self.cursor.fetchall()
                columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
                row_count = len(results)
            else:
                results = []
                columns = []
                row_count = self.cursor.rowcount
                
                # Commit transaction for non-SELECT queries
                if self.connection.autocommit is False:
                    self.connection.commit()
            
            return {
                'success': True,
                'message': f'Query executed successfully ({query_type})',
                'results': results,
                'row_count': row_count,
                'columns': columns,
                'query_time': round(query_time, 4),
                'query_type': query_type,
                'error': None
            }
            
        except MySQLError as e:
            logger.error(f"MySQL query error: {str(e)}")
            return {
                'success': False,
                'message': 'Query execution failed',
                'results': [],
                'row_count': 0,
                'columns': [],
                'query_time': 0,
                'query_type': 'ERROR',
                'error': str(e)
            }
    
    def get_table_info(self, table_name: str = None) -> Dict[str, Any]:
        """
        Get information about database tables
        
        Args:
            table_name: Specific table name (optional, returns all if None)
            
        Returns:
            Dictionary containing table information
        """
        try:
            if table_name:
                # Get specific table info
                query = """
                SELECT 
                    COLUMN_NAME,
                    COLUMN_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COLUMN_KEY,
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = DATABASE()
                ORDER BY ORDINAL_POSITION
                """
                result = self.execute_query(query, (table_name,))
                
                if result['success']:
                    return {
                        'success': True,
                        'table_name': table_name,
                        'columns': result['results'],
                        'column_count': len(result['results']),
                        'error': None
                    }
                else:
                    return result
            else:
                # Get all tables
                query = "SHOW TABLES"
                result = self.execute_query(query)
                
                if result['success']:
                    tables = [list(row.values())[0] for row in result['results']]
                    return {
                        'success': True,
                        'tables': tables,
                        'table_count': len(tables),
                        'error': None
                    }
                else:
                    return result
                    
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to get table information',
                'error': str(e)
            }
    
    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from MySQL database"""
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            
            if self.connection:
                self.connection.close()
                self.connection = None
            
            return {
                'success': True,
                'message': 'Disconnected from MySQL successfully',
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error disconnecting from MySQL: {str(e)}")
            return {
                'success': False,
                'message': 'Error during disconnection',
                'error': str(e)
            }

class MongoDBTool:
    """MongoDB database connectivity and operations tool"""
    
    def __init__(self, config: Dict[str, Any] = None):
        if not MONGODB_AVAILABLE:
            raise ImportError("MongoDB support not available. Install with: pip install pymongo")
        
        self.config = config or {}
        self.client = None
        self.database = None
        
        # Default connection settings
        self.default_config = {
            'host': 'localhost',
            'port': 27017,
            'username': None,
            'password': None,
            'database': 'test',
            'auth_source': 'admin',
            'connection_timeout': 10000,
            'server_selection_timeout': 5000
        }
    
    def connect(self, connection_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Connect to MongoDB database
        
        Args:
            connection_config: Database connection configuration
            
        Returns:
            Dictionary containing connection status and metadata
        """
        try:
            config = {**self.default_config, **(connection_config or {}), **self.config}
            
            logger.info(f"Connecting to MongoDB: {config['host']}:{config['port']}")
            
            # Build connection string
            if config['username'] and config['password']:
                connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config['auth_source']}"
            else:
                connection_string = f"mongodb://{config['host']}:{config['port']}"
            
            # Create client
            self.client = MongoClient(
                connection_string,
                connectTimeoutMS=config['connection_timeout'],
                serverSelectionTimeoutMS=config['server_selection_timeout']
            )
            
            # Select database
            self.database = self.client[config['database']]
            
            # Test connection
            server_info = self.client.server_info()
            
            return {
                'success': True,
                'message': 'Connected to MongoDB successfully',
                'server_version': server_info.get('version', 'Unknown'),
                'database': config['database'],
                'host': config['host'],
                'port': config['port'],
                'connection_time': datetime.now().isoformat(),
                'error': None
            }
            
        except PyMongoError as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to connect to MongoDB',
                'server_version': None,
                'database': None,
                'host': None,
                'port': None,
                'connection_time': None,
                'error': str(e)
            }
    
    def find_documents(self, collection_name: str, query: Dict[str, Any] = None, 
                      limit: int = 10, sort: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Find documents in MongoDB collection
        
        Args:
            collection_name: Name of the collection
            query: Query filter (optional)
            limit: Maximum number of documents to return
            sort: Sort specification (optional)
            
        Returns:
            Dictionary containing query results and metadata
        """
        try:
            if not self.database:
                return {
                    'success': False,
                    'message': 'No active database connection',
                    'documents': [],
                    'document_count': 0,
                    'error': 'Connection not established'
                }
            
            start_time = time.time()
            
            collection = self.database[collection_name]
            query = query or {}
            
            logger.info(f"Finding documents in collection: {collection_name}")
            
            # Execute query
            cursor = collection.find(query).limit(limit)
            
            if sort:
                cursor = cursor.sort(list(sort.items()))
            
            documents = list(cursor)
            query_time = time.time() - start_time
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return {
                'success': True,
                'message': f'Found {len(documents)} documents',
                'documents': documents,
                'document_count': len(documents),
                'collection': collection_name,
                'query_time': round(query_time, 4),
                'error': None
            }
            
        except PyMongoError as e:
            logger.error(f"MongoDB find error: {str(e)}")
            return {
                'success': False,
                'message': 'Document search failed',
                'documents': [],
                'document_count': 0,
                'collection': collection_name,
                'query_time': 0,
                'error': str(e)
            }
    
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert document into MongoDB collection
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            Dictionary containing insert result and metadata
        """
        try:
            if not self.database:
                return {
                    'success': False,
                    'message': 'No active database connection',
                    'error': 'Connection not established'
                }
            
            collection = self.database[collection_name]
            
            logger.info(f"Inserting document into collection: {collection_name}")
            
            # Insert document
            result = collection.insert_one(document)
            
            return {
                'success': True,
                'message': 'Document inserted successfully',
                'inserted_id': str(result.inserted_id),
                'collection': collection_name,
                'error': None
            }
            
        except PyMongoError as e:
            logger.error(f"MongoDB insert error: {str(e)}")
            return {
                'success': False,
                'message': 'Document insertion failed',
                'inserted_id': None,
                'collection': collection_name,
                'error': str(e)
            }
    
    def update_documents(self, collection_name: str, query: Dict[str, Any], 
                        update: Dict[str, Any], upsert: bool = False) -> Dict[str, Any]:
        """
        Update documents in MongoDB collection
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            update: Update operation
            upsert: Create document if not exists
            
        Returns:
            Dictionary containing update result and metadata
        """
        try:
            if not self.database:
                return {
                    'success': False,
                    'message': 'No active database connection',
                    'error': 'Connection not established'
                }
            
            collection = self.database[collection_name]
            
            logger.info(f"Updating documents in collection: {collection_name}")
            
            # Update documents
            result = collection.update_many(query, update, upsert=upsert)
            
            return {
                'success': True,
                'message': f'Updated {result.modified_count} documents',
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_id': str(result.upserted_id) if result.upserted_id else None,
                'collection': collection_name,
                'error': None
            }
            
        except PyMongoError as e:
            logger.error(f"MongoDB update error: {str(e)}")
            return {
                'success': False,
                'message': 'Document update failed',
                'matched_count': 0,
                'modified_count': 0,
                'upserted_id': None,
                'collection': collection_name,
                'error': str(e)
            }
    
    def delete_documents(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete documents from MongoDB collection
        
        Args:
            collection_name: Name of the collection
            query: Query filter
            
        Returns:
            Dictionary containing delete result and metadata
        """
        try:
            if not self.database:
                return {
                    'success': False,
                    'message': 'No active database connection',
                    'error': 'Connection not established'
                }
            
            collection = self.database[collection_name]
            
            logger.info(f"Deleting documents from collection: {collection_name}")
            
            # Delete documents
            result = collection.delete_many(query)
            
            return {
                'success': True,
                'message': f'Deleted {result.deleted_count} documents',
                'deleted_count': result.deleted_count,
                'collection': collection_name,
                'error': None
            }
            
        except PyMongoError as e:
            logger.error(f"MongoDB delete error: {str(e)}")
            return {
                'success': False,
                'message': 'Document deletion failed',
                'deleted_count': 0,
                'collection': collection_name,
                'error': str(e)
            }
    
    def get_collection_info(self, collection_name: str = None) -> Dict[str, Any]:
        """
        Get information about MongoDB collections
        
        Args:
            collection_name: Specific collection name (optional)
            
        Returns:
            Dictionary containing collection information
        """
        try:
            if not self.database:
                return {
                    'success': False,
                    'message': 'No active database connection',
                    'error': 'Connection not established'
                }
            
            if collection_name:
                # Get specific collection info
                collection = self.database[collection_name]
                
                # Get collection stats
                stats = self.database.command("collStats", collection_name)
                
                # Get sample document to understand structure
                sample_doc = collection.find_one()
                if sample_doc and '_id' in sample_doc:
                    sample_doc['_id'] = str(sample_doc['_id'])
                
                return {
                    'success': True,
                    'collection_name': collection_name,
                    'document_count': stats.get('count', 0),
                    'average_document_size': stats.get('avgObjSize', 0),
                    'total_size': stats.get('size', 0),
                    'index_count': stats.get('nindexes', 0),
                    'sample_document': sample_doc,
                    'error': None
                }
            else:
                # Get all collections
                collection_names = self.database.list_collection_names()
                
                return {
                    'success': True,
                    'collections': collection_names,
                    'collection_count': len(collection_names),
                    'error': None
                }
                
        except PyMongoError as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to get collection information',
                'error': str(e)
            }
    
    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from MongoDB database"""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.database = None
            
            return {
                'success': True,
                'message': 'Disconnected from MongoDB successfully',
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error disconnecting from MongoDB: {str(e)}")
            return {
                'success': False,
                'message': 'Error during disconnection',
                'error': str(e)
            }

# Utility functions for database operations
def test_database_connections(mysql_config: Dict[str, Any] = None, 
                            mongodb_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test database connections"""
    results = {
        'mysql': {'available': MYSQL_AVAILABLE, 'connected': False, 'error': None},
        'mongodb': {'available': MONGODB_AVAILABLE, 'connected': False, 'error': None}
    }
    
    # Test MySQL
    if MYSQL_AVAILABLE and mysql_config:
        try:
            mysql_tool = MySQLTool(mysql_config)
            mysql_result = mysql_tool.connect()
            results['mysql']['connected'] = mysql_result['success']
            if not mysql_result['success']:
                results['mysql']['error'] = mysql_result['error']
            mysql_tool.disconnect()
        except Exception as e:
            results['mysql']['error'] = str(e)
    
    # Test MongoDB
    if MONGODB_AVAILABLE and mongodb_config:
        try:
            mongodb_tool = MongoDBTool(mongodb_config)
            mongodb_result = mongodb_tool.connect()
            results['mongodb']['connected'] = mongodb_result['success']
            if not mongodb_result['success']:
                results['mongodb']['error'] = mongodb_result['error']
            mongodb_tool.disconnect()
        except Exception as e:
            results['mongodb']['error'] = str(e)
    
    return results
