
"""
Coordinator Agent for orchestrating multiple specialized agents
"""

import json
from typing import Dict, Any, List, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from agents.calculator_agent import CalculatorAgent
from agents.search_agent import SearchAgent
from agents.database_agent import DatabaseAgent
from agents.rag_agent import RAGAgent
from config import Config
import logging

logger = logging.getLogger(__name__)

class CoordinatorState(TypedDict):
    """State for agent coordination"""
    query: str
    chat_history: List[BaseMessage]
    analysis_results: Dict[str, Any]
    agent_responses: Dict[str, Any]
    final_response: str
    sources: List[Dict[str, Any]]
    confidence: float
    active_agents: List[str]
    coordination_plan: Dict[str, Any]
    error: Optional[str]

class CoordinatorAgent:
    """Agent that coordinates and orchestrates multiple specialized agents"""
    
    def __init__(self, openai_api_key: str, vector_store_manager, 
                 search_config: Dict[str, Any] = None, 
                 database_configs: Dict[str, Dict[str, Any]] = None):
        
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=Config.OPENAI_MODEL,
            temperature=0.1
        )
        
        # Initialize specialized agents
        self.calculator_agent = CalculatorAgent(openai_api_key)
        self.search_agent = SearchAgent(openai_api_key, search_config)
        self.database_agent = DatabaseAgent(openai_api_key, database_configs)
        self.rag_agent = RAGAgent(openai_api_key, vector_store_manager)
        
        self.agent_name = "Coordinator Agent"
        self.available_agents = {
            'calculator': self.calculator_agent,
            'search': self.search_agent,
            'database': self.database_agent,
            'rag': self.rag_agent
        }
        
        self.capabilities = [
            "Multi-agent coordination and orchestration",
            "Task decomposition and assignment",
            "Response synthesis and integration",
            "Conflict resolution between agents",
            "Optimal agent selection and routing"
        ]
    
    def analyze_and_coordinate(self, query: str, context: Dict[str, Any] = None, 
                              chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """
        Analyze query and coordinate appropriate agents
        
        Args:
            query: User query
            context: Additional context
            chat_history: Previous chat messages
            
        Returns:
            Dictionary containing coordinated response
        """
        try:
            logger.info(f"Coordinating agents for query: {query[:50]}...")
            
            # Step 1: Analyze query and determine required agents
            coordination_plan = self._create_coordination_plan(query, context, chat_history)
            
            if not coordination_plan['success']:
                return {
                    'success': False,
                    'query': query,
                    'response': "I couldn't analyze your query properly. Please try rephrasing it.",
                    'sources': [],
                    'agent_responses': {},
                    'coordination_plan': coordination_plan,
                    'confidence': 0.0,
                    'error': coordination_plan.get('error', 'Analysis failed')
                }
            
            # Step 2: Execute agent tasks in parallel or sequence
            agent_responses = self._execute_agent_tasks(
                query, coordination_plan['plan'], context, chat_history
            )
            
            # Step 3: Synthesize responses
            synthesis_result = self._synthesize_agent_responses(
                query, agent_responses, coordination_plan['plan'], context
            )
            
            return {
                'success': True,
                'query': query,
                'response': synthesis_result['response'],
                'sources': synthesis_result['sources'],
                'agent_responses': agent_responses,
                'coordination_plan': coordination_plan,
                'confidence': synthesis_result['confidence'],
                'active_agents': list(agent_responses.keys()),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Coordination error: {str(e)}")
            return {
                'success': False,
                'query': query,
                'response': f"I encountered an error while processing your request: {str(e)}",
                'sources': [],
                'agent_responses': {},
                'coordination_plan': {},
                'confidence': 0.0,
                'active_agents': [],
                'error': str(e)
            }
    
    def _create_coordination_plan(self, query: str, context: Dict[str, Any] = None, 
                                 chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """Create a coordination plan for agent execution"""
        try:
            # Get enabled agents from context
            enabled_agents = context.get('enabled_agents', {}) if context else {}
            enable_calculator = enabled_agents.get('calculator', False)
            
            # Get analysis from enabled agents
            agent_analyses = {}
            
            # Only analyze with enabled agents
            if enabled_agents.get('calculator', False):
                agent_analyses['calculator'] = self.calculator_agent.analyze_request(query)
            if enabled_agents.get('search', False):
                agent_analyses['search'] = self.search_agent.analyze_request(query)
            if enabled_agents.get('database', False):
                agent_analyses['database'] = self.database_agent.analyze_request(query)
            # Use RAG only if no other agents are enabled
            if not any(enabled_agents.values()):
                agent_analyses['rag'] = self.rag_agent.analyze_request(query)
            
            # Create coordination plan using LLM
            coordination_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert agent coordinator. Given a user query and individual agent analyses, 
create an optimal coordination plan that:

1. Determines which agents should be activated
2. Defines the order of execution (parallel vs sequential)
3. Identifies dependencies between agents
4. Assigns priority levels to different agents
5. Plans for response synthesis

Respond in JSON format with:
- agents_to_activate: list of agent names to use
- execution_order: "parallel" or "sequential" or specific order
- agent_priorities: dict with agent names and priority scores (1-5)
- dependencies: dict showing which agents depend on others
- synthesis_strategy: how to combine responses
- estimated_complexity: overall task complexity (low/medium/high)
- reasoning: explanation of the coordination strategy
"""),
                ("human", """
User Query: {query}

Agent Analyses:
{analyses}

Context: {context}

Chat History: {chat_history}

Please create an optimal coordination plan.
""")
            ])
            
            # Prepare chat history summary
            history_summary = ""
            if chat_history:
                for msg in chat_history[-3:]:
                    role = "Human" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                    history_summary += f"{role}: {str(msg.content)[:100]}...\n"
            
            response = self.llm.invoke(
                coordination_prompt.format_messages(
                    query=query,
                    analyses=json.dumps(agent_analyses, indent=2),
                    context=json.dumps(context or {}, indent=2),
                    chat_history=history_summary
                )
            )
            
            # Handle different response types
            if isinstance(response, dict):
                response_text = response.get('content', str(response))
            elif hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
                
            try:
                plan = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback plan based on enabled agents
                activated_agents = []
                
                # Only activate enabled agents that indicate they can help
                for agent_name, analysis in agent_analyses.items():
                    if agent_name == 'calculator' and enabled_agents.get('calculator', False) and analysis.get('requires_calculation', False):
                        activated_agents.append(agent_name)
                    elif agent_name == 'search' and enabled_agents.get('search', False) and (analysis.get('requires_search', False) or any(word in query.lower() for word in ['current', 'latest', 'today'])):
                        activated_agents.append(agent_name)
                    elif agent_name == 'database' and enabled_agents.get('database', False) and analysis.get('requires_database', False):
                        activated_agents.append(agent_name)
                    elif agent_name == 'rag' and not any(enabled_agents.values()) and analysis.get('requires_rag', False):
                        activated_agents.append(agent_name)
                
                # Default to enabled agents if none were activated by analysis
                if not activated_agents:
                    if enabled_agents.get('calculator', False):
                        activated_agents = ['calculator']
                    elif enabled_agents.get('search', False):
                        activated_agents = ['search']
                    elif enabled_agents.get('database', False):
                        activated_agents = ['database']
                    else:
                        activated_agents = ['rag']
                
                # Set priorities based on query type
                priorities = {}
                for agent in activated_agents:
                    if agent == 'calculator':
                        priorities[agent] = 5 if any(word in query.lower() for word in ['calculate', 'compute', 'sum']) else 3
                    elif agent == 'search':
                        priorities[agent] = 5 if any(word in query.lower() for word in ['current', 'latest', 'today']) else 3
                    elif agent == 'database':
                        priorities[agent] = 5 if any(word in query.lower() for word in ['list', 'show', 'find', 'query']) else 3
                    else:
                        priorities[agent] = 3
                
                # Check if query needs current/real-time info
                needs_current = any(word in query.lower() for word in ['current', 'latest', 'today', 'now'])
                
                plan = {
                    "agents_to_activate": activated_agents,
                    "execution_order": "sequential" if needs_current else "parallel",
                    "agent_priorities": priorities,
                    "dependencies": {},
                    "synthesis_strategy": "prioritize_current" if needs_current else "combine_all",
                    "estimated_complexity": "simple" if needs_current else "medium",
                    "reasoning": "Prioritizing current information" if needs_current else "Fallback coordination plan"
                }
            
            return {
                'success': True,
                'plan': plan,
                'agent_analyses': agent_analyses,
                'total_agents_available': len(self.available_agents),
                'agents_to_activate': len(plan.get('agents_to_activate', [])),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Coordination planning error: {str(e)}")
            return {
                'success': False,
                'plan': {},
                'agent_analyses': {},
                'total_agents_available': 0,
                'agents_to_activate': 0,
                'error': str(e)
            }
    
    def _execute_agent_tasks(self, query: str, plan: Dict[str, Any], 
                            context: Dict[str, Any] = None, 
                            chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """Execute tasks across multiple agents based on the plan"""
        agent_responses = {}
        agents_to_activate = plan.get('agents_to_activate', [])
        execution_order = plan.get('execution_order', 'parallel')
        
        try:
            if execution_order == 'parallel':
                # Execute all agents in parallel
                for agent_name in agents_to_activate:
                    try:
                        agent_responses[agent_name] = self._execute_single_agent(
                            agent_name, query, context, chat_history
                        )
                    except Exception as e:
                        logger.error(f"Error executing {agent_name}: {str(e)}")
                        agent_responses[agent_name] = {
                            'success': False,
                            'error': str(e),
                            'agent': agent_name
                        }
            
            elif execution_order == 'sequential':
                # Execute agents in priority order
                priorities = plan.get('agent_priorities', {})
                sorted_agents = sorted(
                    agents_to_activate, 
                    key=lambda x: priorities.get(x, 0), 
                    reverse=True
                )
                
                for agent_name in sorted_agents:
                    try:
                        # Pass previous results as context for sequential execution
                        enhanced_context = context or {}
                        enhanced_context['previous_agent_responses'] = agent_responses
                        
                        agent_responses[agent_name] = self._execute_single_agent(
                            agent_name, query, enhanced_context, chat_history
                        )
                    except Exception as e:
                        logger.error(f"Error executing {agent_name}: {str(e)}")
                        agent_responses[agent_name] = {
                            'success': False,
                            'error': str(e),
                            'agent': agent_name
                        }
            
            else:
                # Custom execution order (list of agent names)
                if isinstance(execution_order, list):
                    for agent_name in execution_order:
                        if agent_name in agents_to_activate:
                            try:
                                enhanced_context = context or {}
                                enhanced_context['previous_agent_responses'] = agent_responses
                                
                                agent_responses[agent_name] = self._execute_single_agent(
                                    agent_name, query, enhanced_context, chat_history
                                )
                            except Exception as e:
                                logger.error(f"Error executing {agent_name}: {str(e)}")
                                agent_responses[agent_name] = {
                                    'success': False,
                                    'error': str(e),
                                    'agent': agent_name
                                }
            
            return agent_responses
            
        except Exception as e:
            logger.error(f"Agent execution error: {str(e)}")
            return {}
    
    def _execute_single_agent(self, agent_name: str, query: str, 
                             context: Dict[str, Any] = None, 
                             chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """Execute a single agent task"""
        try:
            agent = self.available_agents.get(agent_name)
            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_name} not available',
                    'agent': agent_name
                }
            
            logger.info(f"Executing {agent_name} agent...")
            
            if agent_name == 'calculator':
                return agent.solve_problem(query, context)
            elif agent_name == 'search':
                return agent.search_and_analyze(query, context)
            elif agent_name == 'database':
                return agent.execute_database_operation(query, context)
            elif agent_name == 'rag':
                return agent.process_rag_query(query, context, chat_history)
            else:
                return {
                    'success': False,
                    'error': f'Unknown agent execution method for {agent_name}',
                    'agent': agent_name
                }
                
        except Exception as e:
            logger.error(f"Single agent execution error ({agent_name}): {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': agent_name
            }
    
    def _synthesize_agent_responses(self, query: str, agent_responses: Dict[str, Any], 
                                   plan: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Synthesize responses from multiple agents into a cohesive answer"""
        try:
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert response synthesizer. Given a user query and responses from multiple specialized agents, 
create a comprehensive, cohesive response that:

1. Directly answers the user's query
2. Integrates information from all successful agent responses
3. Maintains logical flow and coherence
4. Highlights the most important and relevant information
5. Attributes information to appropriate sources/agents
6. Acknowledges any limitations or conflicting information
7. Provides a clear, actionable answer

Structure your response professionally and ensure it reads as a unified answer, not separate responses.
"""),
                ("human", """
User Query: {query}

Agent Responses: {responses}

Coordination Plan: {plan}

Context: {context}

Please provide a comprehensive, synthesized response.
""")
            ])
            
            # Filter successful responses
            successful_responses = {
                name: resp for name, resp in agent_responses.items() 
                if resp.get('success', False)
            }
            
            if not successful_responses:
                return {
                    'response': "I couldn't find a suitable way to answer your question. Please try rephrasing or providing more specific details.",
                    'sources': [],
                    'confidence': 0.0,
                    'successful_agents': [],
                    'total_sources': 0
                }
                
            # Format messages for synthesis
            formatted_messages = synthesis_prompt.format_messages(
                query=query,
                responses=json.dumps(successful_responses, indent=2, default=str),
                plan=json.dumps(plan, indent=2),
                context=json.dumps(context or {}, indent=2)
            )
            
            # Get response from LLM
            response = self.llm.invoke(formatted_messages)
            
            # Handle different response types
            if isinstance(response, dict):
                response_content = response.get('content', str(response))
            elif hasattr(response, 'content'):
                response_content = response.content
            elif isinstance(response, str):
                response_content = response
            else:
                response_content = str(response)
                
            # Extract sources from agent responses
            sources = []
            for agent_name, resp in successful_responses.items():
                if resp.get('sources'):
                    for source in resp['sources']:
                        if isinstance(source, dict):
                            source['agent'] = agent_name
                            sources.append(source)
                        else:
                            sources.append({
                                'content': str(source),
                                'agent': agent_name
                            })
            
            return {
                'response': response_content,
                'sources': sources,
                'confidence': 0.8 if successful_responses else 0.0,
                'successful_agents': list(successful_responses.keys()),
                'total_sources': len(sources)
            }
            
        except Exception as e:
            logger.error(f"Response synthesis error: {str(e)}")
            return {
                'response': f"I encountered an error while synthesizing the response: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'successful_agents': [],
                'total_sources': 0
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all available agents"""
        status = {}
        
        for agent_name, agent in self.available_agents.items():
            try:
                capabilities = agent.get_capabilities()
                status[agent_name] = {
                    'available': True,
                    'capabilities': capabilities,
                    'agent_class': agent.__class__.__name__
                }
            except Exception as e:
                status[agent_name] = {
                    'available': False,
                    'error': str(e),
                    'agent_class': agent.__class__.__name__
                }
        
        return status
    
    def get_coordination_capabilities(self) -> List[str]:
        """Get coordination capabilities"""
        return self.capabilities.copy()
    
    def reset_agents(self) -> Dict[str, Any]:
        """Reset all agents to initial state"""
        results = {}
        
        # Reset database connections
        if hasattr(self.database_agent, 'disconnect_all'):
            results['database_disconnections'] = self.database_agent.disconnect_all()
        
        # Other agents don't need explicit reset, but we can add logging
        for agent_name in self.available_agents.keys():
            results[f'{agent_name}_reset'] = {'success': True, 'message': 'Agent reset completed'}
        
        return results
