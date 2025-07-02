import os
import json
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import PeerUser

# Konfigürasyon dosyasını kontrol et
CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("⚠️ config.json bulunamadı!")
    api_id = input("API ID: ")
    api_hash = input("API HASH: ")
    owner_id = input("Bot sahibi Telegram kullanıcı ID: ")

    config = {
        "api_id": int(api_id),
        "api_hash": api_hash,
        "owner_id": int(owner_id)
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
else:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
owner_id = config["owner_id"]

session_name = "session"

# Session dosyası kontrolü
if os.path.exists(f"{session_name}.session"):
    print("⚠️ Zaten kayıtlı bir hesabınız var.")
    retry = input("🔁 Yeniden giriş yapmak ister misiniz? (Y/N): ").strip().lower()
    if retry == "y":
        os.remove(f"{session_name}.session")
        print("🗑️ Oturum silindi. Giriş başlatılıyor...")
    else:
        print("✅ Kayıtlı oturum üzerinden devam ediliyor...")

# TelegramClient oluştur
client = TelegramClient(session_name, api_id, api_hash)

# AFK sistemleri
is_afk = False
afk_reason = ""
afk_replied_users = set()

# BOT BAŞLANGICI
@client.on(events.NewMessage(outgoing=True, pattern=r"\.alive"))
async def alive_handler(event):
    if event.sender_id == (await client.get_me()).id:
        await event.reply("✅ **JudgeUserBot Çalışıyor!**\n💡 Sürüm: v1.0")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.afk (.+)"))
async def afk_set(event):
    global is_afk, afk_reason, afk_replied_users
    afk_reason = event.pattern_match.group(1)
    is_afk = True
    afk_replied_users = set()
    await event.reply("🤖 AFK moduna geçildi.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.back"))
async def afk_unset(event):
    global is_afk, afk_reason, afk_replied_users
    is_afk = False
    afk_reason = ""
    afk_replied_users = set()
    await event.reply("✅ AFK modu kapatıldı.")

@client.on(events.NewMessage(incoming=True))
async def afk_auto_reply(event):
    global is_afk, afk_reason, afk_replied_users
    if is_afk and event.sender_id not in afk_replied_users:
        afk_replied_users.add(event.sender_id)
        try:
            await event.reply(afk_reason)
        except Exception:
            pass  # Özellikle grup gibi yerlerde yetki hatası olabilir

@client.on(events.NewMessage(outgoing=True, pattern=r"\.wlive"))
async def wlive(event):
    if event.sender_id == owner_id:
        await event.reply("✅ Userbotunuz çalışıyor ve sana bir şey demek istiyor...\n❤️ Seni seviyorum ByJudge!\n\n📌 Versiyon: v1")
    else:
        await event.reply("⛔ Bu komutu kullanmak için yetkiniz yok.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.id"))
async def id_handler(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        await event.reply(f"🆔 Kullanıcının ID'si: `{user_id}`")
    else:
        await event.reply("ℹ️ Bu komutu kullanmak için bir mesaja yanıt verin.")

# BOTU BAŞLAT
async def main():
    print("🚀 Bot başlatılıyor...")
    await client.start()
    print("✅ Bot aktif!")

    me = await client.get_me()
    print(f"Bot giriş yaptı: {me.first_name} (@{me.username})")

    await client.run_until_disconnected()

# ASENKRON ÇALIŞTIR
asyncio.run(main())
