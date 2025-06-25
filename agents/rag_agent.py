
"""
Enhanced RAG Agent for document-based question answering
"""

import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from config import Config
import logging

logger = logging.getLogger(__name__)

class RAGAgent:
    """Enhanced RAG agent with improved document processing and answer generation"""
    
    def __init__(self, openai_api_key: str, vector_store_manager):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=Config.OPENAI_MODEL,
            temperature=0.1
        )
        self.vector_store_manager = vector_store_manager
        self.agent_name = "RAG Agent"
        self.capabilities = [
            "Document-based question answering",
            "Semantic search and retrieval",
            "Context synthesis and analysis",
            "Multi-document reasoning",
            "Source attribution and citation"
        ]
    
    def analyze_request(self, request: str) -> Dict[str, Any]:
        """
        Analyze if the request requires RAG (document-based) processing
        
        Args:
            request: User request to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert document analysis agent. Analyze the user's request to determine:

1. Whether it requires document-based information retrieval (RAG)
2. Type of information needed (factual, analytical, comparative, summary, etc.)
3. Scope of search (specific documents, broad search, recent documents, etc.)
4. Complexity of reasoning required (simple lookup, multi-step analysis, synthesis)
5. Whether the request needs current/updated information vs historical documents

Respond in JSON format with these fields:
- requires_rag: boolean
- information_type: string (factual/analytical/comparative/summary/etc.)
- search_scope: string (specific/broad/recent/all)
- reasoning_complexity: string (simple/moderate/complex)
- needs_current_info: boolean
- key_concepts: list of key concepts to search for
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
                doc_keywords = ['document', 'file', 'paper', 'report', 'article', 'content',
                               'information', 'details', 'explain', 'describe', 'summarize',
                               'what is', 'how does', 'tell me about', 'find information']
                
                needs_rag = any(keyword in request.lower() for keyword in doc_keywords)
                
                analysis = {
                    "requires_rag": needs_rag,
                    "information_type": "factual" if needs_rag else "none",
                    "search_scope": "broad" if needs_rag else "none",
                    "reasoning_complexity": "moderate" if needs_rag else "none",
                    "needs_current_info": False,
                    "key_concepts": [request] if needs_rag else [],
                    "confidence": 0.7 if needs_rag else 0.3,
                    "reasoning": "Fallback analysis based on keyword detection"
                }
            
            logger.info(f"RAG analysis: {analysis.get('requires_rag', False)}")
            return analysis
            
        except Exception as e:
            logger.error(f"RAG analysis error: {str(e)}")
            return {
                "requires_rag": False,
                "information_type": "error",
                "search_scope": "none",
                "reasoning_complexity": "error",
                "needs_current_info": False,
                "key_concepts": [],
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}"
            }
    
    def process_rag_query(self, query: str, context: Dict[str, Any] = None, 
                         chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """
        Process RAG query with enhanced document retrieval and analysis
        
        Args:
            query: User query
            context: Additional context for the query
            chat_history: Previous chat messages for context
            
        Returns:
            Dictionary containing RAG results and analysis
        """
        try:
            logger.info(f"Processing RAG query: {query[:50]}...")
            
            # Analyze the query
            analysis = self.analyze_request(query)
            
            if not analysis.get('requires_rag', False):
                return {
                    'success': False,
                    'message': 'Query does not require document-based processing',
                    'query': query,
                    'response': "This query doesn't seem to require information from documents. Consider using other tools for this type of request.",
                    'sources': [],
                    'agent': self.agent_name,
                    'confidence': 0.0,
                    'error': 'No RAG processing needed'
                }
            
            # Enhanced document search
            search_results = self._enhanced_document_search(query, analysis, context)
            
            if not search_results['success']:
                return {
                    'success': False,
                    'message': 'Document search failed',
                    'query': query,
                    'response': "I couldn't find relevant documents to answer your question.",
                    'sources': [],
                    'agent': self.agent_name,
                    'confidence': 0.0,
                    'error': search_results.get('error', 'Search failed')
                }
            
            # Enhanced context synthesis
            synthesis_result = self._enhanced_context_synthesis(
                search_results['documents'], query, analysis, context
            )
            
            # Generate enhanced response
            response_result = self._generate_enhanced_response(
                query, synthesis_result, search_results['documents'], 
                analysis, context, chat_history
            )
            
            return {
                'success': True,
                'message': 'RAG processing completed successfully',
                'query': query,
                'response': response_result['response'],
                'sources': response_result['sources'],
                'analysis': analysis,
                'synthesis': synthesis_result,
                'search_metadata': search_results['metadata'],
                'agent': self.agent_name,
                'confidence': response_result['confidence'],
                'error': None
            }
            
        except Exception as e:
            logger.error(f"RAG processing error: {str(e)}")
            return {
                'success': False,
                'message': 'RAG processing failed',
                'query': query,
                'response': f"I encountered an error while processing your query: {str(e)}",
                'sources': [],
                'agent': self.agent_name,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _enhanced_document_search(self, query: str, analysis: Dict[str, Any], 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced document search with improved ranking and filtering"""
        try:
            # Determine search parameters based on analysis
            complexity = analysis.get('reasoning_complexity', 'moderate')
            search_scope = analysis.get('search_scope', 'broad')
            
            # Adjust search parameters
            if complexity == 'complex':
                k = 12
                score_threshold = 0.05
            elif complexity == 'simple':
                k = 5
                score_threshold = 0.2
            else:
                k = 8
                score_threshold = 0.1
            
            # Perform similarity search
            search_results = self.vector_store_manager.similarity_search(
                query=query,
                k=k,
                score_threshold=score_threshold
            )
            
            if not search_results:
                return {
                    'success': False,
                    'documents': [],
                    'metadata': {},
                    'error': 'No relevant documents found'
                }
            
            # Enhanced document processing and ranking
            processed_documents = []
            for i, (doc, score) in enumerate(search_results):
                processed_doc = {
                    'id': i,
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score),
                    'filename': doc.metadata.get('filename', 'Unknown'),
                    'chunk_id': doc.metadata.get('chunk_id', 0),
                    'relevance_score': self._calculate_relevance_score(doc.page_content, query, analysis),
                    'content_quality': self._assess_content_quality(doc.page_content),
                    'word_count': len(doc.page_content.split())
                }
                processed_documents.append(processed_doc)
            
            # Sort by combined relevance score
            processed_documents.sort(
                key=lambda x: (x['relevance_score'] * 0.6 + x['similarity_score'] * 0.4), 
                reverse=True
            )
            
            return {
                'success': True,
                'documents': processed_documents,
                'metadata': {
                    'total_documents': len(processed_documents),
                    'search_parameters': {
                        'k': k,
                        'score_threshold': score_threshold,
                        'complexity': complexity,
                        'search_scope': search_scope
                    },
                    'average_similarity': sum(doc['similarity_score'] for doc in processed_documents) / len(processed_documents),
                    'average_relevance': sum(doc['relevance_score'] for doc in processed_documents) / len(processed_documents)
                },
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Enhanced document search error: {str(e)}")
            return {
                'success': False,
                'documents': [],
                'metadata': {},
                'error': str(e)
            }
    
    def _calculate_relevance_score(self, content: str, query: str, analysis: Dict[str, Any]) -> float:
        """Calculate relevance score based on content and query analysis"""
        score = 0.0
        
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        key_concepts = analysis.get('key_concepts', [])
        
        # Word overlap score
        overlap = len(query_words.intersection(content_words))
        score += (overlap / len(query_words)) * 0.4
        
        # Key concept presence
        for concept in key_concepts:
            concept_words = set(concept.lower().split())
            concept_overlap = len(concept_words.intersection(content_words))
            if concept_overlap > 0:
                score += (concept_overlap / len(concept_words)) * 0.3
        
        # Content length bonus (moderate length preferred)
        content_length = len(content.split())
        if 100 <= content_length <= 500:
            score += 0.2
        elif 50 <= content_length <= 100 or 500 <= content_length <= 1000:
            score += 0.1
        
        # Information type bonus
        info_type = analysis.get('information_type', 'factual')
        if info_type == 'factual' and any(word in content.lower() for word in ['is', 'are', 'means', 'defined']):
            score += 0.1
        elif info_type == 'analytical' and any(word in content.lower() for word in ['because', 'due to', 'analysis', 'shows']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_content_quality(self, content: str) -> float:
        """Assess the quality of content"""
        quality_score = 0.5  # Base score
        
        # Length factor
        word_count = len(content.split())
        if 50 <= word_count <= 1000:
            quality_score += 0.2
        
        # Structure indicators
        if any(indicator in content for indicator in ['.', '!', '?']):
            quality_score += 0.1
        
        # Information density
        if len(set(content.lower().split())) / len(content.split()) > 0.7:
            quality_score += 0.1
        
        # Avoid very short or very long content
        if word_count < 10 or word_count > 2000:
            quality_score -= 0.2
        
        return max(0.0, min(quality_score, 1.0))
    
    def _enhanced_context_synthesis(self, documents: List[Dict[str, Any]], query: str, 
                                   analysis: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced context synthesis with improved analysis"""
        try:
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert information synthesizer. Given documents and query analysis, 
create a comprehensive context synthesis that:

1. Identifies and extracts key information relevant to the query
2. Organizes information by themes and importance
3. Identifies relationships and connections between documents
4. Notes any conflicting or contradictory information
5. Assesses information completeness and gaps
6. Provides confidence assessment for different pieces of information

Focus on creating a structured, coherent synthesis that directly supports answering the user's query.

Respond in JSON format with:
- key_themes: list of main themes found
- important_facts: list of key facts with source attribution
- relationships: connections between different pieces of information
- conflicts: any contradictory information found
- information_gaps: what information might be missing
- synthesis_confidence: overall confidence in the synthesis
- structured_content: organized content ready for response generation
"""),
                ("human", """
Query: {query}

Query Analysis: {analysis}

Documents: {documents}

Context: {context}

Please provide a comprehensive synthesis of the information.
""")
            ])
            
            # Prepare documents for synthesis
            docs_summary = ""
            for i, doc in enumerate(documents[:10]):  # Top 10 documents
                docs_summary += f"\n--- Document {i+1} ---\n"
                docs_summary += f"Source: {doc['filename']}\n"
                docs_summary += f"Relevance: {doc['relevance_score']:.3f}\n"
                docs_summary += f"Content: {doc['content'][:800]}...\n"
            
            response = self.llm.invoke(
                synthesis_prompt.format_messages(
                    query=query,
                    analysis=json.dumps(analysis, indent=2),
                    documents=docs_summary,
                    context=json.dumps(context or {}, indent=2)
                )
            )
            
            try:
                synthesis = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback synthesis
                synthesis = {
                    "key_themes": ["General information"],
                    "important_facts": [{"fact": "Information found in documents", "sources": ["Multiple sources"]}],
                    "relationships": ["Documents provide relevant information"],
                    "conflicts": [],
                    "information_gaps": ["Detailed analysis not available"],
                    "synthesis_confidence": 0.6,
                    "structured_content": response.content
                }
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Context synthesis error: {str(e)}")
            return {
                "key_themes": [],
                "important_facts": [],
                "relationships": [],
                "conflicts": [],
                "information_gaps": ["Synthesis failed"],
                "synthesis_confidence": 0.0,
                "structured_content": "Unable to synthesize context",
                "error": str(e)
            }
    
    def _generate_enhanced_response(self, query: str, synthesis: Dict[str, Any], 
                                   documents: List[Dict[str, Any]], analysis: Dict[str, Any],
                                   context: Dict[str, Any] = None, 
                                   chat_history: List[BaseMessage] = None) -> Dict[str, Any]:
        """Generate enhanced response with improved formatting and citations"""
        try:
            response_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert AI assistant providing comprehensive, accurate responses based on document analysis. 

