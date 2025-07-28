"""
Database Chat Interface using Streamlit
"""

import streamlit as st
from typing import Dict, Any
import json
import pandas as pd
from .database_agent import DatabaseAgent
from config import Config

class DatabaseChat:
    def __init__(self, database_agent: DatabaseAgent):
        self.agent = database_agent
        self.initialize_session_state()

    @staticmethod
    def initialize_session_state():
        """Initialize session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'database_info' not in st.session_state:
            st.session_state.database_info = None

    def display_database_info(self):
        """Display available database information"""
        if not st.session_state.database_info:
            st.session_state.database_info = self.agent.get_database_info()
        
        st.sidebar.header("Database Information")
        
        # MySQL Info
        mysql_info = st.session_state.database_info.get('mysql', {})
        if mysql_info.get('available'):
            st.sidebar.subheader("MySQL Database")
            if mysql_info.get('connected'):
                st.sidebar.success("Connected")
                if mysql_info.get('info'):
                    st.sidebar.write("Available Tables:")
                    for table_info in mysql_info['info']:
                        with st.sidebar.expander(table_info['table_name']):
                            st.write("Columns:")
                            for col in table_info['columns']:
                                st.write(f"- {col['name']} ({col['type']})")
            else:
                st.sidebar.warning("Not Connected")

        # MongoDB Info
        mongo_info = st.session_state.database_info.get('mongodb', {})
        if mongo_info.get('available'):
            st.sidebar.subheader("MongoDB Database")
            if mongo_info.get('connected'):
                st.sidebar.success("Connected")
                if mongo_info.get('info'):
                    st.sidebar.write("Available Collections:")
                    for collection in mongo_info['info']:
                        st.sidebar.write(f"- {collection}")
            else:
                st.sidebar.warning("Not Connected")

    def format_database_response(self, response: Dict[str, Any]) -> str:
        """Format database response for display"""
        if not response.get('success', False):
            return f"❌ Error: {response.get('error', 'Unknown error occurred')}"

        formatted = "✅ Query Results:\n\n"
        
        if 'results' in response:
            if isinstance(response['results'], list):
                if response['results']:
                    # For SELECT queries with results
                    import pandas as pd
                    df = pd.DataFrame(response['results'])
                    return df
                else:
                    return "No results found."
            else:
                # For other operations (INSERT, UPDATE, DELETE)
                return f"Operation completed successfully.\nAffected rows: {response.get('row_count', 0)}"
        
        return formatted + json.dumps(response, indent=2)

    def render_chat_interface(self):
        """Render the main chat interface"""
        st.title("💬 Database Chat Interface")
        st.write("Ask questions about your data in plain English!")

        # Display database information in sidebar
        self.display_database_info()

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], (pd.DataFrame, pd.Series)):
                    st.dataframe(message["content"])
                else:
                    st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask about your data..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from database agent
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # First analyze the request
                    analysis = self.agent.analyze_request(prompt)
                    
                    if analysis.get('requires_database', False):
                        # Execute database operation
                        response = self.agent.execute_database_operation(prompt)
                        formatted_response = self.format_database_response(response)
                        
                        # Add response to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": formatted_response
                        })
                        
                        # Display response
                        if isinstance(formatted_response, (pd.DataFrame, pd.Series)):
                            st.dataframe(formatted_response)
                        else:
                            st.markdown(formatted_response)
                    else:
                        message = ("I don't see how I can help with this using the database. "
                                 "Could you please rephrase your question to ask about specific data? "
                                 "For example:\n"
                                 "- Show me all users\n"
                                 "- Find products with price > 100\n"
                                 "- Count orders by status")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": message
                        })
                        st.markdown(message)

def create_database_chat(openai_api_key: str, database_configs: Dict[str, Dict[str, Any]] = None):
    """Create and return a DatabaseChat instance"""
    agent = DatabaseAgent(openai_api_key=openai_api_key, database_configs=database_configs)
    return DatabaseChat(agent)
