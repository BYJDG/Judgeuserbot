import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon.errors.rpcerrorlist import UserAdminInvalidError
from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
afk_replied_users = set()
filtered_messages = {}
all_filtered_messages = {}
custom_commands = {}
welcome_message = None
welcomed_users = set()

# Load custom commands if available
if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r") as f:
        custom_commands = json.load(f)

# Load filtered messages (private)
if os.path.exists("filtered_messages.json"):
    with open("filtered_messages.json", "r") as f:
        filtered_messages = json.load(f)

# Load all filtered messages (global)
if os.path.exists("all_filtered_messages.json"):
    with open("all_filtered_messages.json", "r") as f:
        all_filtered_messages = json.load(f)

# Load welcome message
if os.path.exists("welcome.json"):
    with open("welcome.json", "r") as f:
        data = json.load(f)
        welcome_message = data.get("message", None)
        welcomed_users = set(data.get("welcomed_users", []))

# Get own user ID (for filtering commands)
me = None
me_id = None

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

@client.on(events.NewMessage(pattern=r"^.judge$"))
async def judge_help(event):
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalıştığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <kelime> <cevap> - Özel mesajlarda otomatik yanıt ekler.\n"
        ".allfilter <kelime> <cevap> - Her yerde otomatik yanıt ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".unallfilter <kelime> - Genel filtreyi kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".welcome [mesaj] - Karşılama mesajını ayarlar/aktif eder.\n"
        ".unwelcome - Karşılama mesajını kapatır.\n"
        ".back - AFK modundan çıkar.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar.\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar.\n"
        ".eval <kod> - Yalnızca admin çalıştırabilir.\n"
        ".wlive - Global admin için sistem durumu."
    )
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = True
    afk_replied_users.clear()
    reason = event.pattern_match.group(1)
    afk_reason = reason if reason else "AFK modundayım."
    await event.edit(f"AFK moduna geçildi, sebep: {afk_reason}")

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
    if not afk_mode:
        return
    if event.is_private or event.is_group:
        if event.sender_id == me_id:
            return
        if event.is_private:
            if event.sender_id not in afk_replied_users:
                await event.reply(afk_reason)
                afk_replied_users.add(event.sender_id)
        else:  # Grup ise, sadece mention veya reply ise cevap ver
            if event.is_reply or (event.message and me_id in [user.id for user in event.message.entities if hasattr(user, 'user_id')]):
                if event.sender_id not in afk_replied_users:
                    await event.reply(afk_reason)
                    afk_replied_users.add(event.sender_id)

@client.on(events.NewMessage(pattern=r"^.filter (\S+) (.+)", func=lambda e: e.is_private and e.sender_id == me_id))
async def filter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filtered_messages[keyword] = response
    with open("filtered_messages.json", "w") as f:
        json.dump(filtered_messages, f)
    await event.reply(f"Özel mesaj filtresi eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.unfilter (\S+)", func=lambda e: e.is_private and e.sender_id == me_id))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        with open("filtered_messages.json", "w") as f:
            json.dump(filtered_messages, f)
        await event.reply(f"Özel mesaj filtresi kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait bir filtre bulunamadı.")

@client.on(events.NewMessage(pattern=r"^.allfilter (\S+) (.+)", func=lambda e: e.sender_id == me_id))
async def allfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    all_filtered_messages[keyword] = response
    with open("all_filtered_messages.json", "w") as f:
        json.dump(all_filtered_messages, f)
    await event.reply(f"Genel filtre eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.unallfilter (\S+)", func=lambda e: e.sender_id == me_id))
async def unallfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        with open("all_filtered_messages.json", "w") as f:
            json.dump(all_filtered_messages, f)
        await event.reply(f"Genel filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait genel filtre bulunamadı.")

@client.on(events.NewMessage())
async def filter_response(event):
    text = event.raw_text.lower()
    if event.is_private:
        for keyword, response in filtered_messages.items():
            if keyword in text:
                await event.reply(response)
                return
    else:
        for keyword, response in all_filtered_messages.items():
            if keyword in text:
                await event.reply(response)
                return

@client.on(events.NewMessage(pattern=r"^.ekle (\S+) (.+)", func=lambda e: e.sender_id == me_id))
async def add_command(event):
    cmd = event.pattern_match.group(1)
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w") as f:
        json.dump(custom_commands, f)
    await event.reply(f"Komut eklendi: {cmd} → {reply}")

@client.on(events.NewMessage(pattern=r"^.sil (\S+)", func=lambda e: e.sender_id == me_id))
async def del_command(event):
    cmd = event.pattern_match.group(1)
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w") as f:
            json.dump(custom_commands, f)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    cmd = event.raw_text.strip()
    if cmd in custom_commands:
        reply = custom_commands[cmd]
        # Eğer mesaj kod olarak gönderilecekse, aşağıdaki gibi düzenleyebilirsin:
        # await event.reply(f"```\n{reply}\n```")
        await event.reply(reply)

@client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?", func=lambda e: e.sender_id == me_id))
async def welcome_handler(event):
    global welcome_message, welcomed_users
    msg = event.pattern_match.group(1)
    if msg:
        welcome_message = msg
        welcomed_users = set()
        with open("welcome.json", "w") as f:
            json.dump({"message": welcome_message, "welcomed_users": list(welcomed_users)}, f)
        await event.reply(f"Karşılama mesajı ayarlandı:\n{welcome_message}")
    else:
        if welcome_message:
            await event.reply(f"Mevcut karşılama mesajı:\n{welcome_message}")
        else:
            await event.reply("Henüz bir karşılama mesajı ayarlanmadı.")

@client.on(events.NewMessage(pattern=r"^.unwelcome$", func=lambda e: e.sender_id == me_id))
async def unwelcome_handler(event):
    global welcome_message, welcomed_users
    welcome_message = None
    welcomed_users = set()
    if os.path.exists("welcome.json"):
        os.remove("welcome.json")
    await event.reply("Karşılama mesajı kapatıldı.")

@client.on(events.NewMessage())
async def welcome_response(event):
    global welcome_message, welcomed_users
    if welcome_message is None:
        return
    if not event.is_private:
        return
    sender_id = event.sender_id
    if sender_id == me_id:
        return
    if sender_id in welcomed_users:
        return
    await event.reply(welcome_message)
    welcomed_users.add(sender_id)
    with open("welcome.json", "w") as f:
        json.dump({"message": welcome_message, "welcomed_users": list(welcomed_users)}, f)

@client.on(events.NewMessage(pattern=r"^.restart$", func=lambda e: e.sender_id == me_id))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?", func=lambda e: e.sender_id == me_id))
async def kick_user(event):
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda kullanılabilir.")
    try:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Kicklemek için kullanıcı belirt.")
        await event.chat.kick_participant(user.id)
        await event.reply(f"{user.first_name} gruptan atıldı.")
    except UserAdminInvalidError:
        await event.reply("Beni yönetici yapmalısın!")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?", func=lambda e: e.sender_id == me_id))
async def ban_user(event):
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda kullanılabilir.")
    try:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Banlamak için kullanıcı belirt.")
        await client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
        await event.reply(f"{user.first_name} gruptan banlandı.")
    except UserAdminInvalidError:
        await event.reply("Beni yönetici yapmalısın!")

@client.on(events.NewMessage(pattern=r"^.eval (.+)", func=lambda e: e.sender_id == admin_id))
async def eval_handler(event):
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        await event.reply(str(result))
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")

async def main():
    global me, me_id
    await client.start()
    me = await client.get_me()
    me_id = me.id
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
