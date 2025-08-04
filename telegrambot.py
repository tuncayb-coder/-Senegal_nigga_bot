import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from collections import defaultdict, deque

import google.generativeai as genai

# 🔐 Your actual API keys (hardcoded for now; better use env vars on Railway)
BOT_TOKEN = "8320732255:AAEkhPUeNbcFTEbA8FDnAyuHKnnLAj1c5Eo"
GEMINI_API_KEY = "AIzaSyC2GokN9VZE2ClYmG13DYlkLtujncKAbaE"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Store user conversations
conversations = defaultdict(lambda: deque(maxlen=10))

# Babatunde's personality prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You be Babatunde from Senegal. You dey speak broken English, no go school well. "
        "You dey call people 'bratha', 'sistah'. You dey try help but you no sabi tech tings. "
        "Use phrases like 'me no sabi', 'ah bratha', 'me head no strong today', 'me try help'. "
        "Be friendly and casual. Talk short and funny."
    )
}

@dp.message(CommandStart())
async def start_handler(message: Message):
    conversations.clear()
    await message.answer(
        "Wetin dey bratha! Me be Babatunde. You wan talk? Drop sometin for me make I try help."
    )

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_text = message.text.strip()
    conversations[user_id].append({"role": "user", "content": user_text})

    await bot.send_chat_action(message.chat.id, action="typing")

    response = await ask_gemini(conversations[user_id])
    if response:
        conversations[user_id].append({"role": "assistant", "content": response})
        await message.answer(response)
    else:
        await message.answer("Ah bratha, me head no strong now. Try later small.")

async def ask_gemini(history):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        full_prompt = [SYSTEM_PROMPT] + list(history)
        response = model.generate_content(full_prompt, temperature=0.7, max_output_tokens=250)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None

async def main():
    logger.info("🚀 Bot dey start...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())

