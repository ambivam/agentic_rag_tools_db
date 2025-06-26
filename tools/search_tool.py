
"""
Internet search tool for web search functionality
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class InternetSearchTool:
    """Internet search tool with multiple search providers and result processing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Search providers configuration
        self.providers = {
            'duckduckgo': {
                'name': 'DuckDuckGo',
                'url': 'https://api.duckduckgo.com/',
                'params': {'format': 'json', 'no_html': '1', 'skip_disambig': '1'}
            },
            'serpapi': {
                'name': 'SerpAPI',
                'url': 'https://serpapi.com/search',
                'api_key_required': True
            },
            'fallback': {
                'name': 'Fallback Scraper',
                'url': 'https://www.google.com/search',
                'params': {'num': 10}
            }
        }
    
    def search(self, query: str, num_results: int = 5, provider: str = 'auto') -> Dict[str, Any]:
        """
        Search the internet for information
        
        Args:
            query: Search query
            num_results: Number of results to return
            provider: Search provider ('auto', 'duckduckgo', 'serpapi', 'fallback')
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            logger.info(f"Searching for: {query}")
            
            # Determine provider
            if provider == 'auto':
                provider = self._select_best_provider()
            
            # Perform search
            if provider == 'duckduckgo':
                results = self._search_duckduckgo(query, num_results)
            elif provider == 'serpapi':
                results = self._search_serpapi(query, num_results)
            else:
                results = self._search_fallback(query, num_results)
            
            # Process and rank results
            processed_results = self._process_results(results, query)
            
            return {
                'success': True,
                'query': query,
                'provider': provider,
                'results': processed_results[:num_results],
                'total_results': len(processed_results),
                'search_time': time.time(),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {
                'success': False,
                'query': query,
                'provider': provider,
                'results': [],
                'total_results': 0,
                'search_time': time.time(),
                'error': str(e)
            }
    
    def _select_best_provider(self) -> str:
        """Select the best available search provider"""
        # Check if SerpAPI key is available
        if self.config.get('serpapi_key'):
            return 'serpapi'
        
        # Default to DuckDuckGo
        return 'duckduckgo'
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(
                self.providers['duckduckgo']['url'],
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract instant answer
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Instant Answer'),
                    'snippet': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': data.get('AbstractSource', 'DuckDuckGo'),
                    'type': 'instant_answer'
                })
            
            # Extract related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('Text', '').split(' - ')[0],
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo',
                        'type': 'related_topic'
                    })
            
            # If no results, try web search fallback
            if not results:
                results = self._search_duckduckgo_web(query, num_results)
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def _search_duckduckgo_web(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search DuckDuckGo web results using the lite interface"""
        try:
            # Use the lite interface which is more reliable
            url = "https://lite.duckduckgo.com/lite/"
            params = {
                'q': query,
                'kl': 'us-en',  # Language/region
                'k1': '-1'      # Safe search off
            }
            
            # Add required headers
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            self.session.headers.update(headers)
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Parse the lite interface results
            for tr in soup.find_all('tr', class_=['result-sponsored', 'result-link'])[:num_results]:
                # Get title and URL
                link = tr.find('a')
                if not link:
                    continue
                    
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                # Get snippet from next row
                snippet_tr = tr.find_next_sibling('tr')
                snippet = snippet_tr.get_text(strip=True) if snippet_tr else ''
                
                if title and url:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url,
                        'source': 'DuckDuckGo',
                        'type': 'web_result'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo web search error: {str(e)}")
            return []
    
    def _search_serpapi(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using SerpAPI (if API key available)"""
        try:
            api_key = self.config.get('serpapi_key')
            if not api_key:
                raise ValueError("SerpAPI key not configured")
            
            params = {
                'q': query,
                'api_key': api_key,
                'engine': 'google',
                'num': num_results
            }
            
            response = self.session.get(
                self.providers['serpapi']['url'],
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract organic results
            for result in data.get('organic_results', []):
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'url': result.get('link', ''),
                    'source': result.get('displayed_link', ''),
                    'type': 'organic_result'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"SerpAPI search error: {str(e)}")
            return []
    
    def _search_fallback(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Fallback search method"""
        try:
            # Simple web scraping fallback (use with caution)
            logger.warning("Using fallback search method")
            
            # Create a simple search result
            return [{
                'title': f'Search results for: {query}',
                'snippet': f'This is a fallback search result for the query: {query}. '
                          'Please configure a proper search API for better results.',
                'url': f'https://www.google.com/search?q={quote(query)}',
                'source': 'Fallback',
                'type': 'fallback_result'
            }]
            
        except Exception as e:
            logger.error(f"Fallback search error: {str(e)}")
            return []
    
    def _process_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Process and enhance search results"""
        processed_results = []
        
        for result in results:
            # Clean and enhance result
            processed_result = {
                'title': self._clean_text(result.get('title', '')),
                'snippet': self._clean_text(result.get('snippet', '')),
                'url': result.get('url', ''),
                'source': result.get('source', 'Unknown'),
                'type': result.get('type', 'web_result'),
                'relevance_score': self._calculate_relevance(result, query),
                'timestamp': time.time()
            }
            
            # Add metadata
            processed_result['metadata'] = {
                'domain': self._extract_domain(processed_result['url']),
                'word_count': len(processed_result['snippet'].split()),
                'has_url': bool(processed_result['url']),
                'confidence': self._calculate_confidence(processed_result)
            }
            
            processed_results.append(processed_result)
        
        # Sort by relevance score
        processed_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return processed_results
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        
        return text.strip()
    
    def _calculate_relevance(self, result: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for a search result"""
        score = 0.0
        query_words = set(query.lower().split())
        
        # Title relevance
        title_words = set(result.get('title', '').lower().split())
        title_overlap = len(query_words.intersection(title_words))
        score += title_overlap * 0.4
        
        # Snippet relevance
        snippet_words = set(result.get('snippet', '').lower().split())
        snippet_overlap = len(query_words.intersection(snippet_words))
        score += snippet_overlap * 0.3
        
        # Result type bonus
        if result.get('type') == 'instant_answer':
            score += 0.5
        elif result.get('type') == 'organic_result':
            score += 0.3
        
        # URL quality
        if result.get('url') and 'wikipedia' in result.get('url', '').lower():
            score += 0.2
        
        return score
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score for a result"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for results with URLs
        if result.get('url'):
            confidence += 0.2
        
        # Higher confidence for longer snippets
        snippet_length = len(result.get('snippet', ''))
        if snippet_length > 100:
            confidence += 0.2
        
        # Higher confidence for certain result types
        if result.get('type') == 'instant_answer':
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def summarize_results(self, search_results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Summarize search results"""
        if not search_results:
            return {
                'summary': f'No results found for query: {query}',
                'key_points': [],
                'sources': [],
                'confidence': 0.0
            }
        
        # Extract key information
        key_points = []
        sources = []
        
        for result in search_results[:5]:  # Top 5 results
            if result.get('snippet'):
                key_points.append({
                    'text': result['snippet'][:200] + '...' if len(result['snippet']) > 200 else result['snippet'],
                    'source': result.get('source', 'Unknown'),
                    'confidence': result.get('metadata', {}).get('confidence', 0.5)
                })
            
            if result.get('url'):
                sources.append({
                    'title': result.get('title', 'Unknown'),
                    'url': result['url'],
                    'domain': result.get('metadata', {}).get('domain', 'Unknown')
                })
        
        # Calculate overall confidence
        overall_confidence = sum(
            result.get('metadata', {}).get('confidence', 0.5) 
            for result in search_results
        ) / len(search_results)
        
        # Create summary
        summary = f"Found {len(search_results)} results for '{query}'. "
        if key_points:
            summary += f"Key information includes: {'; '.join([point['text'][:100] + '...' for point in key_points[:3]])}"
        
        return {
            'summary': summary,
            'key_points': key_points,
            'sources': sources,
            'confidence': overall_confidence,
            'total_results': len(search_results)
        }
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported search features"""
        return [
            'Web search with multiple providers',
            'DuckDuckGo instant answers',
            'SerpAPI integration (with API key)',
            'Result ranking and relevance scoring',
            'Result summarization and key point extraction',
            'Source attribution and metadata',
            'Confidence scoring for results',
            'Domain extraction and URL validation'
        ]
