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
welcomed_users = set()

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

# .wlive
@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

# .judge
@client.on(events.NewMessage(pattern=r"^.judge$"))
async def judge_handler(event):
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive\n.afk <sebep>\n.back\n"
        ".filter <kelime> <cevap>\n.unfilter <kelime>\n.filters\n"
        ".allfilter <kelime> <cevap>\n.unallfilter <kelime>\n.allfilters\n"
        ".ekle <.komut> <cevap>\n.sil <.komut>\n"
        ".restart\n.kick\n.ban\n.eval\n"
        ".welcome <mesaj>\n.unwelcome\n"
        ".wlive"
    )
    await event.reply(help_text)

# .afk / .back / AFK cevap
@client.on(events.NewMessage(pattern=r"^.afk (.+)"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    afk_replied_users.clear()
    await event.edit("AFK moduna geçildi.")

@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = False
    afk_reason = ""
    afk_replied_users.clear()
    await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    if afk_mode and event.sender_id != (await client.get_me()).id:
        if event.is_private or (event.is_group and (event.mentioned or event.is_reply)):
            if event.sender_id not in afk_replied_users:
                await event.reply(afk_reason)
                afk_replied_users.add(event.sender_id)

# .filter / .filters / .unfilter / cevap
@client.on(events.NewMessage(pattern=r"^.filter (\S+) ([\s\S]+)"))
async def filter_handler(event):
    if event.is_private and event.sender_id == (await client.get_me()).id:
        keyword = event.pattern_match.group(1).lower()
        response = event.pattern_match.group(2)
        filtered_messages[keyword] = response
        await event.reply(f"Filtre eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.filters$"))
async def filters_list_handler(event):
    if not filtered_messages:
        return await event.reply("📥 PM filtresi yok.")
    msg = "📅 PM Filtreleri:\n" + "\n".join(f"- {k}" for k in filtered_messages)
    await event.reply(msg)

@client.on(events.NewMessage(pattern=r"^.unfilter (.+)"))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        await event.reply(f"{keyword} filtresi kaldırıldı.")
    else:
        await event.reply("Böyle bir filtre yok.")

@client.on(events.NewMessage())
async def filter_response(event):
    if event.is_private and event.sender_id != (await client.get_me()).id:
        for keyword, response in filtered_messages.items():
            if keyword.lower() in event.raw_text.lower():
                await event.reply(response)
                break

# .allfilter / .allfilters / .unallfilter / genel cevap
@client.on(events.NewMessage(pattern=r"^.allfilter (\S+) ([\s\S]+)"))
async def allfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    all_filtered_messages[keyword] = response
    await event.reply(f"Genel filtre eklendi: {keyword}")

@client.on(events.NewMessage(pattern=r"^.allfilters$"))
async def allfilters_list_handler(event):
    if not all_filtered_messages:
        return await event.reply("🌐 Genel filtre yok.")
    msg = "🌐 Genel Filtreler:\n" + "\n".join(f"- {k}" for k in all_filtered_messages)
    await event.reply(msg)

@client.on(events.NewMessage(pattern=r"^.unallfilter (.+)"))
async def unallfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        await event.reply(f"{keyword} genel filtresi kaldırıldı.")
    else:
        await event.reply("Böyle bir genel filtre yok.")

@client.on(events.NewMessage())
async def all_filter_response(event):
    for keyword, response in all_filtered_messages.items():
        if keyword.lower() in event.raw_text.lower():
            await event.reply(response)
            break

# .ekle / .sil / özel komut çalıştır
@client.on(events.NewMessage(pattern=r"^.ekle (\.\S+) ([\s\S]+)"))
async def add_command(event):
    if event.sender_id == (await client.get_me()).id:
        cmd = event.pattern_match.group(1)
        reply = event.pattern_match.group(2)
        custom_commands[cmd] = reply
        with open("custom_commands.json", "w") as f:
            json.dump(custom_commands, f)
        await event.reply(f"Komut eklendi: {cmd}")

@client.on(events.NewMessage(pattern=r"^.sil (\.\S+)"))
async def del_command(event):
    if event.sender_id == (await client.get_me()).id:
        cmd = event.pattern_match.group(1)
        if cmd in custom_commands:
            del custom_commands[cmd]
            with open("custom_commands.json", "w") as f:
                json.dump(custom_commands, f)
            await event.reply(f"{cmd} komutu silindi.")
        else:
            await event.reply("Böyle bir komut yok.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    if event.raw_text.strip() in custom_commands:
        await event.reply(custom_commands[event.raw_text.strip()])

# .restart
@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# .welcome
@client.on(events.NewMessage(pattern=r"^.welcome(?: ([\s\S]+))?"))
async def welcome_handler(event):
    global welcome_message, welcome_enabled, welcomed_users
    if event.pattern_match.group(1):
        welcome_message = event.pattern_match.group(1)
        with open("welcome.json", "w") as f:
            json.dump({"message": welcome_message, "enabled": True}, f)
        welcome_enabled = True
        welcomed_users.clear()
        await event.reply("Karşılama mesajı ayarlandı ve aktif edildi.")
    elif welcome_message:
        welcome_enabled = True
        with open("welcome.json", "w") as f:
            json.dump({"message": welcome_message, "enabled": True}, f)
        welcomed_users.clear()
        await event.reply("Karşılama mesajı tekrar aktif edildi.")
    else:
        await event.reply("İlk önce bir karşılama mesajı belirlemelisin.")

@client.on(events.NewMessage(pattern=r"^.unwelcome$"))
async def unwelcome_handler(event):
    global welcome_enabled
    welcome_enabled = False
    with open("welcome.json", "w") as f:
        json.dump({"message": welcome_message, "enabled": False}, f)
    await event.reply("Karşılama mesajı devre dışı bırakıldı.")

@client.on(events.NewMessage())
async def welcome_auto(event):
    if welcome_enabled and event.is_private and event.sender_id != (await client.get_me()).id:
        sender_id = str(event.sender_id)
        if sender_id not in welcomed_users:
            await event.reply(welcome_message)
            welcomed_users.add(sender_id)

# Botu başlat
async def main():
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
                
