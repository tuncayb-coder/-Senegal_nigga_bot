"""
Configuration management for the Telegram AI Bot
"""
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        self.telegram_token = self._get_required_env("TELEGRAM_BOT_TOKEN")
        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        
        # Optional webhook configuration (for Replit deployment)
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "default_webhook_secret")
        
        # Bot configuration
        self.bot_username = os.getenv("BOT_USERNAME", "ai_coding_assistant_bot")
        self.admin_user_ids = self._parse_admin_ids(os.getenv("ADMIN_USER_IDS", ""))
        
        # API configuration
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.openai_model = "gpt-4o"
        
        # Rate limiting configuration
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        self._validate_config()
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _parse_admin_ids(self, admin_ids_str: str) -> list:
        """Parse admin user IDs from comma-separated string"""
        if not admin_ids_str:
            return []
        
        try:
            return [int(user_id.strip()) for user_id in admin_ids_str.split(",") if user_id.strip()]
        except ValueError as e:
            logger.error(f"Error parsing admin user IDs: {e}")
            return []
    
    def _validate_config(self):
        """Validate configuration values"""
        # Validate tokens are not empty
        if not self.telegram_token or self.telegram_token == "your_telegram_bot_token_here":
            raise ValueError("Invalid Telegram bot token")
        
        if not self.openai_api_key or self.openai_api_key == "your_openai_api_key_here":
            raise ValueError("Invalid OpenAI API key")
        
        # Validate numeric values
        if self.openai_max_tokens < 100 or self.openai_max_tokens > 4000:
            logger.warning(f"OpenAI max tokens value {self.openai_max_tokens} may be outside optimal range")
        
        if self.openai_temperature < 0 or self.openai_temperature > 2:
            logger.warning(f"OpenAI temperature value {self.openai_temperature} may be outside optimal range")
        
        # Log configuration (without sensitive values)
        logger.info("Bot configuration loaded:")
        logger.info(f"  - Bot username: {self.bot_username}")
        logger.info(f"  - Webhook URL: {'Set' if self.webhook_url else 'Not set'}")
        logger.info(f"  - Admin users: {len(self.admin_user_ids)} configured")
        logger.info(f"  - OpenAI max tokens: {self.openai_max_tokens}")
        logger.info(f"  - OpenAI temperature: {self.openai_temperature}")
        logger.info(f"  - OpenAI model: {self.openai_model}")
        logger.info(f"  - Using OpenAI API directly")
        logger.info(f"  - Rate limit: {self.rate_limit_requests} requests per {self.rate_limit_window} seconds")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin"""
        return user_id in self.admin_user_ids
    
    def get_webhook_info(self) -> dict:
        """Get webhook configuration info"""
        return {
            "url": self.webhook_url,
            "secret_token": self.webhook_secret,
            "enabled": bool(self.webhook_url)
        }
