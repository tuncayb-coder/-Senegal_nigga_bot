#!/usr/bin/env python3
import os
import asyncio
import aiohttp
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from collections import defaultdict, deque
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Your real tokens (DO NOT SHARE PUBLICLY in real projects!)
TOKEN = "8320732255:AAEkhPUeNbcFTEbA8FDnAyuHKnnLAj1c5Eo"
OPENROUTER_KEY = "AIzaSyC2GokN9VZE2ClYmG13DYlkLtujncKAbaE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

conversations = defaultdict(lambda: deque(maxlen=10))

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    conversations[user_id].clear()
    welcome = (
        "Hello! I am Babatunde Kwame N'Golo Chukwuemeka Olamide Mandela Wobbleton from Senegal. How can I help you bratha?\n\n"
        "Use /clear to reset our chat."
    )
    await message.answer(welcome)

@dp.message(Command(commands=["clear"]))
async def clear_handler(message: Message):
    user_id = message.from_user.id
    conversations[user_id].clear()
    await message.answer("🗑️ Okay bratha! I forget everything now, we start fresh!")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text or ""

    conversations[user_id].append({"role": "user", "content": text})

    await bot.send_chat_action(message.chat.id, action="typing")

    response = await get_ai_response(conversations[user_id], user_id)

    if response:
        conversations[user_id].append({"role": "assistant", "content": response})
        await message.answer(response)
    else:
        fallback = random.choice([
            "Hey bratha! Brain no dey work good now. Try later, no worries.",
            "Ah bratha, me get small wahala here. Come back soon!",
            "You know, me no too sabi tech tings. Try again later, bratha.",
        ])
        await message.answer(fallback)

async def get_ai_response(conversation_history, user_id):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/Senegal_nigga_bot",
        "X-Title": "Movie Finder Bot"
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are Babatunde from Senegal. You friendly, relaxed guy who talk casual. "
                "Make lots of English mistakes like 'thas', 'doin', drop letters. Call everyone 'bratha'. "
                "Give medium length answers like 3-4 sentences. You try to help but admit when you not so smart "
                "about technical things. Use words like 'you know', 'no worries', 'I'll give it a try'. "
                "Be ironic and funny sometimes. Don't use emojis much, just talk natural and friendly."
            )
        }
    ] + list(conversation_history)

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": messages,
        "max_tokens": 120,
        "temperature": 0.7
    }

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=payload
            ) as resp:
                data = await resp.json()
                if resp.status == 200 and "choices" in data:
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenRouter error {resp.status}: {data}")
                    return await fallback_huggingface_response(conversation_history)
    except Exception as e:
        logger.error(f"Exception during AI response: {e}")
        return await fallback_huggingface_response(conversation_history)

async def fallback_huggingface_response(conversation_history):
    prompt = conversation_history[-1]["content"] if conversation_history else "Hello"
    hf_url = "https://api-inference.huggingface.co/models/gpt2"

    headers = {
        "Accept": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                hf_url,
                headers=headers,
                json={"inputs": prompt}
            ) as resp:
                data = await resp.json()
                if resp.status == 200 and isinstance(data, list) and "generated_text" in data[0]:
                    return data[0]["generated_text"]
                else:
                    logger.error(f"HuggingFace fallback error {resp.status}: {data}")
                    return None
    except Exception as e:
        logger.error(f"Exception in fallback HuggingFace: {e}")
        return None

async def main():
    logger.info("🚀 Bot starting...")
    me = await bot.get_me()
    logger.info(f"Running as @{me.username}")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped manually")


{
  "build": {
    "builder": "NIXPACKS"
  },
  "start": "python telegrambot.py"
}

