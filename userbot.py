import json
import os
import asyncio
import importlib.util
from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.sessions import StringSession

print("Bot başlatılıyor...")

if not os.path.exists("config.json"):
    print("config.json bulunamadı!")
    exit()

with open("config.json", "r") as f:
    config = json.load(f)

api_id = config.get("api_id")
api_hash = config.get("api_hash")
session_string = config.get("session_string")
admin_username = config.get("admin_username")

if not all([api_id, api_hash, session_string, admin_username]):
    print("Lütfen config.json dosyasındaki tüm alanları doldurun.")
    exit()

client = TelegramClient(StringSession(session_string), api_id, api_hash)

filters = {}
afk_mode = False
afk_reason = ""
afk_users = set()

@client.on(events.NewMessage(pattern=r"\.alive"))
async def alive(event):
    if event.sender_id == (await client.get_me()).id:
        await event.reply("✅ JudgeUserbot Aktif!")

@client.on(events.NewMessage(pattern=r"\.id"))
async def get_id(event):
    if event.sender_id == (await client.get_me()).id:
        reply = await event.get_reply_message()
        if reply:
            await event.reply(f"👤 Kullanıcı ID: `{reply.sender_id}`")
        else:
            await event.reply("Lütfen bir mesaja yanıt verin.")

@client.on(events.NewMessage(pattern=r"\.wlive"))
async def wlive(event):
    try:
        sender = await event.get_sender()
        if sender.username != admin_username:
            await event.reply("❌ Bu komutu kullanmak için yetkiniz yok.")
            return
        await event.reply("Userbotunuz çalışıyor ve sana bişey demek istiyor..\nSeni seviyorum ByJudge ❤️\nBot Versiyonu: v1")
    except Exception as e:
        await event.reply(f"Hata oluştu: {e}")

@client.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?"))
async def afk_set(event):
    global afk_mode, afk_reason, afk_users
    if event.sender_id != (await client.get_me()).id:
        return
    afk_mode = True
    afk_reason = event.pattern_match.group(1) or "AFK"
    afk_users.clear()
    await event.reply(f"AFK moduna geçildi: {afk_reason}")

@client.on(events.NewMessage(pattern=r"\.back"))
async def afk_off(event):
    global afk_mode, afk_reason, afk_users
    if event.sender_id != (await client.get_me()).id:
        return
    afk_mode = False
    afk_reason = ""
    afk_users.clear()
    await event.reply("AFK modu kapatıldı.")

@client.on(events.NewMessage())
async def auto_afk_reply(event):
    global afk_users
    if afk_mode and event.is_private and event.sender_id != (await client.get_me()).id:
        if event.sender_id not in afk_users:
            afk_users.add(event.sender_id)
            await event.reply(afk_reason)

@client.on(events.NewMessage(pattern=r"\.filter (.+?) (.+)", outgoing=True))
async def add_filter(event):
    if event.sender_id != (await client.get_me()).id:
        return
    msg, reply = event.pattern_match.group(1), event.pattern_match.group(2)
    filters[msg.lower()] = reply
    await event.reply(f"✅ Filter eklendi: `{msg}`")

@client.on(events.NewMessage(pattern=r"\.unfilter (.+)", outgoing=True))
async def remove_filter(event):
    if event.sender_id != (await client.get_me()).id:
        return
    msg = event.pattern_match.group(1).lower()
    if msg in filters:
        del filters[msg]
        await event.reply(f"🗑 Filter silindi: `{msg}`")
    else:
        await event.reply("❌ Böyle bir filter yok.")

@client.on(events.NewMessage())
async def filter_reply(event):
    if event.is_private and not event.out:
        msg = event.raw_text.lower()
        if msg in filters and not afk_mode:
            await event.reply(filters[msg])

# Tüm modülleri yükle
if os.path.exists("modules"):
    for filename in os.listdir("modules"):
        if filename.endswith(".py"):
            path = os.path.join("modules", filename)
            spec = importlib.util.spec_from_file_location("module.name", path)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)

with client:
    print("✅ JudgeUserbot başlatıldı!")
    client.run_until_disconnected()
