
"""
Calculator Agent for mathematical operations and calculations
"""

import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from tools.calculator_tool import CalculatorTool
from config import Config
import logging

logger = logging.getLogger(__name__)

class CalculatorAgent:
    """Agent specialized in mathematical calculations and problem solving"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=Config.OPENAI_MODEL,
            temperature=0.1
        )
        self.calculator_tool = CalculatorTool()
        self.agent_name = "Calculator Agent"
        self.capabilities = [
            "Mathematical calculations",
            "Unit conversions",
            "Advanced mathematical functions",
            "Formula evaluation",
            "Statistical calculations"
        ]
    
    def analyze_request(self, request: str) -> Dict[str, Any]:
        """
        Analyze if the request requires mathematical calculations
        
        Args:
            request: User request to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert mathematical analysis agent. Analyze the user's request to determine:

1. Whether it requires mathematical calculations
2. Type of calculation needed (arithmetic, algebra, trigonometry, statistics, unit conversion, etc.)
3. Extract mathematical expressions or problems
4. Identify what calculations are needed
5. Determine complexity level (simple, moderate, complex)

Respond in JSON format with these fields:
- requires_calculation: boolean
- calculation_type: string
- expressions: list of mathematical expressions found
- problems: list of word problems that need solving
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
                math_keywords = ['calculate', 'compute', 'solve', 'convert', 'math', 'equation', 
                               'formula', 'sum', 'product', 'average', 'percentage', '+', '-', 
                               '*', '/', '=', 'degrees', 'feet', 'meters', 'kg', 'pounds']
                
                has_math = any(keyword in request.lower() for keyword in math_keywords)
                
                analysis = {
                    "requires_calculation": has_math,
                    "calculation_type": "general" if has_math else "none",
                    "expressions": [],
                    "problems": [request] if has_math else [],
                    "complexity": "moderate" if has_math else "none",
                    "confidence": 0.7 if has_math else 0.3,
                    "reasoning": "Fallback analysis based on keyword detection"
                }
            
            logger.info(f"Calculator analysis: {analysis.get('requires_calculation', False)}")
            return analysis
            
        except Exception as e:
            logger.error(f"Calculator analysis error: {str(e)}")
            return {
                "requires_calculation": False,
                "calculation_type": "error",
                "expressions": [],
                "problems": [],
                "complexity": "error",
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}"
            }
    
    def solve_problem(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve mathematical problems or perform calculations
        
        Args:
            problem: Mathematical problem or expression to solve
            context: Additional context for the problem
            
        Returns:
            Dictionary containing solution and explanation
        """
        try:
            logger.info(f"Solving mathematical problem: {problem[:50]}...")
            
            # First, try to extract mathematical expressions
            expressions = self._extract_expressions(problem)
            
            calculation_results = []
            
            # Process each expression
            for expr in expressions:
                calc_result = self.calculator_tool.calculate(expr)
                calculation_results.append({
                    'expression': expr,
                    'result': calc_result
                })
            
            # If no expressions found, try to solve as word problem
            if not expressions:
                word_problem_result = self._solve_word_problem(problem, context)
                if word_problem_result:
                    calculation_results.append(word_problem_result)
            
            # Generate comprehensive explanation
            explanation = self._generate_explanation(problem, calculation_results, context)
            
            return {
                'success': True,
                'problem': problem,
                'calculations': calculation_results,
                'explanation': explanation,
                'agent': self.agent_name,
                'confidence': self._calculate_confidence(calculation_results),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Problem solving error: {str(e)}")
            return {
                'success': False,
                'problem': problem,
                'calculations': [],
                'explanation': f"Unable to solve problem: {str(e)}",
                'agent': self.agent_name,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _extract_expressions(self, text: str) -> List[str]:
        """Extract mathematical expressions from text"""
        import re
        
        # Patterns for mathematical expressions
        patterns = [
            r'[\d\+\-\*/\^\(\)\.\s]+(?:=|$)',  # Basic arithmetic
            r'\d+\s*(?:feet|ft|meters?|m|inches?|in|cm|mm|km)\s+to\s+\w+',  # Unit conversion
            r'convert\s+[\d\.\s\w]+',  # Conversion requests
            r'sqrt\([^)]+\)',  # Square root
            r'(?:sin|cos|tan|log|ln)\([^)]+\)',  # Trigonometric and log functions
        ]
        
        expressions = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            expressions.extend(matches)
        
        # Clean up expressions
        cleaned_expressions = []
        for expr in expressions:
            expr = expr.strip().rstrip('=')
            if expr and len(expr) > 1:
                cleaned_expressions.append(expr)
        
        return cleaned_expressions
    
    def _solve_word_problem(self, problem: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Solve word problems using LLM"""
        try:
            word_problem_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert mathematical problem solver. Given a word problem:

1. Identify the mathematical operations needed
2. Extract relevant numbers and units
3. Set up the mathematical expressions
4. Solve step by step
5. Provide the final answer with appropriate units

If the problem cannot be solved mathematically, indicate that clearly.

Respond in JSON format with:
- can_solve: boolean
- mathematical_expression: string (if solvable)
- step_by_step: list of solution steps
- final_answer: string with result and units
- explanation: string explaining the solution approach
"""),
                ("human", """
Word Problem: {problem}

Additional Context: {context}

Please solve this step by step.
""")
            ])
            
            response = self.llm.invoke(
                word_problem_prompt.format_messages(
                    problem=problem,
                    context=json.dumps(context or {}, indent=2)
                )
            )
            
            try:
                solution = json.loads(response.content)
                
                if solution.get('can_solve', False) and solution.get('mathematical_expression'):
                    # Try to calculate the expression
                    expr = solution['mathematical_expression']
                    calc_result = self.calculator_tool.calculate(expr)
                    
                    return {
                        'expression': expr,
                        'result': calc_result,
                        'word_problem_solution': solution
                    }
                    
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Word problem solving error: {str(e)}")
            return None
    
    def _generate_explanation(self, problem: str, calculation_results: List[Dict[str, Any]], 
                            context: Dict[str, Any] = None) -> str:
        """Generate explanation for the solution"""
        try:
            explanation_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert mathematics tutor. Given a problem and calculation results, 
provide a clear, comprehensive explanation that:

1. Explains what the problem is asking
2. Describes the approach taken
3. Walks through the calculations step by step
4. Explains the final result
5. Provides context for the answer

Be clear, educational, and easy to understand.
"""),
                ("human", """
Problem: {problem}

Calculation Results: {results}

Context: {context}

Please provide a comprehensive explanation of the solution.
""")
            ])
            
            response = self.llm.invoke(
                explanation_prompt.format_messages(
                    problem=problem,
                    results=json.dumps(calculation_results, indent=2),
                    context=json.dumps(context or {}, indent=2)
                )
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Explanation generation error: {str(e)}")
            return "Unable to generate detailed explanation."
    
    def _calculate_confidence(self, calculation_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the solution"""
        if not calculation_results:
            return 0.0
        
        total_confidence = 0.0
        successful_calculations = 0
        
        for result in calculation_results:
            calc_result = result.get('result', {})
            if calc_result.get('success', False):
                successful_calculations += 1
                # Base confidence on result type and complexity
                if calc_result.get('type') == 'unit_conversion':
                    total_confidence += 0.9
                elif calc_result.get('type') == 'arithmetic':
                    total_confidence += 0.95
                elif calc_result.get('type') == 'advanced_math':
                    total_confidence += 0.85
                else:
                    total_confidence += 0.8
            
        if successful_calculations == 0:
            return 0.0
        
        return total_confidence / successful_calculations
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities.copy()
    
    def get_supported_functions(self) -> List[str]:
        """Get list of supported mathematical functions"""
        return self.calculator_tool.get_supported_functions()
