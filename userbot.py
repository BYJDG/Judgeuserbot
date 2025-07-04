import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
from config import api_id, api_hash, session_name, admin_username, admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""

filtered_messages = {}
custom_commands = {}

# Load filtered messages
if os.path.exists("filtered_messages.json"):
    with open("filtered_messages.json", "r", encoding="utf-8") as f:
        filtered_messages = json.load(f)

# Load custom commands
if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r", encoding="utf-8") as f:
        custom_commands = json.load(f)

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return  # Sadece admin kullanabilir
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

@client.on(events.NewMessage(pattern=r"^.judge$"))
async def judge_help(event):
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalıştığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <kelime> <cevap> - Otomatik yanıt ekler.\n"
        ".unfilter <kelime> - Filtreyi kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar.\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar.\n"
        ".eval <kod> - Yalnızca admin çalıştırabilir.\n"
        ".wlive - Global admin için sistem durumu."
    )
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^.afk (.+)"))
async def afk_handler(event):
    global afk_mode, afk_reason
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    await event.edit(f"AFK moduna geçildi.\nSebep: {afk_reason}")

@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason
    afk_mode = False
    afk_reason = ""
    await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode
    if afk_mode and event.is_private and event.sender_id != (await client.get_me()).id:
        await event.reply(f"Şu anda AFK'yım. Sebep: {afk_reason}")
        afk_mode = False

@client.on(events.NewMessage(pattern=r"^.filter (.+?) (.+)", func=lambda e: e.sender_id == client.get_me().id))
async def filter_handler(event):
    keyword, response = event.pattern_match.group(1).lower(), event.pattern_match.group(2)
    filtered_messages[keyword] = response
    with open("filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
    await event.reply(f"Filtre eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.unfilter (.+)", func=lambda e: e.sender_id == client.get_me().id))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        with open("filtered_messages.json", "w", encoding="utf-8") as f:
            json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
        await event.reply(f"Filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait bir filtre bulunamadı.")

@client.on(events.NewMessage())
async def filter_response(event):
    text = event.raw_text.lower()
    for keyword, response in filtered_messages.items():
        if keyword in text:
            await event.reply(f"```\n{response}\n```")
            break

@client.on(events.NewMessage(pattern=r"^.ekle (\.\S+) ([\s\S]+)", func=lambda e: e.sender_id == client.get_me().id))
async def add_command(event):
    cmd = event.pattern_match.group(1).strip()
    reply = event.pattern_match.group(2).strip()
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)
    await event.reply(f"Komut eklendi: {cmd} → {reply}")

@client.on(events.NewMessage(pattern=r"^.sil (\.\S+)", func=lambda e: e.sender_id == client.get_me().id))
async def del_command(event):
    cmd = event.pattern_match.group(1).strip()
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w", encoding="utf-8") as f:
            json.dump(custom_commands, f, ensure_ascii=False, indent=2)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    text = event.raw_text.strip()
    if text in custom_commands:
        await event.reply(f"```\n{custom_commands[text]}\n```")

@client.on(events.NewMessage(pattern=r"^.restart$", func=lambda e: e.sender_id == client.get_me().id))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    # .kick sadece bot sahibi kullanabilir
    if event.sender_id != (await client.get_me()).id:
        return
    if event.is_group or event.is_channel:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Kicklemek için kullanıcı belirt.")
        await event.chat.kick_participant(user.id)
        await event.reply(f"{user.first_name} gruptan atıldı.")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    # .ban sadece bot sahibi kullanabilir
    if event.sender_id != (await client.get_me()).id:
        return
    if event.is_group or event.is_channel:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Banlamak için kullanıcı belirt.")
        await client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
        await event.reply(f"{user.first_name} gruptan banlandı.")

@client.on(events.NewMessage(pattern=r"^.eval (.+)"))
async def eval_handler(event):
    if event.sender_id != admin_id:
        return
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        await event.reply(f"```\n{result}\n```")
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")

async def main():
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
