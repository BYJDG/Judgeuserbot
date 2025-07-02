import os import json import asyncio from telethon import TelegramClient, events, functions from telethon.sessions import StringSession

print("Bot başlatılıyor...")

CONFIG_FILE = "config.json" SESSION_FILE = "userbot.session"

Kurulum kontrolü ve config dosyasını oluşturma

def load_config(): if not os.path.exists(CONFIG_FILE): print("İlk kurulum yapılıyor...") api_id = input("API ID: ") api_hash = input("API Hash: ") phone = input("Telefon numaranız (örn: +905...) : ") config = { "api_id": int(api_id), "api_hash": api_hash, "phone": phone, "admin_username": "byjudgee" } with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=4) else: with open(CONFIG_FILE, "r") as f: config = json.load(f) return config

config = load_config()

client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])

Oturum kontrolü

async def main(): if not await client.is_user_authorized(): await client.start(phone=config["phone"]) print("Giriş yapıldı ve oturum kaydedildi.") else: print("Oturum zaten kayıtlı. Giriş yapılmış.")

me = await client.get_me()
owner_id = me.id
print(f"Bot sahibi id ayarlandı: {owner_id}")

afk_mode = False
afk_reason = ""
afk_replied_users = set()
filters = {}

@client.on(events.NewMessage(pattern=r"\.alive"))
async def alive_handler(event):
    if event.sender_id == owner_id:
        await event.reply("JudgeUserBot Aktif! ✅")

@client.on(events.NewMessage(pattern=r"\.id"))
async def id_handler(event):
    if event.sender_id == owner_id:
        if event.reply_to_msg_id:
            replied = await event.get_reply_message()
            await event.reply(f"ID: {replied.sender_id}")
        else:
            await event.reply(f"ID: {event.sender_id}")

@client.on(events.NewMessage(pattern=r"\.afk ?(.*)"))
async def afk_set(event):
    nonlocal afk_mode, afk_reason, afk_replied_users
    if event.sender_id == owner_id:
        afk_reason = event.pattern_match.group(1)
        afk_mode = True
        afk_replied_users = set()
        await event.reply("AFK moduna geçildi.")

@client.on(events.NewMessage(pattern=r"\.back"))
async def afk_off(event):
    nonlocal afk_mode
    if event.sender_id == owner_id:
        afk_mode = False
        await event.reply("AFK modu kapatıldı.")

@client.on(events.NewMessage(pattern=r"\.filter (.+?) (.+)", outgoing=True))
async def add_filter(event):
    if event.sender_id == owner_id:
        keyword, reply = event.pattern_match.group(1), event.pattern_match.group(2)
        filters[keyword.lower()] = reply
        await event.reply(f"Filter eklendi: {keyword} -> {reply}")

@client.on(events.NewMessage(pattern=r"\.unfilter (.+)", outgoing=True))
async def remove_filter(event):
    if event.sender_id == owner_id:
        keyword = event.pattern_match.group(1).lower()
        if keyword in filters:
            del filters[keyword]
            await event.reply(f"Filter kaldırıldı: {keyword}")
        else:
            await event.reply("Böyle bir filter yok.")

@client.on(events.NewMessage(pattern=r"\.wlive"))
async def wlive_command(event):
    sender = await event.get_sender()
    if sender.username and sender.username.lower() == config["admin_username"].lower():
        await event.reply("Userbotunuz çalışıyor ve sana bişey demek istiyor..\nSeni seviyorum ByJudge ❤️\nBot Versiyonu: v1")
    else:
        await event.reply("Bu komutu kullanmak için yetkiniz yok.")

@client.on(events.NewMessage())
async def auto_reply(event):
    if event.sender_id == owner_id:
        return
    if afk_mode and event.sender_id not in afk_replied_users:
        afk_replied_users.add(event.sender_id)
        await event.reply(f"{afk_reason}")
    elif event.raw_text.lower() in filters:
        await event.reply(filters[event.raw_text.lower()])

await client.run_until_disconnected()

with client: client.loop.run_until_complete(main())

