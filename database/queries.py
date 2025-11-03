"""
Database query functions - Thin wrappers around Supabase RPC calls.
"""

from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_top_selling_products(
    category: Optional[str] = None,
    limit: int = 10,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get the top selling products by quantity sold.
    
    Args:
        category: Optional category name to filter by (e.g., 'Wine', 'Beer')
        limit: Maximum number of products to return
        days: Number of days to look back for sales data
        
    Returns:
        List of dicts with product info and total quantity sold
    """
    try:
        response = supabase.rpc('get_top_selling_products', {
            'p_category': category,
            'p_limit': int(limit),
            'p_days': int(days)
        }).execute()
        return response.data
    except Exception as e:
        print(f"Error calling get_top_selling_products: {e}")
        return []


def get_trending_products(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get trending products based on recent sales velocity.
    
    Args:
        days: Number of days for the recent period
        limit: Maximum number of products to return
        
    Returns:
        List of dicts with product info and trend metrics
    """
    try:
        response = supabase.rpc('get_trending_products', {
            'p_days': int(days),
            'p_limit': int(limit)
        }).execute()
        return response.data
    except Exception as e:
        print(f"Error calling get_trending_products: {e}")
        return []


def search_products_by_description(search_term: str) -> List[Dict[str, Any]]:
    """
    Search for products by name, description, or brand.
    
    Args:
        search_term: Search term to match against product fields
        
    Returns:
        List of matching products with relevance scores
    """
    try:
        response = supabase.rpc('search_products_by_description', {
            'p_search_term': search_term
        }).execute()
        return response.data
    except Exception as e:
        print(f"Error calling search_products_by_description: {e}")
        return []


def get_low_stock_products(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get products that need reordering (at or below reorder level).
    
    Args:
        limit: Maximum number of products to return
        
    Returns:
        List of dicts with product and inventory info
    """
    try:
        response = supabase.rpc('get_low_stock_products', {
            'p_limit': int(limit)
        }).execute()
        return response.data
    except Exception as e:
        print(f"Error calling get_low_stock_products: {e}")
        return []


def get_sales_summary_by_category(days: int = 30) -> List[Dict[str, Any]]:
    """
    Get sales performance summary broken down by category.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of dicts with category sales metrics
    """
    try:
        response = supabase.rpc('get_sales_summary_by_category', {
            'p_days': int(days)
        }).execute()
        return response.data
    except Exception as e:
        print(f"Error calling get_sales_summary_by_category: {e}")
        return []


def get_product_details(
    product_id: Optional[int] = None,
    product_name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific product.
    
    Args:
        product_id: Optional product ID to look up
        product_name: Optional product name to search for
        
    Returns:
        Dict with complete product details, or None if not found
    """
    try:
        response = supabase.rpc('get_product_details', {
            'p_product_id': product_id,
            'p_product_name': product_name
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error calling get_product_details: {e}")
        return None


def get_recent_transactions(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent sales transactions with summary info.
    
    Args:
        limit: Maximum number of transactions to return
        
    Returns:
        List of dicts with transaction details
    """
    try:
        response = supabase.rpc('get_recent_transactions', {
            'p_limit': int(limit)
        }).execute()
        return response.data
    except Exception as e:
        print(f"Error calling get_recent_transactions: {e}")
        return []


# Convenience helper functions
def get_all_categories() -> List[str]:
    """Get list of all product categories."""
    try:
        response = supabase.table('categories').select('name').execute()
        return [cat['name'] for cat in response.data]
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []


def get_category_products(category: str) -> List[Dict[str, Any]]:
    """
    Get all active products in a specific category.
    
    Args:
        category: Category name
        
    Returns:
        List of products in the category
    """
    try:
        response = supabase.table('products') \
            .select('id, name, brand, retail_price, categories!inner(name)') \
            .eq('status', 'active') \
            .eq('categories.name', category) \
            .execute()
        return response.data
    except Exception as e:
        print(f"Error getting category products: {e}")
        return []