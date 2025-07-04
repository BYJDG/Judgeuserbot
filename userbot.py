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

# Kayıtlı kişisel komutları yükle
if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r") as f:
        custom_commands = json.load(f)

# .alive komutu
@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

# .wlive sadece admin için
@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

# .judge komut listesi
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

# .afk komutu
@client.on(events.NewMessage(pattern=r"^.afk (.+)"))
async def afk_handler(event):
    global afk_mode, afk_reason
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    await event.edit(f"AFK moduna geçildi. Sebep: {afk_reason}")

# .back komutu
@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason
    afk_mode = False
    afk_reason = ""
    await event.edit("Tekrar aktif oldum!")

# AFK otomatik yanıt (sadece özel mesaj ve mention)
@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason
    if afk_mode and (event.is_private or (event.is_group and event.message.mentioned)):
        # Sadece ilk mesajda cevap ver
        if not getattr(event.chat, "afk_replied", False):
            await event.reply(f"Şuan AFK modundayım. Sebep: {afk_reason}")
            event.chat.afk_replied = True

# .filter komutu düzeltilmiş hali
@client.on(events.NewMessage(pattern=r"^.filter (\S+) (.+)"))
async def filter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filtered_messages[keyword] = response
    await event.reply(f"Filtre eklendi: {keyword} → {response}")

# .unfilter komutu
@client.on(events.NewMessage(pattern=r"^.unfilter (\S+)"))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        await event.reply(f"Filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait bir filtre bulunamadı.")

# Filtreli mesajlara cevap
@client.on(events.NewMessage())
async def filter_response(event):
    for keyword, response in filtered_messages.items():
        if keyword in event.raw_text.lower():
            await event.reply(response)
            break

# .ekle komutu düzeltilmiş hali
@client.on(events.NewMessage(pattern=r"^.ekle (\S+) (.+)"))
async def add_command(event):
    cmd = event.pattern_match.group(1).strip()
    reply = event.pattern_match.group(2).strip()
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w") as f:
        json.dump(custom_commands, f)
    await event.reply(f"Komut eklendi: {cmd} → {reply}")

# .sil komutu
@client.on(events.NewMessage(pattern=r"^.sil (\S+)"))
async def del_command(event):
    cmd = event.pattern_match.group(1).strip()
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w") as f:
            json.dump(custom_commands, f)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

# Kişisel komutlar için handler
@client.on(events.NewMessage())
async def custom_command_handler(event):
    text = event.raw_text.strip()
    if text in custom_commands:
        await event.reply(custom_commands[text])

# .restart komutu (herkes kullanabilir)
@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# .kick komutu (sadece bot sahibi kullanabilir)
@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    if event.sender_id != admin_id:
        return
    if event.is_group:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Kicklemek için kullanıcı belirt.")
        await event.chat.kick_participant(user.id)
        await event.reply(f"{user.first_name} gruptan atıldı.")

# .ban komutu (sadece bot sahibi kullanabilir)
@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    if event.sender_id != admin_id:
        return
    if event.is_group:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Banlamak için kullanıcı belirt.")
        await client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
        await event.reply(f"{user.first_name} gruptan banlandı.")

# .eval komutu (sadece admin)
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

async def main():
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
