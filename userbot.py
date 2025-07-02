import os
import asyncio
from telethon import TelegramClient, events

try:
    from config import API_ID, API_HASH, session_name
except ModuleNotFoundError:
    print("HATA: config.py dosyası bulunamadı!")
    print("Lütfen config.py.example dosyasını kopyalayıp config.py olarak düzenleyin")
    exit(1)
except ImportError as e:
    print(f"HATA: Config dosyasında eksik bilgi: {e}")
    exit(1)

# Client oluşturma
client = TelegramClient(session_name, API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.alive'))
async def alive(event):
    await event.edit("✅ **JudgeUserBot Aktif!**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.help'))
async def help(event):
    help_text = """
**🤖 JudgeUserBot Komutları**

`.alive` - Bot durumunu kontrol et
`.help` - Bu yardım mesajını göster
`.reboot` - Botu yeniden başlat
"""
    await event.edit(help_text)

async def main():
    print("\n✨ JudgeUserBot başarıyla başlatıldı!")
    print(f"📌 Oturum dosyası: {session_name}.session")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot kapatıldı")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
