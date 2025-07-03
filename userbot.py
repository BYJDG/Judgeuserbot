import asyncio
import json
import os
from telethon import TelegramClient, events

# CONFIG BÖLÜMÜ (install.sh ile config.py'den çekildiği varsayılır)
from config import api_id, api_hash, session_name, admin_username, admin_id  # config.py içinde tanımlı

COMMANDS_FILE = "custom_commands.json"

def load_commands():
    if not os.path.isfile(COMMANDS_FILE):
        return {}
    with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_commands(commands):
    with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(commands, f, ensure_ascii=False, indent=2)

client = TelegramClient(session_name, api_id, api_hash)

afk_status = {
    "active": False,
    "reason": None,
    "users_notified": set()
}

@client.on(events.NewMessage(pattern=r"^\.alive$"))
async def alive(event):
    me = await client.get_me()
    first_name = me.first_name
    # Mesajı düzenleyerek yanıt ver
    await event.delete()
    await event.respond(f"Userbotunuz çalışıyor ve sana bişey demek istiyor.. Seni seviyorum {first_name} ❤️\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"^\.afk(?:\s+(.*))?$"))
async def afk(event):
    user_id = (await client.get_me()).id
    if event.sender_id != user_id:
        return

    reason = event.pattern_match.group(1) or "Sebep belirtilmedi."
    afk_status["active"] = True
    afk_status["reason"] = reason
    afk_status["users_notified"].clear()

    await event.edit(f"AFK moduna geçildi. Sebep: {reason}")

@client.on(events.NewMessage(pattern=r"^\.back$"))
async def back(event):
    user_id = (await client.get_me()).id
    if event.sender_id != user_id:
        return

    afk_status["active"] = False
    afk_status["reason"] = None
    afk_status["users_notified"].clear()

    await event.edit("AFK modundan çıkıldı. Artık müsaitsin.")

@client.on(events.NewMessage(incoming=True))
async def afk_reply(event):
    me = await client.get_me()
    user_id = me.id

    if not afk_status["active"]:
        return

    # Sadece farklı kişilerden gelen mesajlara cevap ver
    if event.sender_id == user_id:
        return

    # Sadece kişisel veya grup içinde benden bahsedilirse cevap ver
    if event.is_private or (me.username and me.username in event.raw_text):
        if event.sender_id not in afk_status["users_notified"]:
            afk_status["users_notified"].add(event.sender_id)
            await event.reply(f"Ben şu an AFK modundayım. Sebep: {afk_status['reason']}")
        # Eğer zaten cevap verdiysek tekrar mesaj atma

# .wlive komutu sadece admin_id için
@client.on(events.NewMessage(pattern=r"^\.wlive$"))
async def wlive(event):
    if event.sender_id != admin_id:
        await event.reply("Yetkiniz yok.")
        return

    await event.reply("Bot çalışıyor, sorun yok.\nBot Versiyonu: v1.0")

# .judge komutu komut listesini verir
@client.on(events.NewMessage(pattern=r"^\.judge$"))
async def judge(event):
    user_id = (await client.get_me()).id
    if event.sender_id != user_id:
        return

    komutlar = """
Judge Userbot Komutları v1.0:

.alive - Botun çalışıp çalışmadığını kontrol eder.
.afk <sebep> - AFK moduna geçer, sebebi belirtir.
.back - AFK modundan çıkar.
.filter <mesaj> <cevap> - Filtreli otomatik cevap ekler.
.unfilter <mesaj> - Filtreyi kaldırır.
.judge - Komut listesini gösterir.
.ekle <.komut> <cevap> - Kişisel özel komut ekler.
"""

    await event.edit(komutlar.strip())

# Özel komutlar için dosya
def load_commands():
    if not os.path.isfile(COMMANDS_FILE):
        return {}
    with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_commands(commands):
    with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(commands, f, ensure_ascii=False, indent=2)

# .ekle komutu: Kişisel özel komut ekle
@client.on(events.NewMessage(pattern=r"^\.ekle\s+(\.\S+)\s+(.+)$"))
async def add_command(event):
    user_id = (await client.get_me()).id
    if event.sender_id != user_id:
        await event.reply("Bu komutu sadece bot sahibi kullanabilir.")
        return

    cmd = event.pattern_match.group(1)
    answer = event.pattern_match.group(2)

    commands = load_commands()
    commands[cmd] = answer
    save_commands(commands)

    await event.reply(f"'{cmd}' komutu başarıyla eklendi!")

# Özel komutları yakalayıp yanıtlayan handler
@client.on(events.NewMessage(pattern=r"^\.\S+"))
async def custom_command_handler(event):
    user_id = (await client.get_me()).id
    if event.sender_id != user_id:
        return

    commands = load_commands()
    text = event.raw_text.split()[0]

    if text in commands:
        await event.edit(commands[text])

async def main():
    await client.start()
    print("Bot aktif!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
