"""
Gemini LLM implementation with function calling support.
SIMPLIFIED VERSION - no complex type conversions.
"""

import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from llm.base import BaseLLM
from database import queries


class GeminiLLM(BaseLLM):
    """Gemini implementation of the LLM interface."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google AI API key
            model_name: Gemini model to use (default: gemini-2.5-flash-lite)
        """
        super().__init__(api_key, model_name)
        genai.configure(api_key=api_key)
        
        # Map tool names to actual functions
        self.tool_map = {
            'get_top_selling_products': queries.get_top_selling_products,
            'get_trending_products': queries.get_trending_products,
            'search_products_by_description': queries.search_products_by_description,
            'get_low_stock_products': queries.get_low_stock_products,
            'get_sales_summary_by_category': queries.get_sales_summary_by_category,
            'get_product_details': queries.get_product_details,
            'get_recent_transactions': queries.get_recent_transactions,
        }
    
    def chat(
        self, 
        messages: List[Dict[str, Any]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat message to Gemini and get response.
        Uses a simple approach - just send the latest user message as a prompt.
        """
        try:
            # Build a simple prompt from all messages
            prompt_parts = []
            for msg in messages:
                role = msg['role']
                content = msg['content']
                
                if role == 'system':
                    prompt_parts.append(f"System: {content}\n")
                elif role == 'user':
                    prompt_parts.append(f"User: {content}\n")
                elif role == 'assistant':
                    prompt_parts.append(f"Assistant: {content}\n")
            
            full_prompt = "\n".join(prompt_parts)
            
            # Convert tools to Gemini format if provided
            gemini_tools = None
            if tools:
                gemini_tools = self._convert_tools_to_gemini_format(tools)
            
            # Create model with or without tools
            if gemini_tools:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    tools=gemini_tools
                )
            else:
                model = genai.GenerativeModel(model_name=self.model_name)
            
            # Generate response
            response = model.generate_content(full_prompt)
            
            # Parse response
            result = {
                'content': '',
                'tool_calls': []
            }
            
            # Extract text and function calls
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    # Check for function call
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        result['tool_calls'].append({
                            'name': fc.name,
                            'arguments': dict(fc.args)
                        })
                    # Check for text
                    if hasattr(part, 'text') and part.text:
                        result['content'] += part.text
            
            # If we have tool calls but no text, add placeholder
            if result['tool_calls'] and not result['content']:
                result['content'] = '[Calling tools...]'
            
            return result
            
        except Exception as e:
            import traceback
            print(f"Error in Gemini chat: {e}")
            print(traceback.format_exc())
            return {
                'content': f"Error: {str(e)}",
                'tool_calls': []
            }
    
    def execute_tool_call(
        self, 
        tool_name: str, 
        tool_args: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool/function call.
        """
        if tool_name not in self.tool_map:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            func = self.tool_map[tool_name]
            result = func(**tool_args)
            return result
        except Exception as e:
            import traceback
            print(f"Error executing tool {tool_name}: {e}")
            print(traceback.format_exc())
            return {"error": str(e)}
    
    def format_tool_response(
        self, 
        tool_name: str, 
        tool_result: Any
    ) -> str:
        """
        Format tool result as a string.
        """
        if isinstance(tool_result, dict) and 'error' in tool_result:
            return f"Error executing {tool_name}: {tool_result['error']}"
        
        # Format as JSON for structured data
        if isinstance(tool_result, (list, dict)):
            return json.dumps(tool_result, indent=2)
        
        return str(tool_result)
    
    def _convert_tools_to_gemini_format(self, tools: List[Dict[str, Any]]) -> List[Any]:
        """
        Convert tool definitions to Gemini's function declaration format.
        """
        # Import only what we need
        from google.generativeai.types import FunctionDeclaration, Tool
        
        function_declarations = []
        for tool in tools:
            func_decl = FunctionDeclaration(
                name=tool['name'],
                description=tool['description'],
                parameters=tool['parameters']
            )
            function_declarations.append(func_decl)
        
        # Return as a list with single Tool object
        return [Tool(function_declarations=function_declarations)]