from telethon import TelegramClient, events
import json
import os

# Config yükle
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
    api_id = config["api_id"]
    api_hash = config["api_hash"]
else:
    print("config.json bulunamadı!")
    exit()

client = TelegramClient("session", api_id, api_hash)

# --- Özellik Değişkenleri ---
filters = {}           # .filter sistemi
afk_mode = False       # AFK açık mı?
afk_reason = ""        # AFK sebebi
afk_users = set()      # Kime cevap verildi
ADMIN_USERNAME = "byjudgee"  # Sadece bu kişi .wlive çalıştırabilir

# --- .alive komutu ---
@client.on(events.NewMessage(pattern=r"\.alive"))
async def alive_handler(event):
    await event.reply("🤖 Bot çalışıyor!\nBot Versiyonu: v1.0")

# --- .afk <sebep> komutu ---
@client.on(events.NewMessage(pattern=r"\.afk (.+)"))
async def afk_on(event):
    global afk_mode, afk_reason, afk_users
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    afk_users.clear()
    await event.reply(f"AFK moduna geçildi. Sebep: {afk_reason}")

# --- .back komutu ---
@client.on(events.NewMessage(pattern=r"\.back"))
async def afk_off(event):
    global afk_mode
    afk_mode = False
    await event.reply("AFK modu kapatıldı. Hoş geldin!")

# --- .filter <mesaj> <cevap> komutu ---
@client.on(events.NewMessage(pattern=r"\.filter (.+?) (.+)"))
async def add_filter(event):
    keyword = event.pattern_match.group(1).lower()
    reply = event.pattern_match.group(2)
    filters[keyword] = reply
    await event.reply(f"'{keyword}' kelimesine cevap kaydedildi.")

# --- .unfilter <mesaj> komutu ---
@client.on(events.NewMessage(pattern=r"\.unfilter (.+)"))
async def remove_filter(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filters:
        del filters[keyword]
        await event.reply(f"'{keyword}' filtresi silindi.")
    else:
        await event.reply("Bu kelime için filtre bulunamadı.")

# --- Mesajlara filtre ve AFK cevabı verme ---
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    global afk_users
    if event.is_private and not event.out:
        text = event.raw_text.lower()

        if afk_mode and event.sender_id not in afk_users:
            afk_users.add(event.sender_id)
            await event.reply(f"{afk_reason}")

        # AFK açıkken filtre çalışmasın
        if not afk_mode:
            for keyword, reply in filters.items():
                if keyword in text:
                    await event.reply(reply)
                    break

# --- .wlive komutu (sadece admin kullanabilir) ---
@client.on(events.NewMessage(pattern=r"\.wlive"))
async def wlive_handler(event):
    try:
        sender = await event.get_sender()
        username = sender.username

        if username and username.lower() == ADMIN_USERNAME.lower():
            await event.reply(
                "Userbotunuz çalışıyor ve sana bişey demek istiyor..\n"
                "Seni seviyorum ByJudge ❤️\n"
                "Bot Versiyonu: v1.0"
            )
    except Exception as e:
        await event.reply(f"Hata oluştu: {e}")

# --- Bot başlat ---
print("Bot başlatılıyor...")
client.start()
print("Bot çalışıyor!")
client.run_until_disconnected()
