import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

# Global değişkenler
afk_mode = False
afk_reason = ""
afk_replied_users = set()
filtered_messages = {}
all_filtered_messages = {}
custom_commands = {}
welcome_message = None
welcome_enabled = False

# Özel komutları yükle
if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r") as f:
        custom_commands = json.load(f)

if os.path.exists("welcome.json"):
    with open("welcome.json", "r") as f:
        data = json.load(f)
        welcome_message = data.get("message")
        welcome_enabled = data.get("enabled", False)

# .alive
@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

# .wlive (sadece admin)
@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

# .judge
@client.on(events.NewMessage(pattern=r"^.judge$"))
async def judge_help(event):
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalıştığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <kelime> <cevap> - PM'de otomatik yanıt ekler.\n"
        ".unfilter <kelime> - PM'deki filtreyi kaldırır.\n"
        ".allfilter <kelime> <cevap> - Tüm sohbetler için filtre ekler.\n"
        ".unallfilter <kelime> - Genel filtreyi kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar.\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar.\n"
        ".eval <kod> - Yalnızca admin çalıştırabilir.\n"
        ".welcome <mesaj> - Karşılama mesajı ayarla.\n"
        ".unwelcome - Karşılama mesajını kapatır.\n"
        ".wlive - Global admin için sistem durumu."
    )
    await event.reply(help_text)

# .afk
@client.on(events.NewMessage(pattern=r"^.afk (.+)"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    afk_replied_users = set()
    await event.edit(afk_reason)

# .back
@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = False
    afk_reason = ""
    afk_replied_users = set()
    await event.edit("Tekrar aktif oldum!")

# AFK reply
@client.on(events.NewMessage())
async def afk_auto_reply(event):
    if afk_mode and event.sender_id != (await client.get_me()).id:
        if event.is_private or (event.is_group and (event.mentioned or event.is_reply)):
            if event.sender_id not in afk_replied_users:
                await event.reply(afk_reason)
                afk_replied_users.add(event.sender_id)

# .filter (sadece PM)
@client.on(events.NewMessage(pattern=r"^.filter (\S+) ([\s\S]+)"))
async def filter_handler(event):
    if event.is_private and event.sender_id == (await client.get_me()).id:
        keyword = event.pattern_match.group(1).lower()
        response = event.pattern_match.group(2)
        filtered_messages[keyword] = response
        await event.reply(f"Filtre eklendi: {keyword} → {response}")

# .unfilter
@client.on(events.NewMessage(pattern=r"^.unfilter (.+)"))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        await event.reply(f"Filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait bir filtre bulunamadı.")

# PM filter cevap
@client.on(events.NewMessage())
async def filter_response(event):
    if event.is_private and event.sender_id != (await client.get_me()).id:
        for keyword, response in filtered_messages.items():
            if keyword.lower() in event.raw_text.lower():
                await event.reply(response)
                break

# .allfilter
@client.on(events.NewMessage(pattern=r"^.allfilter (\S+) ([\s\S]+)"))
async def allfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    all_filtered_messages[keyword] = response
    await event.reply(f"Genel filtre eklendi: {keyword} → {response}")

# .unallfilter
@client.on(events.NewMessage(pattern=r"^.unallfilter (.+)"))
async def unallfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        await event.reply(f"Genel filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait genel filtre bulunamadı.")

# Genel filter cevap
@client.on(events.NewMessage())
async def all_filter_response(event):
    for keyword, response in all_filtered_messages.items():
        if keyword.lower() in event.raw_text.lower():
            await event.reply(response)
            break

# .ekle
@client.on(events.NewMessage(pattern=r"^.ekle (\S+) ([\s\S]+)"))
async def add_command(event):
    if event.sender_id != (await client.get_me()).id:
        return
    cmd = event.pattern_match.group(1)
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w") as f:
        json.dump(custom_commands, f)
    await event.reply(f"Komut eklendi: {cmd} → {reply}")

# .sil
@client.on(events.NewMessage(pattern=r"^.sil (\S+)"))
async def del_command(event):
    if event.sender_id != (await client.get_me()).id:
        return
    cmd = event.pattern_match.group(1)
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w") as f:
            json.dump(custom_commands, f)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

# Özel komutları yürüt
@client.on(events.NewMessage())
async def custom_command_handler(event):
    if event.raw_text.strip() in custom_commands:
        await event.reply(custom_commands[event.raw_text.strip()])

# .restart
@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# .kick
@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    if event.is_group:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Kicklemek için kullanıcı belirt.")
        await event.chat.kick_participant(user.id)
        await event.reply(f"{user.first_name} gruptan atıldı.")

# .ban
@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    if event.is_group:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Banlamak için kullanıcı belirt.")
        rights = ChatBannedRights(until_date=None, view_messages=True)
        await client(EditBannedRequest(event.chat_id, user.id, rights))
        await event.reply(f"{user.first_name} gruptan banlandı.")

# .eval
@client.on(events.NewMessage(pattern=r"^.eval (.+)"))
async def eval_handler(event):
    if event.sender_id != admin_id:
        return
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        await event.reply(str(result))
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")

# .welcome
@client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?"))
async def welcome_handler(event):
    global welcome_message, welcome_enabled
    if event.pattern_match.group(1):
        welcome_message = event.pattern_match.group(1)
        with open("welcome.json", "w") as f:
            json.dump({"message": welcome_message, "enabled": True}, f)
        welcome_enabled = True
        await event.reply("Karşılama mesajı ayarlandı ve aktif edildi.")
    elif welcome_message:
        welcome_enabled = True
        with open("welcome.json", "w") as f:
            json.dump({"message": welcome_message, "enabled": True}, f)
        await event.reply("Karşılama mesajı tekrar aktif edildi.")
    else:
        await event.reply("İlk önce bir karşılama mesajı belirlemelisin.\nÖrn: .welcome Hoş geldin!")

# .unwelcome
@client.on(events.NewMessage(pattern=r"^.unwelcome$"))
async def unwelcome_handler(event):
    global welcome_enabled
    welcome_enabled = False
    with open("welcome.json", "w") as f:
        json.dump({"message": welcome_message, "enabled": False}, f)
    await event.reply("Karşılama mesajı devre dışı bırakıldı.")

# Karşılama mesajı otomatik
@client.on(events.NewMessage())
async def welcome_auto(event):
    if welcome_enabled and event.is_private and event.sender_id != (await client.get_me()).id:
        if not os.path.exists("welcomed_users.json"):
            with open("welcomed_users.json", "w") as f:
                json.dump([], f)
        with open("welcomed_users.json", "r") as f:
            welcomed = json.load(f)
        if event.sender_id not in welcomed:
            await event.reply(welcome_message)
            welcomed.append(event.sender_id)
            with open("welcomed_users.json", "w") as f:
                json.dump(welcomed, f)

# Başlat
async def main():
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
    
