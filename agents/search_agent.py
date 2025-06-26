
"""
Search Agent for internet search and information retrieval
"""

import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from tools.search_tool import InternetSearchTool
from config import Config
import logging

logger = logging.getLogger(__name__)

class SearchAgent:
    """Agent specialized in internet search and information retrieval"""
    
    def __init__(self, openai_api_key: str, search_config: Dict[str, Any] = None):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=Config.OPENAI_MODEL,
            temperature=0.1
        )
        self.search_tool = InternetSearchTool(search_config or {})
        self.agent_name = "Search Agent"
        self.capabilities = [
            "Internet search and information retrieval",
            "Real-time information gathering",
            "Multiple search provider support",
            "Result summarization and analysis",
            "Source verification and ranking"
        ]
    
    def analyze_request(self, request: str) -> Dict[str, Any]:
        """
        Analyze if the request requires internet search
        
        Args:
            request: User request to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert search analysis agent. Analyze the user's request to determine:

1. Whether it requires internet search for current/recent information
2. Type of search needed (factual, news, research, specific topic, etc.)
3. Extract search keywords and phrases
4. Identify what specific information is being sought
5. Determine search complexity and scope
6. Assess if the information might be time-sensitive

Respond in JSON format with these fields:
- requires_search: boolean
- search_type: string (factual/news/research/academic/product/etc.)
- search_queries: list of optimized search queries
- information_needed: list of specific information types sought
- time_sensitivity: string (current/recent/historical/any)
- complexity: string (simple/moderate/complex)
- confidence: float (0-1)
- reasoning: string explaining the analysis
"""),
                ("human", "Request: {request}")
            ])
            
            response = self.llm.invoke(
                analysis_prompt.format_messages(request=request)
            )
            
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback analysis
                search_keywords = ['latest', 'current', 'recent', 'news', 'today', 'now', 
                                 'search', 'find', 'lookup', 'what is', 'who is', 'when', 
                                 'where', 'how', 'information about', 'tell me about']
                
                needs_search = any(keyword in request.lower() for keyword in search_keywords)
                
                analysis = {
                    "requires_search": needs_search,
                    "search_type": "general" if needs_search else "none",
                    "search_queries": [request] if needs_search else [],
                    "information_needed": ["general information"],
                    "time_sensitivity": "any",
                    "complexity": "moderate" if needs_search else "none",
                    "confidence": 0.7 if needs_search else 0.3,
                    "reasoning": "Fallback analysis based on keyword detection"
                }
            
            logger.info(f"Search analysis: {analysis.get('requires_search', False)}")
            return analysis
            
        except Exception as e:
            logger.error(f"Search analysis error: {str(e)}")
            return {
                "requires_search": False,
                "search_type": "error",
                "search_queries": [],
                "information_needed": [],
                "time_sensitivity": "any",
                "complexity": "error",
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}"
            }
    
    def search_and_analyze(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform internet search and analyze results
        
        Args:
            query: Search query
            context: Additional context for the search
            
        Returns:
            Dictionary containing search results and analysis
        """
        try:
            logger.info(f"Performing search for: {query}")
            
            # Optimize search query based on context
            optimized_query = self._optimize_search_query(query, context)
            
            # Perform search
            search_results = self.search_tool.search(
                query=optimized_query,
                num_results=8,
                provider='auto'
            )
            
            if not search_results['success']:
                return {
                    'success': False,
                    'query': query,
                    'optimized_query': optimized_query,
                    'search_results': [],
                    'analysis': {},
                    'summary': "Search failed",
                    'agent': self.agent_name,
                    'error': search_results.get('error', 'Unknown search error')
                }
            
            # Analyze and summarize results
            analysis = self._analyze_search_results(search_results['results'], query, context)
            
            # Generate comprehensive summary
            summary = self._generate_search_summary(search_results['results'], query, analysis)
            
            return {
                'success': True,
                'query': query,
                'optimized_query': optimized_query,
                'search_results': search_results['results'],
                'analysis': analysis,
                'summary': summary,
                'provider': search_results.get('provider', 'unknown'),
                'total_results': search_results.get('total_results', 0),
                'agent': self.agent_name,
                'confidence': analysis.get('overall_confidence', 0.5),
                'sources': [{
                    'type': 'web',
                    'title': result.get('title', 'Unknown'),
                    'url': result.get('url', ''),
                    'domain': result.get('metadata', {}).get('domain', 'unknown'),
                    'confidence': result.get('metadata', {}).get('confidence', 0.5)
                } for result in search_results['results']],
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Search and analysis error: {str(e)}")
            return {
                'success': False,
                'query': query,
                'optimized_query': query,
                'search_results': [],
                'analysis': {},
                'summary': f"Search analysis failed: {str(e)}",
                'agent': self.agent_name,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _optimize_search_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Optimize search query for better results"""
        try:
            optimization_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert search query optimizer. Given a user query and context, 
create an optimized search query that will yield the best results. Consider:

1. Add relevant keywords that improve search accuracy
2. Remove ambiguous terms
3. Include synonyms or alternative terms
4. Consider time sensitivity (add date constraints if needed)
5. Focus on the core information need

Return only the optimized search query, nothing else.
"""),
                ("human", """
Original Query: {query}
Context: {context}

Optimized Query:""")
            ])
            
            response = self.llm.invoke(
                optimization_prompt.format_messages(
                    query=query,
                    context=json.dumps(context or {}, indent=2)
                )
            )
            
            optimized = response.content.strip()
            return optimized if optimized else query
            
        except Exception as e:
            logger.error(f"Query optimization error: {str(e)}")
            return query
    
    def _analyze_search_results(self, results: List[Dict[str, Any]], query: str, 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze search results for relevance and quality"""
        try:
            if not results:
                return {
                    'overall_confidence': 0.0,
                    'result_quality': 'poor',
                    'key_findings': [],
                    'source_diversity': 0.0,
                    'information_completeness': 0.0
                }
            
            # Calculate metrics
            total_relevance = sum(result.get('relevance_score', 0) for result in results)
            avg_relevance = total_relevance / len(results)
            
            # Source diversity
            unique_domains = set()
            for result in results:
                domain = result.get('metadata', {}).get('domain', 'unknown')
                unique_domains.add(domain)
            source_diversity = len(unique_domains) / len(results)
            
            # Extract key findings
            key_findings = []
            for result in results[:5]:  # Top 5 results
                if result.get('snippet') and len(result['snippet']) > 50:
                    key_findings.append({
                        'finding': result['snippet'][:200] + '...' if len(result['snippet']) > 200 else result['snippet'],
                        'source': result.get('source', 'Unknown'),
                        'relevance': result.get('relevance_score', 0),
                        'confidence': result.get('metadata', {}).get('confidence', 0.5)
                    })
            
            # Overall confidence calculation
            confidence_factors = [
                avg_relevance * 0.4,
                source_diversity * 0.3,
                min(len(results) / 5, 1.0) * 0.2,  # Result count factor
                min(len(key_findings) / 3, 1.0) * 0.1  # Findings factor
            ]
            overall_confidence = sum(confidence_factors)
            
            # Determine result quality
            if overall_confidence >= 0.8:
                quality = 'excellent'
            elif overall_confidence >= 0.6:
                quality = 'good'
            elif overall_confidence >= 0.4:
                quality = 'fair'
            else:
                quality = 'poor'
            
            return {
                'overall_confidence': overall_confidence,
                'result_quality': quality,
                'key_findings': key_findings,
                'source_diversity': source_diversity,
                'information_completeness': min(len(key_findings) / 5, 1.0),
                'average_relevance': avg_relevance,
                'total_results': len(results)
            }
            
        except Exception as e:
            logger.error(f"Result analysis error: {str(e)}")
            return {
                'overall_confidence': 0.0,
                'result_quality': 'error',
                'key_findings': [],
                'source_diversity': 0.0,
                'information_completeness': 0.0,
                'error': str(e)
            }
    
    def _generate_search_summary(self, results: List[Dict[str, Any]], query: str, 
                               analysis: Dict[str, Any]) -> str:
        """Generate comprehensive summary of search results"""
        try:
            summary_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert information synthesizer. Given search results and analysis, 
create a comprehensive summary that:

1. Answers the original query directly
2. Synthesizes key information from multiple sources
3. Highlights important findings and insights
4. Notes any conflicting information
5. Provides source attribution for key claims
6. Assesses information reliability

Structure your response clearly and be concise yet comprehensive.
"""),
                ("human", """
Original Query: {query}

Search Results: {results}

Analysis: {analysis}

Please provide a comprehensive summary that answers the query and synthesizes the key information found.
""")
            ])
            
            # Prepare results summary for LLM
            results_summary = ""
            for i, result in enumerate(results[:10]):  # Top 10 results
                results_summary += f"\n--- Result {i+1} ---\n"
                results_summary += f"Title: {result.get('title', 'Unknown')}\n"
                results_summary += f"Source: {result.get('source', 'Unknown')}\n"
                results_summary += f"Relevance: {result.get('relevance_score', 0):.3f}\n"
                results_summary += f"Content: {result.get('snippet', 'No content')[:300]}...\n"
            
            response = self.llm.invoke(
                summary_prompt.format_messages(
                    query=query,
                    results=results_summary,
                    analysis=json.dumps(analysis, indent=2)
                )
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return f"Unable to generate detailed summary. Found {len(results)} results for query: {query}"
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities.copy()
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported search features"""
        return self.search_tool.get_supported_features()
