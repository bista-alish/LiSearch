"""
Configuration management for the liquor store chat application.
Loads environment variables and provides centralized access to settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        """Initialize settings and validate required environment variables."""
        self.supabase_url = self._get_required_env('SUPABASE_URL')
        self.supabase_key = self._get_required_env('SUPABASE_KEY')
        self.gemini_api_key = self._get_required_env('GEMINI_API_KEY')
        
        # Optional: Add debug flag for development
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    def _get_required_env(self, key: str) -> str:
        """
        Get a required environment variable or raise an error.
        
        Args:
            key: The environment variable name
            
        Returns:
            The environment variable value
            
        Raises:
            ValueError: If the environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Missing required environment variable: {key}\n"
                f"Please ensure your .env file contains {key}=your_value"
            )
        return value
    
    def __repr__(self):
        """Return a safe string representation (without exposing secrets)."""
        return (
            f"Settings(supabase_url={self.supabase_url[:20]}..., "
            f"keys_loaded=True)"
        )

# Create a singleton instance
settings = Settings()

# For convenience, expose settings directly
SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_key
GEMINI_API_KEY = settings.gemini_api_key
DEBUG = settings.debug