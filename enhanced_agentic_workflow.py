"""
Enhanced Agentic Workflow with Multi-Agent Coordination
"""

import json
from typing import Dict, List, Any, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from agents.coordinator_agent import CoordinatorAgent
from config import Config
import logging

logger = logging.getLogger(__name__)

class EnhancedAgentState(TypedDict):
    """Enhanced state for the multi-agent workflow"""
    query: str
    chat_history: List[BaseMessage]
    coordinator_analysis: Dict[str, Any]
    agent_responses: Dict[str, Any]
    synthesis_result: Dict[str, Any]
    final_response: str
    sources: List[Dict[str, Any]]
    current_step: str
    active_agents: List[str]
    confidence: float
    metadata: Dict[str, Any]
    error: Optional[str]

class EnhancedAgenticWorkflow:
    """Enhanced agentic workflow with multi-agent coordination"""
    
    def __init__(self, openai_api_key: str, vector_store_manager, 
                 search_config: Dict[str, Any] = None,
                 database_configs: Dict[str, Dict[str, Any]] = None):
        
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=Config.OPENAI_MODEL,
            temperature=0.1
        )
        
        # Initialize coordinator agent
        self.coordinator = CoordinatorAgent(
            openai_api_key=openai_api_key,
            vector_store_manager=vector_store_manager,
            search_config=search_config,
            database_configs=database_configs
        )
        
        self.workflow = self._create_enhanced_workflow()
    
    def _create_enhanced_workflow(self) -> StateGraph:
        """Create the enhanced multi-agent workflow graph"""
        workflow = StateGraph(EnhancedAgentState)
        
        # Add nodes for the enhanced workflow
        workflow.add_node("query_preprocessing", self._preprocess_query)
        workflow.add_node("agent_coordination", self._coordinate_agents)
        workflow.add_node("response_synthesis", self._synthesize_responses)
        workflow.add_node("quality_assurance", self._quality_assurance)
        workflow.add_node("response_formatting", self._format_final_response)
        
        # Add edges
        workflow.set_entry_point("query_preprocessing")
        workflow.add_edge("query_preprocessing", "agent_coordination")
        workflow.add_edge("agent_coordination", "response_synthesis")
        workflow.add_edge("response_synthesis", "quality_assurance")
        workflow.add_edge("quality_assurance", "response_formatting")
        workflow.add_edge("response_formatting", END)
        
        return workflow.compile()
    
    def _preprocess_query(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Preprocess and analyze the user query"""
        try:
            logger.info("Preprocessing query...")
            
            query = state["query"]
            chat_history = state.get("chat_history", [])
            
            # Enhanced query analysis
            preprocessing_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert query preprocessor. Analyze the user's query and provide:

1. Query intent and type classification
2. Key entities and concepts extraction
3. Complexity assessment
4. Context requirements
5. Expected response type
6. Any ambiguities that need clarification

Respond in JSON format with:
- intent: string (question/request/command/analysis/etc.)
- query_type: string (factual/procedural/analytical/creative/etc.)
- entities: list of key entities found
- concepts: list of main concepts
- complexity: string (simple/moderate/complex)
- context_needed: boolean
- expected_response: string (short_answer/detailed_explanation/list/analysis/etc.)
- ambiguities: list of potential ambiguities
- preprocessed_query: optimized version of the query
- confidence: float (0-1)
"""),
                ("human", """
Query: {query}

Chat History: {chat_history}

Please analyze and preprocess this query.
""")
            ])
            
            # Prepare chat history
            history_summary = ""
            if chat_history:
                for msg in chat_history[-5:]:
                    role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
                    history_summary += f"{role}: {str(msg.content)[:150]}...\n"
            
            response = self.llm.invoke(
                preprocessing_prompt.format_messages(
                    query=query,
                    chat_history=history_summary
                )
            )
            
            try:
                preprocessing_result = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback preprocessing
                preprocessing_result = {
                    "intent": "question",
                    "query_type": "general",
                    "entities": [],
                    "concepts": [query],
                    "complexity": "moderate",
                    "context_needed": bool(chat_history),
                    "expected_response": "detailed_explanation",
                    "ambiguities": [],
                    "preprocessed_query": query,
                    "confidence": 0.6
                }
            
            # Update metadata while preserving existing values
            metadata = state.get("metadata", {})
            metadata.update({
                "preprocessing": preprocessing_result,
                "original_query": query,
                "query_length": len(query),
                "has_chat_history": bool(chat_history)
            })
            state["metadata"] = metadata
            state["current_step"] = "query_preprocessing_complete"
            
            logger.info(f"Query preprocessing complete: {preprocessing_result.get('query_type', 'unknown')}")
            return state
            
        except Exception as e:
            logger.error(f"Query preprocessing error: {str(e)}")
            state["error"] = f"Query preprocessing failed: {str(e)}"
            return state
    
    def _coordinate_agents(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Coordinate multiple agents to handle the query"""
        try:
            logger.info("Coordinating agents...")
            
            query = state["query"]
            chat_history = state.get("chat_history", [])
            preprocessing = state.get("metadata", {}).get("preprocessing", {})
            
            # Prepare context for coordination
            context = {
                "preprocessing": preprocessing,
                "metadata": state.get("metadata", {}),
                "chat_history_length": len(chat_history),
                "enabled_agents": state.get("metadata", {}).get("enabled_agents", {})
            }
            
            # Use coordinator to analyze and execute agents
            coordination_result = self.coordinator.analyze_and_coordinate(
                query=query,
                context=context,
                chat_history=chat_history
            )
            
            state["coordinator_analysis"] = coordination_result.get("coordination_plan", {})
            state["agent_responses"] = coordination_result.get("agent_responses", {})
            state["active_agents"] = coordination_result.get("active_agents", [])
            state["current_step"] = "agent_coordination_complete"
            
            if not coordination_result.get("success", False):
                state["error"] = coordination_result.get("error", "Agent coordination failed")
            
            logger.info(f"Agent coordination complete: {len(state['active_agents'])} agents activated")
            return state
            
        except Exception as e:
            logger.error(f"Agent coordination error: {str(e)}")
            state["error"] = f"Agent coordination failed: {str(e)}"
            return state
    
    def _synthesize_responses(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Synthesize responses from multiple agents"""
        try:
            logger.info("Synthesizing agent responses...")
            
            query = state["query"]
            agent_responses = state.get("agent_responses", {})
            preprocessing = state.get("metadata", {}).get("preprocessing", {})
            
            if not agent_responses:
                state["error"] = "No agent responses to synthesize"
                return state
            
            # Enhanced synthesis using coordinator
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert response synthesizer. Given multiple agent responses and query analysis,
create a comprehensive, unified response that:

1. Directly addresses the user's original query
2. Integrates information from all successful agent responses
3. Maintains coherent flow and professional tone
4. Prioritizes the most relevant and accurate information
5. Provides proper attribution when citing sources
6. Acknowledges limitations or uncertainties
7. Structures information logically

Create a response that reads as a single, comprehensive answer, not separate agent outputs.
"""),
                ("human", """
Original Query: {query}

Query Analysis: {preprocessing}

Agent Responses: {agent_responses}

Please create a synthesized, comprehensive response.
""")
            ])
            
            # Filter successful responses
            successful_responses = {
                name: resp for name, resp in agent_responses.items()
                if resp.get('success', False)
            }
            
            if successful_responses:
                response = self.llm.invoke(
                    synthesis_prompt.format_messages(
                        query=query,
                        preprocessing=json.dumps(preprocessing, indent=2),
                        agent_responses=json.dumps(successful_responses, indent=2, default=str)
                    )
                )
                
                synthesis_result = {
                    "response": response.content,
                    "successful_agents": list(successful_responses.keys()),
                    "failed_agents": [name for name, resp in agent_responses.items() if not resp.get('success', False)],
                    "synthesis_confidence": len(successful_responses) / len(agent_responses) if agent_responses else 0.0
                }
            else:
                synthesis_result = {
                    "response": "I apologize, but I wasn't able to find a suitable answer to your question. Please try rephrasing or providing more specific details.",
                    "successful_agents": [],
                    "failed_agents": list(agent_responses.keys()),
                    "synthesis_confidence": 0.0
                }
            
            state["synthesis_result"] = synthesis_result
            state["current_step"] = "response_synthesis_complete"
            
            logger.info(f"Response synthesis complete: {len(synthesis_result['successful_agents'])} successful agents")
            return state
            
        except Exception as e:
            logger.error(f"Response synthesis error: {str(e)}")
            state["error"] = f"Response synthesis failed: {str(e)}"
            return state
    
    def _quality_assurance(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Perform quality assurance on the synthesized response"""
        try:
            logger.info("Performing quality assurance...")
            
            query = state["query"]
            synthesis_result = state.get("synthesis_result", {})
            agent_responses = state.get("agent_responses", {})
            
            response_text = synthesis_result.get("response", "")
            
            # Quality checks
            quality_metrics = {
                "response_length": len(response_text),
                "addresses_query": self._check_query_addressed(query, response_text),
                "coherence_score": self._assess_coherence(response_text),
                "completeness_score": self._assess_completeness(query, response_text, agent_responses),
                "source_attribution": self._check_source_attribution(response_text, agent_responses),
                "overall_quality": 0.0
            }
            
            # Calculate overall quality
            quality_factors = [
                quality_metrics["addresses_query"] * 0.3,
                quality_metrics["coherence_score"] * 0.3,
                quality_metrics["completeness_score"] * 0.2,
                quality_metrics["source_attribution"] * 0.2
            ]
            quality_metrics["overall_quality"] = sum(quality_factors)
            
            # Collect sources from all agents
            all_sources = []
            for agent_name, agent_response in agent_responses.items():
                if agent_response.get('success', False):
                    sources = agent_response.get('sources', [])
                    for source in sources:
                        if 'agent' not in source:
                            source['agent'] = agent_name
                        all_sources.append(source)
            
            state["sources"] = all_sources
            state["confidence"] = quality_metrics["overall_quality"]
            state["metadata"]["quality_metrics"] = quality_metrics
            state["current_step"] = "quality_assurance_complete"
            
            logger.info(f"Quality assurance complete: {quality_metrics['overall_quality']:.3f} score")
            return state
            
        except Exception as e:
            logger.error(f"Quality assurance error: {str(e)}")
            state["error"] = f"Quality assurance failed: {str(e)}"
            return state
    
    def _format_final_response(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Format the final response with proper structure"""
        try:
            logger.info("Formatting final response...")
            
            synthesis_result = state.get("synthesis_result", {})
            sources = state.get("sources", [])
            quality_metrics = state.get("metadata", {}).get("quality_metrics", {})
            
            response_text = synthesis_result.get("response", "")
            
            # Add metadata to response if quality is low
            if quality_metrics.get("overall_quality", 0.0) < 0.6:
                response_text += "\n\n*Note: This response may be incomplete. Consider rephrasing your question or providing more specific details.*"
            
            # Add source count if sources available
            if sources:
                response_text += f"\n\n*Based on {len(sources)} source(s) from {len(set(s.get('agent', 'unknown') for s in sources))} specialized agent(s).*"
            
            state["final_response"] = response_text
            state["current_step"] = "complete"
            
            logger.info("Final response formatting complete")
            return state
            
        except Exception as e:
            logger.error(f"Response formatting error: {str(e)}")
            state["error"] = f"Response formatting failed: {str(e)}"
            return state
    
    def _check_query_addressed(self, query: str, response: str) -> float:
        """Check if the response addresses the original query"""
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        overlap = len(query_words.intersection(response_words))
        return min(overlap / len(query_words), 1.0) if query_words else 0.0
    
    def _assess_coherence(self, response: str) -> float:
        """Assess response coherence"""
        if not response:
            return 0.0
        
        # Simple coherence metrics
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.5
        
        # Check for proper punctuation and structure
        has_proper_punctuation = any(punct in response for punct in ['.', '!', '?'])
        has_proper_length = 50 <= len(response) <= 2000
        
        coherence_score = 0.3
        if has_proper_punctuation:
            coherence_score += 0.3
        if has_proper_length:
            coherence_score += 0.4
        
        return min(coherence_score, 1.0)
    
    def _assess_completeness(self, query: str, response: str, agent_responses: Dict[str, Any]) -> float:
        """Assess response completeness"""
        completeness_score = 0.5  # Base score
        
        # Check if multiple agents contributed
        successful_agents = sum(1 for resp in agent_responses.values() if resp.get('success', False))
        if successful_agents > 1:
            completeness_score += 0.2
        
        # Check response length adequacy
        if len(response) > 100:
            completeness_score += 0.2
        
        # Check if response has structure
        if any(indicator in response for indicator in [':', '\n', '1.', '2.', '-']):
            completeness_score += 0.1
        
        return min(completeness_score, 1.0)
    
    def _check_source_attribution(self, response: str, agent_responses: Dict[str, Any]) -> float:
        """Check for proper source attribution"""
        has_sources = any(
            resp.get('sources', []) for resp in agent_responses.values() 
            if resp.get('success', False)
        )
        
        # If sources are available, check if response acknowledges them
        if has_sources:
            attribution_indicators = ['source', 'based on', 'according to', 'from', 'reference']
            has_attribution = any(indicator in response.lower() for indicator in attribution_indicators)
            return 0.8 if has_attribution else 0.4
        
        return 0.6  # Neutral score if no sources available
    
    def run_enhanced_workflow(self, query: str, chat_history: List[BaseMessage] = None, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the complete enhanced agentic workflow"""
        try:
            logger.info(f"Running enhanced agentic workflow for query: {query[:50]}...")
            
            # Initialize enhanced state
            initial_state = EnhancedAgentState(
                query=query,
                chat_history=chat_history or [],
                coordinator_analysis={},
                agent_responses={},
                synthesis_result={},
                final_response="",
                sources=[],
                current_step="initialized",
                active_agents=[],
                confidence=0.0,
                metadata=context or {},
                error=None
            )
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Format results
            results = {
                "response": final_state.get("final_response", ""),
                "sources": final_state.get("sources", []),
                "confidence": final_state.get("confidence", 0.0),
                "active_agents": final_state.get("active_agents", []),
                "agent_responses": final_state.get("agent_responses", {}),
                "synthesis_result": final_state.get("synthesis_result", {}),
                "coordinator_analysis": final_state.get("coordinator_analysis", {}),
                "metadata": final_state.get("metadata", {}),
                "current_step": final_state.get("current_step", "unknown"),
                "error": final_state.get("error"),
                "success": final_state.get("error") is None
            }
            
            logger.info(f"Enhanced workflow completed: {results['current_step']}")
            return results
            
        except Exception as e:
            logger.error(f"Enhanced workflow error: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error while processing your query.",
                "sources": [],
                "confidence": 0.0,
                "active_agents": [],
                "agent_responses": {},
                "synthesis_result": {},
                "coordinator_analysis": {},
                "metadata": {},
                "current_step": "error",
                "error": str(e),
                "success": False
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return self.coordinator.get_agent_status()
    
    def reset_workflow(self) -> Dict[str, Any]:
        """Reset workflow and all agents"""
        return self.coordinator.reset_agents()
