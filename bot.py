"""
Telegram Bot implementation with AI conversation capabilities
"""
import logging
import os
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta

from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
from telegram.constants import ParseMode

from ai_assistant import AIAssistant
from rate_limiter import RateLimiter
from config import Config

logger = logging.getLogger(__name__)

class TelegramAIBot:
    """Telegram bot with AI conversation capabilities"""
    
    def __init__(self):
        self.config = Config()
        self.ai_assistant = AIAssistant()
        self.rate_limiter = RateLimiter()
        
        # Store conversation contexts per user
        self.user_contexts: Dict[int, list] = {}
        
        # Initialize bot application
        self.application = Application.builder().token(self.config.telegram_token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Message handler for regular conversation
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.first_name or "User"
        
        welcome_message = (
            f"Eh {username}! Me be Babatunde Kwame N'Golo Chukwuemeka Olamide Mandela Wobbleton from small village for Senegal. How you dey bratha?\n\n"
            "Me no too sabi all these tech tings but we fit talk about daily life, food, weather, and simple tings. Use /clear if you want forget our talk."
        )
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"User {user_id} started conversation")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "Ah bratha, you want help? Me no too understand all these command ting but make me try explain:\n\n"
            "/start - Say hello to me\n"
            "/help - You get am now\n" 
            "/clear - Make me forget wetin we talk before\n"
            "/status - Check if me still dey here\n\n"
            "Me no sabi programming or computer wahala. But we fit talk about:\n"
            "• Food wey me like\n"
            "• Weather for my village\n"
            "• Stories about my goat and neighbors\n"
            "• Simple tings for daily life\n\n"
            "Just talk to me like normal person, no need big big grammar!"
        )
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        
        # Clear user's conversation context
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
        
        await update.message.reply_text(
            "Ah bratha! Me don forget everything now. We start fresh like new day!",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Cleared conversation context for user {user_id}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        context_length = len(self.user_contexts.get(user_id, []))
        
        status_message = (
            "Bratha, you want know if me dey fine?\n\n"
            f"Me still dey here and me dey talk with you\n"
            f"We don talk {context_length} times today\n"
            f"Time now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Me no understand all these computer ting but me still dey answer you!"
        )
        
        await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        try:
            # Check rate limiting
            if not self.rate_limiter.is_allowed(user_id):
                await update.message.reply_text(
                    "⚠️ Please wait a moment before sending another message. "
                    "Rate limit exceeded.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, 
                action="typing"
            )
            
            # Get or initialize user conversation context
            if user_id not in self.user_contexts:
                self.user_contexts[user_id] = []
            
            # Add user message to context
            self.user_contexts[user_id].append({
                "role": "user",
                "content": user_message
            })
            
            # Keep context manageable (last 10 exchanges)
            if len(self.user_contexts[user_id]) > 20:
                self.user_contexts[user_id] = self.user_contexts[user_id][-20:]
            
            # Get AI response
            ai_response = await self.ai_assistant.get_response(
                user_message, 
                self.user_contexts[user_id]
            )
            
            # Add AI response to context
            self.user_contexts[user_id].append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Send response with proper formatting
            await self._send_formatted_response(update, ai_response)
            
            logger.info(f"Processed message from user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}")
            
            # Check for specific API errors
            if "402" in str(e) or "Insufficient credits" in str(e) or "quota" in str(e).lower():
                await update.message.reply_text(
                    "Ah bratha, me got small wahala with the API thing. Maybe quota finished or something.\n\n"
                    "Try again later, no? Sometimes these tech tings just need small time to work again."
                )
            else:
                # Use fallback Babatunde responses like the original code
                import random
                fallback_responses = [
                    "Hey bratha! Brain no dey work good now. Try later, no worries.",
                    "Ah bratha, me get small wahala here. Come back soon!",
                    "You know, me no too sabi tech tings. Try again later, bratha.",
                    "Sorry bratha, something go wrong. Give me small time, I go fix am."
                ]
                fallback = random.choice(fallback_responses)
                await update.message.reply_text(fallback)
    
    async def _send_formatted_response(self, update: Update, response: str):
        """Send response with proper formatting for code blocks"""
        try:
            # Split long messages to avoid Telegram's limit
            max_length = 4000
            
            if len(response) <= max_length:
                await update.message.reply_text(
                    response, 
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # Split into chunks
                chunks = []
                current_chunk = ""
                
                lines = response.split('\n')
                for line in lines:
                    if len(current_chunk + line + '\n') > max_length:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = line + '\n'
                        else:
                            # Single line too long, force split
                            chunks.append(line[:max_length])
                            current_chunk = line[max_length:] + '\n'
                    else:
                        current_chunk += line + '\n'
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Send chunks
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await update.message.reply_text(
                            chunk + f"\n\n*[Message {i+1}/{len(chunks)}]*",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    else:
                        await update.message.reply_text(
                            f"*[Message {i+1}/{len(chunks)}]*\n\n" + chunk,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        
        except Exception as e:
            logger.error(f"Error sending formatted response: {e}")
            # Fallback to plain text
            await update.message.reply_text(
                f"Response (plain text due to formatting error):\n\n{response[:4000]}"
            )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    def run(self):
        """Run the bot"""
        try:
            # Set up bot commands
            asyncio.get_event_loop().run_until_complete(
                self._setup_bot_commands()
            )
            
            # Start the bot
            if self.config.webhook_url:
                # Webhook mode (for Replit)
                self.application.run_webhook(
                    listen="0.0.0.0",
                    port=5000,
                    webhook_url=self.config.webhook_url,
                    secret_token=self.config.webhook_secret
                )
            else:
                # Polling mode (for local development)
                self.application.run_polling(allowed_updates=Update.ALL_TYPES)
                
        except Exception as e:
            logger.error(f"Failed to run bot: {e}")
            raise
    
    async def _setup_bot_commands(self):
        """Setup bot commands for Telegram UI"""
        commands = [
            BotCommand("start", "Initialize the AI assistant"),
            BotCommand("help", "Show available commands and usage"),
            BotCommand("clear", "Clear conversation history"),
            BotCommand("status", "Check bot status")
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands configured")
