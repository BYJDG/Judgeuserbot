from telethon import TelegramClient, events
import os
import json
import asyncio

# Config dosyasını yükle
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
else:
    print("config.json dosyası bulunamadı! Lütfen config.json.example dosyasını kopyalayıp doldurun.")
    exit()

api_id = config.get("api_id")
api_hash = config.get("api_hash")

client = TelegramClient("session", api_id, api_hash)

# AFK ve filtre sistemleri
afk_mode = False
afk_reason = ""
afk_replied_users = set()
filter_dict = {}

# Bot hazır mesajı
@client.on(events.NewMessage(outgoing=True, pattern=r"\.alive"))
async def alive_handler(event):
    await event.reply("Bot çalışıyor! ✅")

# AFK aç
@client.on(events.NewMessage(outgoing=True, pattern=r"\.afk(?: (.+))?"))
async def afk_on(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = True
    afk_reason = event.pattern_match.group(1) or "Belirtilmedi"
    afk_replied_users = set()
    await event.reply(f"AFK moduna geçildi. Sebep: {afk_reason}")

# AFK kapat
@client.on(events.NewMessage(outgoing=True, pattern=r"\.back"))
async def afk_off(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = False
    afk_reason = ""
    afk_replied_users = set()
    await event.reply("AFK modu kapatıldı.")

# Filtre ekle
@client.on(events.NewMessage(outgoing=True, pattern=r"\.filter (.+?) (.+)"))
async def filter_add(event):
    try:
        text = event.pattern_match.group(1).lower()
        reply = event.pattern_match.group(2)
        filter_dict[text] = reply
        await event.reply(f'Filtre eklendi: "{text}" -> "{reply}"')
    except Exception as e:
        await event.reply(f"Hata: {e}")

# Filtre kaldır
@client.on(events.NewMessage(outgoing=True, pattern=r"\.unfilter (.+)"))
async def filter_remove(event):
    text = event.pattern_match.group(1).lower()
    if text in filter_dict:
        del filter_dict[text]
        await event.reply(f"Filtre kaldırıldı: {text}")
    else:
        await event.reply("Bu filtre bulunamadı.")

# Yardım komutu
@client.on(events.NewMessage(outgoing=True, pattern=r"\.judge"))
async def help_handler(event):
    msg = (
        "**Komutlar:**\n"
        ".alive - Botun çalıştığını gösterir\n"
        ".afk <sebep> - AFK modunu açar\n"
        ".back - AFK modunu kapatır\n"
        ".filter <mesaj> <cevap> - Otomatik cevap ekler\n"
        ".unfilter <mesaj> - Otomatik cevabı kaldırır\n"
        ".judge - Bu mesajı gösterir"
    )
    await event.reply(msg)

# Gelen mesajlara yanıt
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        global afk_mode, afk_replied_users, afk_reason, filter_dict
        sender_id = event.sender_id

        # AFK mod açık ve bu kullanıcıya daha önce cevap verilmemişse
        if afk_mode and sender_id not in afk_replied_users:
            afk_replied_users.add(sender_id)
            await event.reply(afk_reason)

        # Filtre kontrolü (AFK kapalıysa veya filtre daha öncelikli ise)
        if not afk_mode:
            msg_lower = event.raw_text.lower()
            for key, value in filter_dict.items():
                if key in msg_lower:
                    await event.reply(value)
                    break

    except Exception as e:
        print(f"Mesaj hatası: {e}")

client.start()
print("Bot başlatıldı!")
client.run_until_disconnected()
