"""
Tool definitions for LLM function calling.
Maps natural language queries to database functions.
"""

from typing import List, Dict, Any


# Gemini-compatible tool definitions
GEMINI_TOOLS = [
    {
        'name': 'get_top_selling_products',
        'description': 'Get the best-selling products by total quantity sold. Use this when users ask about top sellers, best sellers, or most popular products.',
        'parameters': {
            'type': 'object',
            'properties': {
                'category': {
                    'type': 'string',
                    'description': 'Optional category to filter by (Wine, Beer, Spirits, Liqueurs, Ready-to-Drink). Leave null for all categories.',
                    'nullable': True
                },
                'limit': {
                    'type': 'integer',
                    'description': 'Number of products to return (default: 10)'
                },
                'days': {
                    'type': 'integer',
                    'description': 'Number of days to look back for sales data (default: 30)'
                }
            }
        }
    },
    {
        'name': 'get_trending_products',
        'description': 'Get products that are trending based on recent sales velocity. Use this when users ask about trending, hot, or what\'s popular right now.',
        'parameters': {
            'type': 'object',
            'properties': {
                'days': {
                    'type': 'integer',
                    'description': 'Number of days for the recent period (default: 7)'
                },
                'limit': {
                    'type': 'integer',
                    'description': 'Number of products to return (default: 10)'
                }
            }
        }
    },
    {
        'name': 'search_products_by_description',
        'description': 'Search for products by name, description, or brand. Use this when users describe characteristics like "woody", "citrus", "smooth", or search for specific product names.',
        'parameters': {
            'type': 'object',
            'properties': {
                'search_term': {
                    'type': 'string',
                    'description': 'The search term to match against product names, descriptions, and brands'
                }
            },
            'required': ['search_term']
        }
    },
    {
        'name': 'get_low_stock_products',
        'description': 'Get products that need reordering (at or below reorder level). Use this when users ask about low stock, inventory alerts, or what needs to be restocked.',
        'parameters': {
            'type': 'object',
            'properties': {
                'limit': {
                    'type': 'integer',
                    'description': 'Maximum number of products to return (default: 20)'
                }
            }
        }
    },
    {
        'name': 'get_sales_summary_by_category',
        'description': 'Get sales performance summary broken down by product category. Use this when users ask about category performance, which category sells best, or want category-level analytics.',
        'parameters': {
            'type': 'object',
            'properties': {
                'days': {
                    'type': 'integer',
                    'description': 'Number of days to look back (default: 30)'
                }
            }
        }
    },
    {
        'name': 'get_product_details',
        'description': 'Get detailed information about a specific product including sales history. Use this when users ask about a specific product by name or want detailed info.',
        'parameters': {
            'type': 'object',
            'properties': {
                'product_id': {
                    'type': 'integer',
                    'description': 'Product ID (if known)',
                    'nullable': True
                },
                'product_name': {
                    'type': 'string',
                    'description': 'Product name to search for',
                    'nullable': True
                }
            }
        }
    },
    {
        'name': 'get_recent_transactions',
        'description': 'Get recent sales transactions with details. Use this when users ask about recent sales, latest orders, or transaction history.',
        'parameters': {
            'type': 'object',
            'properties': {
                'limit': {
                    'type': 'integer',
                    'description': 'Number of transactions to return (default: 10)'
                }
            }
        }
    }
]


# OpenAI-compatible tool definitions (for future use)
OPENAI_TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': tool['name'],
            'description': tool['description'],
            'parameters': tool['parameters']
        }
    }
    for tool in GEMINI_TOOLS
]


def get_tools_for_provider(provider: str = 'gemini') -> List[Dict[str, Any]]:
    """
    Get tool definitions for a specific LLM provider.
    
    Args:
        provider: The LLM provider ('gemini' or 'openai')
        
    Returns:
        List of tool definitions in the appropriate format
    """
    if provider.lower() == 'gemini':
        return GEMINI_TOOLS
    elif provider.lower() == 'openai':
        return OPENAI_TOOLS
    else:
        raise ValueError(f"Unknown provider: {provider}")


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a liquor store's point-of-sale and inventory management system. 

You help store staff and managers by answering questions about:
- Product sales and performance
- Inventory levels and reordering needs
- Product information and recommendations
- Sales trends and analytics

When users ask questions, use the available tools to query the database and provide accurate, data-driven answers. 

Always be:
- Concise and professional
- Data-driven (use actual numbers from queries)
- Helpful in suggesting follow-up actions
- Clear about what time period your data covers

If you need to search for a product, use the search_products_by_description tool with relevant keywords from the user's question."""