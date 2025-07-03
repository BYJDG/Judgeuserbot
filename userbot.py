from telethon import TelegramClient, events
import asyncio
from config import api_id, api_hash, session_name, global_admin_username, global_admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk = False
afk_reason = ""
filters = {}
afk_users_notified = set()  # AFK modunda hangi kullanıcılara yanıt verildiğini tutar

async def is_bot_owner(event):
    me = await client.get_me()
    sender = await event.get_sender()
    return sender.id == me.id

@client.on(events.NewMessage(pattern=r'^\.alive$'))
async def alive(event):
    if not await is_bot_owner(event):
        return
    me = await client.get_me()
    first_name = me.first_name if me.first_name else "User"
    text = f"Userbotunuz çalışıyor ve sana bişey demek istiyor.. Seni seviyorum {first_name} ❤️\nBot Versiyonu: v1.0"
    try:
        await event.edit(text)
    except:
        await event.reply(text)

@client.on(events.NewMessage(pattern=r'^\.wlive$'))
async def wlive(event):
    sender = await event.get_sender()
    if sender.id == global_admin_id:
        text = (
            f"Bot sahibi tarafından yönetiliyor.\n"
            f"Bot çalışıyor! Sorunsuz.\n"
            f"Bot Versiyonu: v1.0"
        )
        try:
            await event.edit(text)
        except:
            await event.reply(text)
    else:
        await event.reply("Yetkiniz yok.")

@client.on(events.NewMessage(pattern=r'^\.judge$'))
async def judge_help(event):
    if not await is_bot_owner(event):
        return
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalışıp çalışmadığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer, sebebi belirtir.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <mesaj> <cevap> - Filtreli otomatik cevap ekler.\n"
        ".unfilter <mesaj> - Filtreyi kaldırır.\n"
        ".wlive - Owner komutu, sadece sahibi kullanabilir.\n"
        ".judge - Komut listesini gösterir."
    )
    try:
        await event.edit(help_text)
    except:
        await event.reply(help_text)

@client.on(events.NewMessage(pattern=r'^\.afk(?: (.+))?'))
async def set_afk(event):
    if not await is_bot_owner(event):
        return
    global afk, afk_reason, afk_users_notified
    afk = True
    afk_reason = event.pattern_match.group(1) or "Sebep belirtilmedi."
    afk_users_notified.clear()  # Yeni afk modunda bildirim geçmişi temizlenir
    await event.reply(f"AFK moduna geçildi. Sebep: {afk_reason}")

@client.on(events.NewMessage(pattern=r'^\.back$'))
async def back(event):
    if not await is_bot_owner(event):
        return
    global afk, afk_reason, afk_users_notified
    afk = False
    afk_reason = ""
    afk_users_notified.clear()
    await event.reply("AFK modundan çıkıldı.")

@client.on(events.NewMessage(pattern=r'^\.filter (.+?) (.+)'))
async def add_filter(event):
    if not await is_bot_owner(event):
        return
    global filters
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filters[keyword] = response
    await event.reply(f"Filtre eklendi: {keyword} -> {response}")

@client.on(events.NewMessage(pattern=r'^\.unfilter (.+)'))
async def remove_filter(event):
    if not await is_bot_owner(event):
        return
    global filters
    keyword = event.pattern_match.group(1).lower()
    if keyword in filters:
        del filters[keyword]
        await event.reply(f"Filtre kaldırıldı: {keyword}")
    else:
        await event.reply(f"Filtre bulunamadı: {keyword}")

@client.on(events.NewMessage())
async def filter_response(event):
    if not await is_bot_owner(event):
        return
    global filters
    text = event.raw_text.lower()
    if text in filters:
        await event.reply(filters[text])

@client.on(events.NewMessage(incoming=True))
async def afk_notify(event):
    global afk, afk_reason, afk_users_notified
    if not afk:
        return
    me = await client.get_me()
    sender = await event.get_sender()
    # Bot sahibine gelen mesaj, ve mesajı atan bot sahibi değilse
    if sender.id == me.id:
        return
    if sender.id not in afk_users_notified:
        afk_users_notified.add(sender.id)
        await event.reply(f" {afk_reason}")

async def main():
    print("Bot çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
