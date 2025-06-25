
"""
Calculator tool for mathematical operations and calculations
"""

import math
import re
import ast
import operator
from typing import Dict, Any, Union, List
from decimal import Decimal, getcontext
import logging

logger = logging.getLogger(__name__)

class CalculatorTool:
    """Advanced calculator tool with support for various mathematical operations"""
    
    def __init__(self):
        # Set precision for decimal calculations
        getcontext().prec = 28
        
        # Safe operators for eval
        self.safe_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg,
        }
        
        # Mathematical constants
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'inf': math.inf,
            'nan': math.nan
        }
        
        # Unit conversion factors (to base units)
        self.unit_conversions = {
            # Length (to meters)
            'length': {
                'mm': 0.001, 'cm': 0.01, 'm': 1, 'km': 1000,
                'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mi': 1609.344
            },
            # Weight (to grams)
            'weight': {
                'mg': 0.001, 'g': 1, 'kg': 1000, 't': 1000000,
                'oz': 28.3495, 'lb': 453.592, 'st': 6350.29
            },
            # Temperature (to Celsius)
            'temperature': {
                'c': lambda x: x,
                'f': lambda x: (x - 32) * 5/9,
                'k': lambda x: x - 273.15
            },
            # Volume (to liters)
            'volume': {
                'ml': 0.001, 'l': 1, 'gal': 3.78541, 'qt': 0.946353,
                'pt': 0.473176, 'cup': 0.236588, 'fl_oz': 0.0295735
            }
        }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Calculate mathematical expressions with enhanced capabilities
        
        Args:
            expression: Mathematical expression or calculation request
            
        Returns:
            Dictionary containing result and metadata
        """
        try:
            logger.info(f"Calculating expression: {expression}")
            
            # Clean and normalize the expression
            expression = self._normalize_expression(expression)
            
            # Handle special function calls
            if any(func in expression.lower() for func in ['sqrt', 'sin', 'cos', 'tan', 'log', 'ln']):
                result = self._calculate_advanced_functions(expression)
            # Handle unit conversions
            elif 'convert' in expression.lower() or 'to' in expression.lower():
                result = self._handle_unit_conversion(expression)
            # Handle basic arithmetic
            else:
                result = self._calculate_basic_expression(expression)
            
            return {
                'success': True,
                'result': result,
                'expression': expression,
                'type': self._determine_calculation_type(expression),
                'formatted_result': self._format_result(result),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            return {
                'success': False,
                'result': None,
                'expression': expression,
                'type': 'error',
                'formatted_result': None,
                'error': str(e)
            }
    
    def _normalize_expression(self, expression: str) -> str:
        """Normalize mathematical expression"""
        # Remove extra whitespace
        expression = ' '.join(expression.split())
        
        # Replace common mathematical symbols
        replacements = {
            '×': '*',
            '÷': '/',
            '^': '**',
            '√': 'sqrt',
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        # Handle implicit multiplication (e.g., 2(3+4) -> 2*(3+4))
        expression = re.sub(r'(\d)\(', r'\1*(', expression)
        expression = re.sub(r'\)(\d)', r')*\1', expression)
        
        return expression
    
    def _calculate_basic_expression(self, expression: str) -> float:
        """Calculate basic arithmetic expressions safely"""
        try:
            # Parse the expression into an AST
            node = ast.parse(expression, mode='eval')
            return self._eval_node(node.body)
        except:
            # Fallback to eval with restricted globals
            safe_dict = {
                "__builtins__": {},
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                **self.constants
            }
            return eval(expression, safe_dict)
    
    def _eval_node(self, node):
        """Safely evaluate AST nodes"""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.safe_operators[type(node.op)](
                self._eval_node(node.left),
                self._eval_node(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return self.safe_operators[type(node.op)](self._eval_node(node.operand))
        elif isinstance(node, ast.Name):
            return self.constants.get(node.id, 0)
        else:
            raise TypeError(f"Unsupported operation: {type(node)}")
    
    def _calculate_advanced_functions(self, expression: str) -> float:
        """Calculate expressions with advanced mathematical functions"""
        # Create safe environment with math functions
        safe_dict = {
            "__builtins__": {},
            # Basic functions
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            # Math functions
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "log": math.log,
            "log10": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "pow": math.pow,
            "ceil": math.ceil,
            "floor": math.floor,
            "factorial": math.factorial,
            "degrees": math.degrees,
            "radians": math.radians,
            # Constants
            **self.constants
        }
        
        # Handle natural log notation
        expression = expression.replace('ln(', 'log(')
        
        return eval(expression, safe_dict)
    
    def _handle_unit_conversion(self, expression: str) -> Dict[str, Any]:
        """Handle unit conversion requests"""
        try:
            # Parse conversion request
            # Format: "convert X unit1 to unit2" or "X unit1 to unit2"
            pattern = r'(?:convert\s+)?(\d+(?:\.\d+)?)\s*(\w+)\s+to\s+(\w+)'
            match = re.search(pattern, expression.lower())
            
            if not match:
                raise ValueError("Invalid conversion format")
            
            value = float(match.group(1))
            from_unit = match.group(2)
            to_unit = match.group(3)
            
            # Determine unit category
            category = self._get_unit_category(from_unit, to_unit)
            
            if category == 'temperature':
                result = self._convert_temperature(value, from_unit, to_unit)
            else:
                result = self._convert_standard_units(value, from_unit, to_unit, category)
            
            return {
                'value': result,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'category': category,
                'original_value': value
            }
            
        except Exception as e:
            raise ValueError(f"Unit conversion failed: {str(e)}")
    
    def _get_unit_category(self, from_unit: str, to_unit: str) -> str:
        """Determine the category of units"""
        for category, units in self.unit_conversions.items():
            if category == 'temperature':
                continue
            if from_unit in units and to_unit in units:
                return category
        
        # Check temperature units
        temp_units = ['c', 'f', 'k', 'celsius', 'fahrenheit', 'kelvin']
        if from_unit.lower() in temp_units and to_unit.lower() in temp_units:
            return 'temperature'
        
        raise ValueError(f"Unknown unit category for {from_unit} to {to_unit}")
    
    def _convert_standard_units(self, value: float, from_unit: str, to_unit: str, category: str) -> float:
        """Convert between standard units"""
        conversions = self.unit_conversions[category]
        
        # Convert to base unit, then to target unit
        base_value = value * conversions[from_unit]
        result = base_value / conversions[to_unit]
        
        return result
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature units"""
        from_unit = from_unit.lower()[0]  # Get first letter
        to_unit = to_unit.lower()[0]
        
        # Convert to Celsius first
        if from_unit == 'c':
            celsius = value
        elif from_unit == 'f':
            celsius = (value - 32) * 5/9
        elif from_unit == 'k':
            celsius = value - 273.15
        else:
            raise ValueError(f"Unknown temperature unit: {from_unit}")
        
        # Convert from Celsius to target
        if to_unit == 'c':
            return celsius
        elif to_unit == 'f':
            return celsius * 9/5 + 32
        elif to_unit == 'k':
            return celsius + 273.15
        else:
            raise ValueError(f"Unknown temperature unit: {to_unit}")
    
    def _determine_calculation_type(self, expression: str) -> str:
        """Determine the type of calculation"""
        if 'convert' in expression.lower() or ' to ' in expression.lower():
            return 'unit_conversion'
        elif any(func in expression.lower() for func in ['sqrt', 'sin', 'cos', 'tan', 'log']):
            return 'advanced_math'
        elif any(op in expression for op in ['+', '-', '*', '/', '**', '^']):
            return 'arithmetic'
        else:
            return 'simple'
    
    def _format_result(self, result: Union[float, Dict[str, Any]]) -> str:
        """Format the result for display"""
        if isinstance(result, dict):
            # Unit conversion result
            return f"{result['original_value']} {result['from_unit']} = {result['value']:.6g} {result['to_unit']}"
        elif isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            else:
                return f"{result:.6g}"
        else:
            return str(result)
    
    def get_supported_functions(self) -> List[str]:
        """Get list of supported mathematical functions"""
        return [
            'Basic arithmetic: +, -, *, /, **, ^',
            'Advanced functions: sqrt, sin, cos, tan, asin, acos, atan',
            'Logarithms: log, log10, ln, exp',
            'Other: abs, round, min, max, ceil, floor, factorial',
            'Constants: pi, e, tau, inf, nan',
            'Unit conversions: length, weight, temperature, volume',
            'Conversion syntax: "convert 5 ft to m" or "5 ft to m"'
        ]
