from telethon import TelegramClient, events
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

# Config'den import ediyoruz, kendi config.py dosyana göre düzenle
from config import api_id, api_hash, session_name, global_admin_id, global_admin_username

client = TelegramClient(session_name, api_id, api_hash)

afk = False
afk_reason = ""
afk_users_notified = set()

@client.on(events.NewMessage(pattern=r"\.alive"))
async def alive_handler(event):
    me = await client.get_me()
    first_name = me.first_name
    # Mesajı düzenleyerek cevap verelim
    await event.edit(f"Userbotunuz çalışıyor ve sana bişey demek istiyor.. Seni seviyorum {first_name} ❤️\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"\.afk(?: (.+))?"))
async def afk_on(event):
    global afk, afk_reason, afk_users_notified
    if afk:
        await event.respond("Zaten AFK modundasın.")
        return
    reason = event.pattern_match.group(1)
    afk = True
    afk_reason = reason if reason else "Sebep belirtilmedi."
    afk_users_notified = set()
    await event.respond(f"AFK moduna geçtin.\nSebep: {afk_reason}")

@client.on(events.NewMessage(pattern=r"\.back"))
async def afk_off(event):
    global afk, afk_reason, afk_users_notified
    if not afk:
        await event.respond("Zaten AFK değilsin.")
        return
    afk = False
    afk_reason = ""
    afk_users_notified = set()
    await event.respond("AFK modundan çıktın, artık mesajlarına cevap verebilirim.")

@client.on(events.NewMessage(pattern=r"\.wlive"))
async def wlive_handler(event):
    sender = await event.get_sender()
    if sender.id != global_admin_id:
        await event.respond("Yetkiniz yok.")
        return
    await event.respond("Bot çalışıyor sorunsuz! 🌟\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"\.judge"))
async def judge_help(event):
    me = await client.get_me()
    sender = await event.get_sender()
    if sender.id != me.id and sender.id != global_admin_id:
        await event.respond("Bu komutu kullanma yetkiniz yok.")
        return
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalışıp çalışmadığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer, sebebi belirtir.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <mesaj> <cevap> - Filtreli otomatik cevap ekler.\n"
        ".unfilter <mesaj> - Filtreyi kaldırır.\n"
        ".wlive - Owner komutu, sadece sahibi kullanabilir.\n"
    )
    await event.respond(help_text)

# AFK Modundayken, sadece özel mesaj ve gruplarda mention olanlara cevap verelim
@client.on(events.NewMessage(incoming=True))
async def afk_notify(event):
    global afk, afk_reason, afk_users_notified

    if not afk:
        return

    me = await client.get_me()
    sender = await event.get_sender()
    if sender.id == me.id:
        # Kendi mesajına yanıt verme
        return

    if event.is_private:
        if sender.id not in afk_users_notified:
            afk_users_notified.add(sender.id)
            await event.reply(f" {afk_reason}")
        return

    # Grup veya kanalsa ve mesajda beni mention'ladıysa
    if event.is_group or event.is_channel:
        if me.id in event.message.mentioned:
            if sender.id not in afk_users_notified:
                afk_users_notified.add(sender.id)
                await event.reply(f"Şu anda AFK modundayım.\nSebep: {afk_reason}")
        return

# Burada filter ve unfilter komutları varsa onları ekleyebilirsin
# ... (varsa kodlarını ekle)

async def main():
    await client.start()
    print("Bot aktif!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
