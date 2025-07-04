import asyncio
import os
import json
from telethon import TelegramClient, events
from config import api_id, api_hash, session_name, admin_username, admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
custom_commands_file = "custom_commands.json"
filters_file = "filters.json"

# JSON yükleme
def load_json_file(file_path):
    return json.load(open(file_path)) if os.path.exists(file_path) else {}

custom_commands = load_json_file(custom_commands_file)
filters = load_json_file(filters_file)

@client.on(events.NewMessage(pattern=r"^\.alive$"))
async def alive_handler(event):
    if event.sender_id != (await client.get_me()).id:
        return
    name = (await client.get_me()).first_name
    await event.edit(f"Userbotunuz çalışıyor ve sana bir şey demek istiyor...\n**Seni seviyorum {name} ❤️**\n\nBot Versiyonu: `v1.0`")

@client.on(events.NewMessage(pattern=r"^\.wlive$"))
async def wlive_handler(event):
    sender = await event.get_sender()
    if sender.id == int(admin_id):
        await event.reply("🛰️ Bot çevrimiçi.\n✨ Versiyon: `v1.0`\n🚀 Tüm sistemler çalışıyor.")
    else:
        await event.reply("⛔ Bu komutu kullanma yetkiniz yok.")

@client.on(events.NewMessage(pattern=r"^\.judge$"))
async def judge_handler(event):
    if event.sender_id != (await client.get_me()).id:
        return
    await event.reply("""🧠 Judge Userbot Komutları v1.0:

.alive - Botun çalışıp çalışmadığını kontrol eder.
.afk <sebep> - AFK moduna geçer, sebebi belirtir.
.back - AFK modundan çıkar.
.filter <mesaj> <cevap> - Filtreli otomatik cevap ekler.
.unfilter <mesaj> - Filtreyi kaldırır.
.ekle <.komut> <cevap> - Özel komut tanımlar.
.wlive - Owner komutu, sadece @byjudgee kullanabilir.""")

@client.on(events.NewMessage(pattern=r"^\.afk (.+)$"))
async def afk_handler(event):
    global afk_mode, afk_reason
    if event.sender_id != (await client.get_me()).id:
        return
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    await event.edit(f"AFK moduna geçildi: {afk_reason}")

@client.on(events.NewMessage(pattern=r"^\.back$"))
async def back_handler(event):
    global afk_mode, afk_reason
    if event.sender_id != (await client.get_me()).id:
        return
    afk_mode = False
    afk_reason = ""
    await event.edit("AFK modundan çıkıldı.")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason
    if afk_mode:
        me = await client.get_me()
        if (event.is_private and event.sender_id != me.id) or (me.id in getattr(event.message, 'message', '')):
            await event.reply(afk_reason)
            afk_mode = False  # sadece bir kez atsın

@client.on(events.NewMessage(pattern=r"^\.filter (.+?) (.+)$"))
async def add_filter(event):
    if event.sender_id != (await client.get_me()).id:
        return
    trigger, response = event.pattern_match.group(1), event.pattern_match.group(2)
    filters[trigger] = response
    json.dump(filters, open(filters_file, "w"))
    await event.reply(f"🔎 `{trigger}` kelimesine karşılık yanıt eklendi.")

@client.on(events.NewMessage(pattern=r"^\.unfilter (.+)$"))
async def remove_filter(event):
    if event.sender_id != (await client.get_me()).id:
        return
    trigger = event.pattern_match.group(1)
    if trigger in filters:
        del filters[trigger]
        json.dump(filters, open(filters_file, "w"))
        await event.reply(f"❌ `{trigger}` filtresi kaldırıldı.")
    else:
        await event.reply("⚠️ Bu filtre bulunamadı.")

@client.on(events.NewMessage())
async def filter_responder(event):
    if event.sender_id == (await client.get_me()).id:
        return
    for trigger, response in filters.items():
        if trigger in event.raw_text:
            await event.reply(response)
            break

@client.on(events.NewMessage(pattern=r"^\.ekle\s+(\.\w+)\s+(.+)$"))
async def add_custom_command(event):
    if event.sender_id != (await client.get_me()).id:
        return
    cmd, response = event.pattern_match.group(1), event.pattern_match.group(2)
    custom_commands[cmd] = response
    json.dump(custom_commands, open(custom_commands_file, "w"))
    await event.reply(f"✅ `{cmd}` komutu tanımlandı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    if event.raw_text in custom_commands and event.sender_id == (await client.get_me()).id:
        await event.reply(custom_commands[event.raw_text])

async def main():
    await client.start()
    print("JudgeUserBot çalışıyor!")
    await client.run_until_disconnected()

asyncio.run(main())
