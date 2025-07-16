import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import json

from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

# Load plugins dynamically from plugins folder
plugins_folder = "plugins"

for file in os.listdir(plugins_folder):
    if file.endswith(".py"):
        mod_name = file[:-3]
        mod = __import__(f"plugins.{mod_name}", fromlist=["*"])

async def main():
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
