import os
import sys
from telethon import TelegramClient
from config import API_ID, API_HASH, session_name

# Session kontrolü
session_file = f"{session_name}.session"

if "--existing-session" in sys.argv:
    if not os.path.exists(session_file):
        print(f"HATA: {session_file} bulunamadı!")
        sys.exit(1)
    print(f"Mevcut oturum kullanılıyor: {session_file}")
else:
    if os.path.exists(session_file):
        print(f"UYARI: {session_file} zaten var, üzerine yazılacak!")

# Client oluşturma
client = TelegramClient(session_name, API_ID, API_HASH)

async def main():
    print("\n✨ JudgeUserBot başarıyla başlatıldı!")
    print(f"🔑 Oturum: {session_name}.session")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nBot kapatıldı")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
