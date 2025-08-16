from telegram.ext import Application
import asyncio

BOT_TOKEN = "7739338057:AAHFzDpOgh-XrBr-vqWvV5TEqKs62HQS9zY"
CHANNEL_USERNAME = "@num_insight"  # Публичное имя канала

async def get_id():
    app = Application.builder().token(BOT_TOKEN).build()
    async with app:
        chat = await app.bot.get_chat(CHANNEL_USERNAME)
        print(f"ID канала: {chat.id}")

asyncio.run(get_id())
"-1002496521038"