import json
import os
from telethon import TelegramClient, events

# config.json'u yükle
if not os.path.exists("config.json"):
    print("❌ config.json bulunamadı!")
    exit()

with open("config.json", "r") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]

session_name = "session"
client = TelegramClient(session_name, api_id, api_hash)

owner_id = None  # Botu başlatan kullanıcı
admin_username = "byjudgee"  # Sadece bu kullanıcı .wlive komutunu kullanabilir
afk_mode = False
afk_reason = ""
filtered_messages = {}
afk_users = set()

@client.on(events.NewMessage)
async def handler(event):
    global afk_mode, afk_reason, afk_users

    # Giriş yapan kullanıcıyı owner olarak ata
    global owner_id
    if owner_id is None and event.out:
        owner_id = event.sender_id
        print(f"Bot sahibi id ayarlandı: {owner_id}")

    # Komutlar sadece owner tarafından çalıştırılır
    if event.text == ".alive" and event.sender_id == owner_id:
        await event.reply("✅ Bot aktif ve çalışıyor!")
    elif event.text.startswith(".afk") and event.sender_id == owner_id:
        afk_mode = True
        afk_reason = event.text.split(".afk", 1)[1].strip()
        await event.reply("AFK moduna geçildi.")
    elif event.text == ".back" and event.sender_id == owner_id:
        afk_mode = False
        afk_reason = ""
        afk_users.clear()
        await event.reply("AFK modu kapatıldı.")
    elif event.text.startswith(".filter") and event.sender_id == owner_id:
        try:
            _, msg, reply = event.text.split(" ", 2)
            filtered_messages[msg.lower()] = reply
            await event.reply("✅ Filtre eklendi.")
        except:
            await event.reply("❌ Hatalı kullanım. .filter <mesaj> <cevap>")
    elif event.text.startswith(".unfilter") and event.sender_id == owner_id:
        try:
            _, msg = event.text.split(" ", 1)
            filtered_messages.pop(msg.lower(), None)
            await event.reply("✅ Filtre kaldırıldı.")
        except:
            await event.reply("❌ Hatalı kullanım. .unfilter <mesaj>")
    elif event.text == ".id" and event.sender_id == owner_id:
        reply = await event.get_reply_message()
        if reply:
            await event.reply(f"🆔 Kullanıcı ID: {reply.sender_id}")
        else:
            await event.reply("❌ Bir mesaja yanıt vermelisin.")
    elif event.text == ".wlive":
        sender = await event.get_sender()
        if sender.username == admin_username:
            await event.reply("Userbotunuz çalışıyor ve sana bir şey demek istiyor...\n\n❤️ Seni seviyorum ByJudge!\n\nBot Versiyonu: v1.0")
        else:
            await event.reply("❌ Bu komutu kullanmak için yetkiniz yok.")
    else:
        # Filtre kontrolü
        if not event.out and afk_mode and event.sender_id not in afk_users:
            await event.reply(f"Şu anda AFK'yım. Sebep: {afk_reason}")
            afk_users.add(event.sender_id)
        elif not event.out:
            msg_text = event.text.lower()
            if msg_text in filtered_messages:
                await event.reply(filtered_messages[msg_text])

print("Bot başlatılıyor...")
client.start()
print("✅ Bot aktif!")
client.run_until_disconnected()