Guidelines for your response:
1. Answer the user's question directly and thoroughly
2. Use information from the provided synthesis and documents
3. Provide clear structure with appropriate formatting
4. Include specific citations and source references
5. Acknowledge any limitations or uncertainties
6. Use a professional, helpful tone
7. If information is incomplete, state what additional information would be helpful

Structure your response clearly with:
- Direct answer to the main question
- Supporting details and evidence
- Source citations
- Any relevant caveats or limitations
"""),
                ("human", """
User Query: {query}

Context Synthesis: {synthesis}

Query Analysis: {analysis}

Additional Context: {context}

Chat History: {chat_history}

Please provide a comprehensive response to the user's query.
""")
            ])
            
            # Prepare chat history
            history_summary = ""
            if chat_history:
                for i, msg in enumerate(chat_history[-3:]):  # Last 3 messages
                    role = "Human" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                    history_summary += f"{role}: {str(msg.content)[:200]}...\n"
            
            response = self.llm.invoke(
                response_prompt.format_messages(
                    query=query,
                    synthesis=json.dumps(synthesis, indent=2),
                    analysis=json.dumps(analysis, indent=2),
                    context=json.dumps(context or {}, indent=2),
                    chat_history=history_summary
                )
            )
            
            # Prepare sources
            sources = []
            for i, doc in enumerate(documents[:8]):  # Top 8 sources
                sources.append({
                    'id': i + 1,
                    'filename': doc['filename'],
                    'content_preview': doc['content'][:300] + '...' if len(doc['content']) > 300 else doc['content'],
                    'relevance_score': doc['relevance_score'],
                    'similarity_score': doc['similarity_score'],
                    'word_count': doc['word_count'],
                    'metadata': doc['metadata']
                })
            
            # Calculate response confidence
            confidence = self._calculate_response_confidence(synthesis, documents, analysis)
            
            return {
                'response': response.content,
                'sources': sources,
                'confidence': confidence,
                'synthesis_quality': synthesis.get('synthesis_confidence', 0.5)
            }
            
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return {
                'response': f"I encountered an error while generating the response: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'synthesis_quality': 0.0
            }
    
    def _calculate_response_confidence(self, synthesis: Dict[str, Any], 
                                     documents: List[Dict[str, Any]], 
                                     analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the response"""
        confidence_factors = []
        
        # Synthesis confidence
        synthesis_conf = synthesis.get('synthesis_confidence', 0.5)
        confidence_factors.append(synthesis_conf * 0.3)
        
        # Document quality and relevance
        if documents:
            avg_relevance = sum(doc['relevance_score'] for doc in documents) / len(documents)
            confidence_factors.append(avg_relevance * 0.3)
            
            # Document count factor
            doc_count_factor = min(len(documents) / 5, 1.0)
            confidence_factors.append(doc_count_factor * 0.2)
        else:
            confidence_factors.extend([0.0, 0.0])
        
        # Analysis confidence
        analysis_conf = analysis.get('confidence', 0.5)
        confidence_factors.append(analysis_conf * 0.2)
        
        return sum(confidence_factors)
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities.copy()
