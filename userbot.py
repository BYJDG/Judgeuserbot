import os
import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH, session_name

# Oturum kontrolü
if not API_ID or not API_HASH:
    print("HATA: config.py dosyasında API_ID veya API_HASH eksik!")
    print("Lütfen https://my.telegram.org adresinden API bilgilerinizi alın")
    exit(1)

client = TelegramClient(session_name, API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.alive'))
async def alive(event):
    await event.edit("`👽 JudgeUserBot Aktif!`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.help'))
async def help(event):
    await event.edit("`🧠 Kullanılabilir Komutlar:`\n"
                     "`.alive` - Bot durumunu kontrol et\n"
                     "`.help` - Yardım menüsünü göster\n"
                     "`.reboot` - Botu yeniden başlat")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.reboot'))
async def reboot(event):
    await event.edit("`♻️ Bot yeniden başlatılıyor...`")
    os.system("python userbot.py")

async def main():
    print("\n\033[1;36mJudgeUserBot başarıyla başlatıldı!\033[0m")
    print("\033[1;33mKullanılabilir komutlar: .alive, .help, .reboot\033[0m")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
