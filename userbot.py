import os
import asyncio
from telethon import TelegramClient, events

# Config import
try:
    from config import API_ID, API_HASH, OWNER_USERNAME, session_name
except ImportError:
    print("Config dosyasını bulamadım veya değişkenler eksik.")
    exit(1)

# Session dosya adı (aynı config'ten)
session_file = f"{session_name}.session"

client = TelegramClient(session_name, API_ID, API_HASH)

# Admin kullanıcı adını küçük harfe çeviriyoruz kontrol için
owner_username = OWNER_USERNAME.lower()

@client.on(events.NewMessage(pattern=r'^\.alive$'))
async def alive_handler(event):
    sender = await event.get_sender()
    sender_username = (sender.username or "").lower()

    # Sadece botun giriş yaptığı hesap komut verebilir
    if sender.id != (await client.get_me()).id:
        return  # Başka kullanıcıların komutları yoksayılır

    await event.respond("Bot aktif ve çalışıyor!")

@client.on(events.NewMessage(pattern=r'^\.id$'))
async def id_handler(event):
    # Mesaj yanıtlanan kişiyi veya mesajı atanı bul
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg:
            user_id = reply_msg.sender_id
            await event.respond(f"ID: {user_id}")
            return

    # Eğer cevap yoksa, komutu atan kişinin ID'sini ver
    await event.respond(f"ID: {event.sender_id}")

@client.on(events.NewMessage(pattern=r'^\.wlive$'))
async def wlive_handler(event):
    sender = await event.get_sender()
    sender_username = (sender.username or "").lower()

    # Sadece admin kullanabilir
    if sender_username != owner_username:
        await event.respond("❌ Yetkiniz yok!")
        return

    await event.respond("Admin .wlive komutunu kullandı, bot aktif!")

async def main():
    print("Bot başlatılıyor...")
    await client.start()
    print("Bot aktif!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot kapatıldı.")
