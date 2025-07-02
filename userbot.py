import json
import os
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import PhoneNumberBannedError

# Config dosyası varsa yükle
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {}

api_id = config.get("api_id")
api_hash = config.get("api_hash")
phone = config.get("phone")
owner_username = config.get("owner_username")  # Admin için kullanıcı adı örn: "byjudgee"

if not api_id or not api_hash or not phone or not owner_username:
    print("Lütfen önce config.json dosyasını doldurun veya kurulum scriptini kullanın.")
    exit(1)

client = TelegramClient("session", api_id, api_hash)

afk = False
afk_reason = ""
filter_map = {}
answered_users = set()  # AFK modunda bir kişiye sadece 1 cevap için

@client.on(events.NewMessage(pattern=r"\.alive"))
async def alive(event):
    if event.sender_id == (await client.get_me()).id:
        await event.reply("Bot aktif ve çalışıyor! 🟢")

@client.on(events.NewMessage(pattern=r"\.wlive"))
async def wlive(event):
    sender = await event.get_sender()
    username = sender.username if sender else ""
    if username.lower() != owner_username.lower():
        await event.reply("❌ Bu komutu kullanmak için yetkiniz yok.")
        return
    await event.reply("Userbotunuz çalışıyor ve sana bişey demek istiyor..\nSeni seviyorum ByJudge ❤️\nBot Versiyonu: v1")

@client.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?"))
async def afk_cmd(event):
    global afk, afk_reason, answered_users
    if event.sender_id != (await client.get_me()).id:
        return
    afk = True
    afk_reason = event.pattern_match.group(1) or "AFK"
    answered_users = set()
    await event.reply(f"AFK modu aktif: {afk_reason}")

@client.on(events.NewMessage(pattern=r"\.back"))
async def back_cmd(event):
    global afk, afk_reason, answered_users
    if event.sender_id != (await client.get_me()).id:
        return
    afk = False
    afk_reason = ""
    answered_users = set()
    await event.reply("AFK modu kapatıldı.")

@client.on(events.NewMessage(pattern=r"\.filter\s+(\S+)\s+(.+)"))
async def filter_add(event):
    global filter_map
    if event.sender_id != (await client.get_me()).id:
        return
    key = event.pattern_match.group(1)
    val = event.pattern_match.group(2)
    filter_map[key] = val
    await event.reply(f"Filter eklendi: '{key}' → '{val}'")

@client.on(events.NewMessage(pattern=r"\.unfilter\s+(\S+)"))
async def filter_remove(event):
    global filter_map
    if event.sender_id != (await client.get_me()).id:
        return
    key = event.pattern_match.group(1)
    if key in filter_map:
        filter_map.pop(key)
        await event.reply(f"Filter kaldırıldı: '{key}'")
    else:
        await event.reply(f"Filter bulunamadı: '{key}'")

@client.on(events.NewMessage)
async def auto_reply(event):
    global afk, afk_reason, answered_users, filter_map
    sender_id = event.sender_id
    me_id = (await client.get_me()).id

    if sender_id == me_id:
        return  # Kendi mesajına cevap verme

    # AFK modu yanıtı
    if afk:
        if sender_id not in answered_users:
            answered_users.add(sender_id)
            await event.reply(afk_reason)
        return

    # Filtreli cevap
    text = event.raw_text.lower()
    for key in filter_map:
        if key.lower() in text:
            await event.reply(filter_map[key])
            break

async def main():
    print("Bot başlatılıyor...")
    await client.start(phone)
    print("Bot aktif!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except PhoneNumberBannedError:
        print("Telefon numaranız Telegram tarafından engellenmiş olabilir.")
    except Exception as e:
        print(f"Hata: {e}")
