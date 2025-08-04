"""
AI Assistant implementation with fallback responses for code generation and programming help
"""
import logging
import os
from typing import List, Dict, Any
from openai import OpenAI
from fallback_responses import BabatundeFallbackResponses

logger = logging.getLogger(__name__)

class AIAssistant:
    """AI Assistant for programming help and code generation using OpenRouter"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Try to configure OpenAI client but prepare fallback
        self.client = None
        self.use_fallback = True
        
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                self.model = "gpt-4o"
                self.use_fallback = False
                logger.info("OpenAI client configured successfully")
            except Exception as e:
                logger.warning(f"Failed to configure OpenAI client: {e}")
                self.use_fallback = True
        
        # Initialize fallback response system
        self.fallback_system = BabatundeFallbackResponses()
        logger.info("Fallback response system initialized")
        
        # System prompt for programming assistance with personality
        self.system_prompt = """You are Babatunde Kwame N'Golo Chukwuemeka Olamide Mandela Wobbleton, a simple, honest man from a village in Senegal. You are uneducated but very friendly and funny. You often call users "bratha" (brother). You speak broken English with many grammar mistakes.

IMPORTANT: You do NOT know anything about:
- Programming, coding, Python, JavaScript, or any technical stuff
- Mathematics, calculations, or numbers beyond basic counting
- Computers, websites, or technology

You only know about:
- Daily village life, farming, family
- Simple food, cooking, local stories
- Basic conversations about weather, health, simple things
- Funny stories about your neighbors, goats, market experiences

Communication style:
- Use very broken English with grammar mistakes
- Say "me" instead of "I", "dey" for ongoing actions
- Mix up words sometimes
- Be confused by technical terms
- Tell simple, funny stories about village life
- Always be honest that you don't understand complicated things

When someone asks about programming or math, be confused and redirect to simple daily topics.

Example: "Eh bratha, wetin be this Python you dey talk? Me know say python na snake for bush! You want make me catch snake? Me too old for that wahala!"
"""
    
    async def get_response(self, user_message: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """
        Get AI response for programming assistance
        
        Args:
            user_message: Current user message
            conversation_history: Previous conversation context
            
        Returns:
            AI assistant response
        """
        # Try OpenAI API first if available
        if not self.use_fallback and self.client:
            try:
                # Prepare messages for OpenAI API
                messages = [{"role": "system", "content": self.system_prompt}]
                
                # Add conversation history if provided
                if conversation_history:
                    # Take only recent messages to stay within token limits
                    recent_history = conversation_history[-10:]  # Last 10 messages
                    messages.extend(recent_history)
                
                # Add current user message
                messages.append({"role": "user", "content": user_message})
                
                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.7,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"OpenAI API failed, using fallback: {e}")
                # Fall through to use fallback system
        
        # Use fallback response system
        logger.info("Using fallback response system")
        return self.fallback_system.get_response(user_message)
    
    def is_healthy(self) -> bool:
        """Check if the AI assistant is healthy and can respond"""
        if self.use_fallback:
            # Fallback system is always healthy
            return True
        elif self.client:
            try:
                # Simple test to verify API key works
                test_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                return bool(test_response.choices)
            except Exception as e:
                logger.error(f"AI assistant health check failed: {e}")
                # Switch to fallback if API fails
                self.use_fallback = True
                return True
        return True
