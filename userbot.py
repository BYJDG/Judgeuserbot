from telethon import TelegramClient, events
import os

# Config kısmı - bunları install.sh ile config.py'ye yazdırıyorsun zaten
from config import api_id, api_hash, session_name

client = TelegramClient(session_name, api_id, api_hash)

# Global admin (byjudgee) Telegram ID'si
GLOBAL_ADMIN_ID = 1486645014

@client.on(events.NewMessage(pattern=r"\.alive"))
async def alive_handler(event):
    # Sadece botun giriş yaptığı hesap kullanabilir
    if event.sender_id == (await client.get_me()).id:
        me = await client.get_me()
        name = me.first_name or "User"
        await event.edit(
            f"Userbotunuz çalışıyor ve sana bişey demek istiyor..\n"
            f"Seni seviyorum {name} ❤️\n\n"
            "Bot Versiyonu: v1.0"
        )
    else:
        # Başka biri yazarsa cevap verme (opsiyonel: silebilirsin)
        pass

@client.on(events.NewMessage(pattern=r"\.wlive"))
async def wlive_handler(event):
    # Sadece global admin kullanabilir
    if event.sender_id == GLOBAL_ADMIN_ID:
        try:
            await event.edit(
                "🚀 JudgeUserBot aktif ve sorunsuz çalışıyor!\n"
                "🌟 Geliştirici: ByJudge\n"
                "✨ Bot Versiyonu: v1.0\n"
                "🔥 Her zaman yanınızdayım!"
            )
        except Exception as e:
            print(f".wlive komutunda hata: {e}")
    else:
        await event.respond("❌ Yetkiniz yok!")

# Buraya diğer komutlarınızı ekleyebilirsiniz...

print("Bot başlatılıyor...")
client.start()
print("Bot aktif!")
client.run_until_disconnected()
