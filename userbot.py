from telethon import TelegramClient, events
import asyncio

# config.py'den API ID ve HASH al
from config import API_ID, API_HASH

# Client oluştur
client = TelegramClient('session', API_ID, API_HASH)

# Örnek komut
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Bot çalışıyor!")

# Botu başlat
with client:
    client.run_until_disconnected()
