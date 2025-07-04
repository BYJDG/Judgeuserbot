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

# Verileri dosyadan yükle
if os.path.exists("filtered_messages.json"):
    with open("filtered_messages.json", "r", encoding="utf-8") as f:
        filtered_messages = json.load(f)

if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r", encoding="utf-8") as f:
        custom_commands = json.load(f)


# Komut: .alive
@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")


# Komut: .wlive (Sadece global admin)
@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return  # Sadece admin kullanabilir
    await event.reply(
        "🔥 JudgeBot Aktif 🔥\n"
        "Sorunsuz çalışıyor.\n"
        "Bot Versiyonu: v1.0"
    )


# Komut: .judge - Yardım metni
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
        ".eval <kod> - Yalnızca admin kullanabilir.\n"
        ".wlive - Global admin için sistem durumu."
    )
    await event.reply(help_text)


# Komut: .afk <sebep>
@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason
    if afk_mode:
        await event.reply("Zaten AFK modundasınız.")
        return

    reason = event.pattern_match.group(1)
    afk_mode = True
    afk_reason = reason if reason else "Sebep belirtilmedi."
    await event.edit(f"AFK moduna geçildi. Sebep: {afk_reason}")


# Komut: .back
@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason
    if not afk_mode:
        await event.reply("Zaten AFK modunda değilsiniz.")
        return

    afk_mode = False
    afk_reason = ""
    await event.edit("Tekrar aktif oldum!")


# AFK moddayken özelden gelen ilk mesajda cevap verir, sonra sessize alır
afk_replied_to = set()


@client.on(events.NewMessage(incoming=True))
async def afk_auto_reply(event):
    global afk_mode, afk_reason, afk_replied_to
    if not afk_mode:
        return
    if event.is_private:
        sender = event.sender_id
        if sender not in afk_replied_to and sender != (await client.get_me()).id:
            await event.reply(afk_reason)
            afk_replied_to.add(sender)
    elif event.is_group and event.message.mentioned:
        sender = event.sender_id
        if sender != (await client.get_me()).id:
            await event.reply(afk_reason)


# Komut: .filter <kelime> <cevap>
@client.on(events.NewMessage(pattern=r"^.filter (\S+)", func=lambda e: e.sender_id == (await e.client.get_me()).id))
async def filter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    full_text = event.raw_text
    prefix = f".filter {keyword} "
    if full_text.startswith(prefix):
        response = full_text[len(prefix):].strip()
    else:
        await event.reply("Filtre komutu doğru formatta değil.")
        return

    filtered_messages[keyword] = response
    with open("filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
    await event.reply(f"Filtre eklendi: {keyword} → {response}")


# Komut: .unfilter <kelime>
@client.on(events.NewMessage(pattern=r"^.unfilter (\S+)", func=lambda e: e.sender_id == (await e.client.get_me()).id))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        with open("filtered_messages.json", "w", encoding="utf-8") as f:
            json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
        await event.reply(f"Filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait bir filtre bulunamadı.")


# Filtrelere yanıt ver
@client.on(events.NewMessage(incoming=True))
async def filter_response(event):
    text = event.raw_text.lower()
    for keyword, response in filtered_messages.items():
        if keyword in text:
            await event.reply(response)
            break


# Komut: .ekle <.komut> <cevap> (Kişisel komut ekle)
@client.on(events.NewMessage(pattern=r"^.ekle (\.\S+)", func=lambda e: e.sender_id == (await e.client.get_me()).id))
async def add_command(event):
    cmd = event.pattern_match.group(1).strip()
    full_text = event.raw_text
    prefix = f".ekle {cmd} "
    if full_text.startswith(prefix):
        reply = full_text[len(prefix):].strip()
    else:
        await event.reply("Komut ve cevap doğru formatta değil.")
        return

    custom_commands[cmd] = reply
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)
    await event.reply(f"Komut eklendi: {cmd} → {reply}")


# Komut: .sil <.komut> (Kişisel komut sil)
@client.on(events.NewMessage(pattern=r"^.sil (\.\S+)", func=lambda e: e.sender_id == (await e.client.get_me()).id))
async def del_command(event):
    cmd = event.pattern_match.group(1).strip()
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w", encoding="utf-8") as f:
            json.dump(custom_commands, f, ensure_ascii=False, indent=2)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")


# Kişisel komutları çalıştır
@client.on(events.NewMessage(incoming=True))
async def custom_command_handler(event):
    text = event.raw_text.strip()
    if text in custom_commands:
        reply = custom_commands[text]
        # Eğer mesaj kod bloğu olarak gönderilmek isteniyorsa,
        # burada basitçe ``` kod bloğu içinde gönderebiliriz:
        if reply.startswith("```") and reply.endswith("```"):
            await event.reply(reply)
        else:
            await event.reply(reply)


# Komut: .restart (Sadece owner)
@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    if event.sender_id != admin_id:
        return
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


# Komut: .kick <id veya reply> (Sadece owner, grup içinde)
@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    if event.sender_id != admin_id:
        return
    if not event.is_group:
        await event.reply("Bu komut sadece gruplarda çalışır.")
        return

    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        user = await client.get_entity(event.pattern_match.group(1))
    else:
        await event.reply("Kicklemek için kullanıcı belirt.")
        return

    await event.chat.kick_participant(user.id)
    await event.reply(f"{user.first_name} gruptan atıldı.")


# Komut: .ban <id veya reply> (Sadece owner, grup içinde)
@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    if event.sender_id != admin_id:
        return
    if not event.is_group:
        await event.reply("Bu komut sadece gruplarda çalışır.")
        return

    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        user = await client.get_entity(event.pattern_match.group(1))
    else:
        await event.reply("Banlamak için kullanıcı belirt.")
        return

    banned_rights = ChatBannedRights(
        until_date=None,
        view_messages=True,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    await client(EditBannedRequest(event.chat_id, user.id, banned_rights))
    await event.reply(f"{user.first_name} gruptan banlandı.")


# Komut: .eval (Sadece admin)
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
