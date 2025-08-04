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
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Tokens from .env
TOKEN = os.getenv("8320732255:AAE4kkllUbYK7E2PiIJSFe_Yu4XVs4HTshM")
GEMINI_KEY = os.getenv("AIzaSyC2GokN9VZE2ClYmG13DYlkLtujncKAbaE")

bot = Bot(token=TOKEN)
dp = Dispatcher()
conversations = defaultdict(lambda: deque(maxlen=10))

@dp.message(CommandStart())
async def start_handler(message: Message):
    conversations[message.from_user.id].clear()
    await message.answer(
        "Hello bratha! I be Babatunde from Senegal. You wan talk, I dey here.\nUse /clear to clean my memory."
    )

@dp.message(Command(commands=["clear"]))
async def clear_handler(message: Message):
    conversations[message.from_user.id].clear()
    await message.answer("Okay bratha, me forget wetin we talk before!")

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    conversations[user_id].append({"role": "user", "content": message.text})

    await bot.send_chat_action(message.chat.id, action="typing")

    reply = await get_ai_response(conversations[user_id])
    if reply:
        conversations[user_id].append({"role": "assistant", "content": reply})
        await message.answer(reply)
    else:
        await message.answer("You know, me no sabi dis tech thing now. Try again, bratha.")

async def get_ai_response(history):
    prompt = history[-1]["content"] if history else "Hello"

    url = "https://generativelanguage.googleapis.com/v1beta3/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, params=params, json=data) as resp:
                res = await resp.json()
                return res["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logging.error(f"AI error: {e}")
        return None

async def main():
    logging.info("Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")


