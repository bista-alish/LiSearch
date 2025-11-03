"""
Abstract base class for LLM providers.
Enables easy switching between Gemini, OpenAI, or other providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLM(ABC):
    """Abstract base class for LLM interactions."""
    
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for the LLM provider
            model_name: Name/ID of the model to use
        """
        self.api_key = api_key
        self.model_name = model_name
    
    @abstractmethod
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat message and get a response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool/function definitions
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict containing response text and any tool calls
        """
        pass
    
    @abstractmethod
    def execute_tool_call(
        self, 
        tool_name: str, 
        tool_args: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool/function call.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool
            
        Returns:
            Result from the tool execution
        """
        pass
    
    @abstractmethod
    def format_tool_response(
        self, 
        tool_name: str, 
        tool_result: Any
    ) -> str:
        """
        Format a tool execution result for the LLM.
        
        Args:
            tool_name: Name of the tool that was executed
            tool_result: Result from the tool execution
            
        Returns:
            Formatted string for the LLM to process
        """
        pass
    
    def chat_with_tools(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        High-level method to handle chat with automatic tool calling.
        
        This method handles the complete flow:
        1. Send user message with available tools
        2. If LLM requests tool calls, execute them
        3. Send tool results back to LLM
        4. Repeat until LLM provides final response or max iterations reached
        
        Args:
            user_message: The user's input message
            conversation_history: Optional previous conversation messages
            tools: Optional list of available tools
            max_iterations: Maximum number of tool call iterations
            
        Returns:
            Dict with 'response' (final text) and 'tool_calls_made' (list of tools used)
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})
        
        tool_calls_made = []
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            
            # Get response from LLM
            response = self.chat(messages, tools=tools)
            
            # Check if LLM wants to call any tools
            if not response.get('tool_calls'):
                # No tool calls, we have final response
                return {
                    'response': response.get('content', ''),
                    'tool_calls_made': tool_calls_made,
                    'iterations': iterations
                }
            
            # Execute tool calls
            for tool_call in response['tool_calls']:
                tool_name = tool_call['name']
                tool_args = tool_call['arguments']
                
                # Execute the tool
                tool_result = self.execute_tool_call(tool_name, tool_args)
                
                # Track tool usage
                tool_calls_made.append({
                    'name': tool_name,
                    'arguments': tool_args,
                    'result': tool_result
                })
                
                # Format result for LLM
                formatted_result = self.format_tool_response(tool_name, tool_result)
                
                # Add tool result to conversation
                messages.append({
                    "role": "assistant",
                    "content": f"[Tool call: {tool_name}]"
                })
                messages.append({
                    "role": "user",
                    "content": formatted_result
                })
        
        # Max iterations reached
        return {
            'response': "I apologize, but I'm having trouble processing your request. Please try rephrasing.",
            'tool_calls_made': tool_calls_made,
            'iterations': iterations,
            'error': 'max_iterations_reached'
        }