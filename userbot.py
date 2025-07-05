import asyncio
import os
import json
import re
from telethon import TelegramClient, events
from telethon.tl.functions.messages import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

# Genel değişkenler
afk_mode = False
afk_reason = ""
afk_replied_users = set()
filtered_messages = {}
all_filtered_messages = {}
custom_commands = {}
welcome_message = None
welcome_active = False
my_id = None  # Botun kendi ID'si (sahibi)

# JSON verileri yükleme
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

filtered_messages = load_json("filtered_messages.json")
all_filtered_messages = load_json("all_filtered_messages.json")
custom_commands = load_json("custom_commands.json")

def is_owner(event):
    return event.sender_id == admin_id

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if not is_owner(event):
        return
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

@client.on(events.NewMessage(pattern=r"^.judge$"))
async def judge_help(event):
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalıştığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <kelime> <cevap> - Sadece özelde otomatik yanıt ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".allfilter <kelime> <cevap> - Her yerde geçerli filtre.\n"
        ".unallfilter <kelime> - Her yer filtresini kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".welcome [mesaj] - Karşılama mesajını ayarlar/aktifleştirir.\n"
        ".unwelcome - Karşılama mesajını devre dışı bırakır.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id/reply> - Kullanıcıyı atar.\n"
        ".ban <id/reply> - Kullanıcıyı banlar.\n"
        ".eval <kod> - Yalnızca admin çalıştırabilir.\n"
        ".wlive - Global admin için sistem durumu."
    )
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^.afk (.+)"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    afk_replied_users.clear()
    await event.edit(afk_reason)

@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = False
    afk_reason = ""
    afk_replied_users.clear()
    await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason, afk_replied_users
    if afk_mode and (event.is_private or (event.mentioned or event.is_reply)):
        if event.sender_id not in afk_replied_users:
            await event.reply(afk_reason)
            afk_replied_users.add(event.sender_id)

@client.on(events.NewMessage(pattern=r"^.filter (\S+) (.+)"))
async def filter_handler(event):
    if not event.is_private or event.sender_id != my_id:
        return
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filtered_messages[keyword] = response
    save_json("filtered_messages.json", filtered_messages)
    await event.reply(f"Özel mesaj filtresi eklendi: {keyword}")

@client.on(events.NewMessage(pattern=r"^.unfilter (\S+)"))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        save_json("filtered_messages.json", filtered_messages)
        await event.reply(f"Filtre kaldırıldı: {keyword}")

@client.on(events.NewMessage(pattern=r"^.allfilter (\S+) (.+)"))
async def allfilter_handler(event):
    if event.sender_id != my_id:
        return
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    all_filtered_messages[keyword] = response
    save_json("all_filtered_messages.json", all_filtered_messages)
    await event.reply(f"Genel filtre eklendi: {keyword}")

@client.on(events.NewMessage(pattern=r"^.unallfilter (\S+)"))
async def unallfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        save_json("all_filtered_messages.json", all_filtered_messages)
        await event.reply(f"Genel filtre kaldırıldı: {keyword}")

@client.on(events.NewMessage())
async def filter_response(event):
    if event.sender_id == my_id:
        return
    text = event.raw_text.lower()
    if event.is_private:
        for keyword, response in filtered_messages.items():
            if keyword in text:
                return await event.reply(response)
    for keyword, response in all_filtered_messages.items():
        if keyword in text:
            return await event.reply(response)

@client.on(events.NewMessage(pattern=r"^.ekle (\S+) (.+)", func=lambda e: e.sender_id == my_id))
async def add_command(event):
    cmd = event.pattern_match.group(1).strip()
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    save_json("custom_commands.json", custom_commands)
    await event.reply(f"Komut eklendi: {cmd}")

@client.on(events.NewMessage(pattern=r"^.sil (\S+)", func=lambda e: e.sender_id == my_id))
async def del_command(event):
    cmd = event.pattern_match.group(1).strip()
    if cmd in custom_commands:
        del custom_commands[cmd]
        save_json("custom_commands.json", custom_commands)
        await event.reply(f"Komut silindi: {cmd}")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    if event.raw_text.strip() in custom_commands:
        await event.reply(custom_commands[event.raw_text.strip()])

@client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?"))
async def welcome_set(event):
    global welcome_message, welcome_active
    if event.sender_id != my_id:
        return
    msg = event.pattern_match.group(1)
    if msg:
        welcome_message = msg
    welcome_active = True
    await event.reply("Karşılama mesajı aktif.")

@client.on(events.NewMessage(pattern=r"^.unwelcome"))
async def unwelcome(event):
    global welcome_active
    if event.sender_id != my_id:
        return
    welcome_active = False
    await event.reply("Karşılama mesajı devre dışı bırakıldı.")

@client.on(events.NewMessage())
async def welcome_handler(event):
    if welcome_active and event.is_private and event.sender_id != my_id:
        if not hasattr(event.client, "welcomed"):
            event.client.welcomed = set()
        if event.sender_id not in event.client.welcomed:
            await event.reply(welcome_message)
            event.client.welcomed.add(event.sender_id)

@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execl(sys.executable, sys.executable, *sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    if not event.is_group:
        return
    user = await event.get_reply_message().get_sender() if event.is_reply else None
    if not user:
        return await event.reply("Kicklemek için kullanıcı belirt.")
    await event.client.kick_participant(event.chat_id, user.id)
    await event.reply(f"{user.first_name} gruptan atıldı.")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    if not event.is_group:
        return
    user = await event.get_reply_message().get_sender() if event.is_reply else None
    if not user:
        return await event.reply("Banlamak için kullanıcı belirt.")
    rights = ChatBannedRights(until_date=None, view_messages=True)
    await event.client(EditBannedRequest(event.chat_id, user.id, rights))
    await event.reply(f"{user.first_name} gruptan banlandı.")

@client.on(events.NewMessage(pattern=r"^.eval (.+)"))
async def eval_handler(event):
    if not is_owner(event):
        return
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        await event.reply(str(result))
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")

async def main():
    global my_id
    await client.start()
    me = await client.get_me()
    my_id = me.id
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
