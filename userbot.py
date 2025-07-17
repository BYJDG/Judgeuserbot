from telethon import TelegramClient, events
from config import api_id, api_hash, session_name
import os
from dotenv import load_dotenv

load_dotenv()

client = TelegramClient(session_name, api_id, api_hash)

# OWNER sabit kalacak (senin ID'n), buraya dokunma
OWNER_ID = 5181234567
OWNER_USERNAME = "@byjudgee"

# Global değişken olarak bot sahibini tanımla
BOT_USER_ID = None
BOT_USERNAME = None

@client.on(events.NewMessage(outgoing=True, pattern=r"\.wlive"))
async def handle_wlive(event):
    if event.sender_id != OWNER_ID:
        return
    await event.reply("✅ JudgeUserBot aktif.")

# Başlangıçta kendi kullanıcı bilgilerini al
async def setup_bot_user():
    global BOT_USER_ID, BOT_USERNAME
    me = await client.get_me()
    BOT_USER_ID = me.id
    BOT_USERNAME = me.username
    print(f"🔑 Bot hesabı: {BOT_USERNAME} [{BOT_USER_ID}]")

# Bot başlasın
async def main():
    await setup_bot_user()
    print("🚀 JudgeUserBot başlatıldı.")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
