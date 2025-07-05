import asyncio
import os
import json
import re
import sys
from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id  # admin_id int, kendi user_id'n

client = TelegramClient(session_name, api_id, api_hash)

# --- GLOBAL DEĞİŞKENLER ---
afk_mode = False
afk_reason = ""
afk_replied_users = set()

filtered_messages = {}
all_filtered_messages = {}

custom_commands = {}

welcome_active = False
welcome_message = ""
welcomed_users = set()

# --- DOSYALARDAN YÜKLEME ---
if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r", encoding="utf-8") as f:
        custom_commands = json.load(f)

if os.path.exists("filtered_messages.json"):
    with open("filtered_messages.json", "r", encoding="utf-8") as f:
        filtered_messages = json.load(f)

if os.path.exists("all_filtered_messages.json"):
    with open("all_filtered_messages.json", "r", encoding="utf-8") as f:
        all_filtered_messages = json.load(f)

if os.path.exists("welcome.json"):
    with open("welcome.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        welcome_active = data.get("active", False)
        welcome_message = data.get("message", "")

if os.path.exists("welcomed_users.json"):
    with open("welcomed_users.json", "r", encoding="utf-8") as f:
        welcomed_users = set(json.load(f))


# --- YARDIMCI FONKSİYONLAR ---
async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id


async def is_admin(event):
    # admin komutları için sadece owner/admin
    return event.sender_id == admin_id or await is_owner(event)


# --- KOMUTLAR ---

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await client.get_me()
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
        ".filter <kelime> <cevap> - Özel mesajlarda çalışan filtre ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".allfilter <kelime> <cevap> - Tüm sohbetlerde çalışan filtre ekler.\n"
        ".unallfilter <kelime> - Tüm sohbet filtresini kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".welcome <mesaj> - Özel mesajlarda yeni kişilere karşılama mesajı.\n"
        ".unwelcome - Karşılama mesajını kapatır.\n"
        ".restart - Botu yeniden başlatır (owner+bot sahibi).\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar (bot sahibi).\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar (bot sahibi).\n"
        ".eval <kod> - Yalnızca admin kullanabilir.\n"
        ".wlive - Global admin için sistem durumu.\n"
    )
    await event.reply(help_text)


# --- AFK MODU ---

@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = True
    reason = event.pattern_match.group(1)
    afk_reason = reason if reason else "AFK"
    afk_replied_users = set()
    await event.edit(f"AFK moduna geçtin. Sebep: {afk_reason}")


@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = False
    afk_reason = ""
    afk_replied_users = set()
    await event.edit("Tekrar aktif oldum!")


@client.on(events.NewMessage)
async def afk_auto_reply(event):
    global afk_mode, afk_replied_users, afk_reason
    if not afk_mode:
        return
    # Kendi mesajına cevap verme
    me = await client.get_me()
    if event.sender_id == me.id:
        return

    # Özel veya grup mesajı
    if event.is_private or event.is_group:
        # Sadece mesaj bana geliyorsa
        if event.is_group:
            # Etiket veya reply değilse atlama
            if not (event.is_reply or event.message.mentioned):
                return

        # Daha önce cevap verdiğimiz kişiye cevap verme
        if event.sender_id in afk_replied_users:
            return

        afk_replied_users.add(event.sender_id)
        await event.reply(f"Şu an AFK'yım. Sebep: {afk_reason}")


# --- FILTER KOMUTLARI ---

@client.on(events.NewMessage(pattern=r"^.filter (\S+) (.+)", func=lambda e: e.is_private and e.sender_id == (await client.get_me()).id))
async def filter_add(event):
    global filtered_messages
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filtered_messages[keyword] = response
    with open("filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
    await event.reply(f"Filtre eklendi: {keyword}")


@client.on(events.NewMessage(pattern=r"^.unfilter (\S+)", func=lambda e: e.is_private and e.sender_id == (await client.get_me()).id))
async def filter_remove(event):
    global filtered_messages
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        with open("filtered_messages.json", "w", encoding="utf-8") as f:
            json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
        await event.reply(f"Filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait filtre bulunamadı.")


@client.on(events.NewMessage(pattern=r".*"))
async def filter_response(event):
    global filtered_messages
    if not filtered_messages:
        return
    # Sadece özel mesajlarda çalışır
    if not event.is_private:
        return
    text = event.raw_text.lower()
    for keyword, response in filtered_messages.items():
        if keyword in text:
            await event.reply(response)
            break


# --- ALLFILTER KOMUTLARI (Tüm sohbetlerde) ---

@client.on(events.NewMessage(pattern=r"^.allfilter (\S+) (.+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def allfilter_add(event):
    global all_filtered_messages
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    all_filtered_messages[keyword] = response
    with open("all_filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(all_filtered_messages, f, ensure_ascii=False, indent=2)
    await event.reply(f"Allfilter eklendi: {keyword}")


@client.on(events.NewMessage(pattern=r"^.unallfilter (\S+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def allfilter_remove(event):
    global all_filtered_messages
    keyword = event.pattern_match.group(1).lower()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        with open("all_filtered_messages.json", "w", encoding="utf-8") as f:
            json.dump(all_filtered_messages, f, ensure_ascii=False, indent=2)
        await event.reply(f"Allfilter kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait allfilter bulunamadı.")


@client.on(events.NewMessage(pattern=r".*"))
async def allfilter_response(event):
    global all_filtered_messages
    if not all_filtered_messages:
        return
    text = event.raw_text.lower()
    for keyword, response in all_filtered_messages.items():
        if keyword in text:
            await event.reply(response)
            break


# --- KİŞİSEL KOMUTLAR ---

@client.on(events.NewMessage(pattern=r"^.ekle (\S+) (.+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def add_command(event):
    global custom_commands
    cmd = event.pattern_match.group(1).strip()
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)
    await event.reply(f"Komut eklendi: {cmd}")


@client.on(events.NewMessage(pattern=r"^.sil (\S+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def delete_command(event):
    global custom_commands
    cmd = event.pattern_match.group(1).strip()
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w", encoding="utf-8") as f:
            json.dump(custom_commands, f, ensure_ascii=False, indent=2)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")


@client.on(events.NewMessage(pattern=r".*"))
async def custom_command_handler(event):
    global custom_commands
    text = event.raw_text.strip()
    if text in custom_commands:
        await event.reply(custom_commands[text])


# --- WELCOME KOMUTLARI ---

@client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?", func=lambda e: e.sender_id == (await client.get_me()).id))
async def welcome_cmd(event):
    global welcome_active, welcome_message
    text = event.pattern_match.group(1)
    welcome_active = True
    if text:
        welcome_message = text
    with open("welcome.json", "w", encoding="utf-8") as f:
        json.dump({"active": welcome_active, "message": welcome_message}, f, ensure_ascii=False, indent=2)
    await event.reply(f"Karşılama mesajı aktif! Mesaj:\n\n{welcome_message}")


@client.on(events.NewMessage(pattern=r"^.unwelcome$", func=lambda e: e.sender_id == (await client.get_me()).id))
async def unwelcome_cmd(event):
    global welcome_active
    welcome_active = False
    with open("welcome.json", "w", encoding="utf-8") as f:
        json.dump({"active": welcome_active, "message": welcome_message}, f, ensure_ascii=False, indent=2)
    await event.reply("Karşılama mesajı devre dışı bırakıldı.")


@client.on(events.NewMessage(func=lambda e: e.is_private))
async def send_welcome(event):
    global welcomed_users, welcome_active, welcome_message
    if not welcome_active:
        return
    user_id = event.sender_id
    if user_id == (await client.get_me()).id:
        return  # Bot kendi mesajına cevap vermesin
    if user_id in welcomed_users:
        return
    await event.reply(welcome_message)
    welcomed_users.add(user_id)
    with open("welcomed_users.json", "w", encoding="utf-8") as f:
        json.dump(list(welcomed_users), f, ensure_ascii=False, indent=2)


# --- KULLANICIYA ÖZEL KOMUTLAR (OWNER + BOT SAHİBİ) ---

@client.on(events.NewMessage(pattern=r"^.restart$", func=lambda e: e.sender_id == admin_id))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    await client.disconnect()
    os.execv(sys.executable, [sys.executable] + sys.argv)


@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?", func=lambda e: e.sender_id == admin_id))
async def kick_user(event):
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda kullanılabilir.")
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except errors.UsernameNotOccupiedError:
            return await event.reply("Kullanıcı bulunamadı.")
    else:
        return await event.reply("Kicklemek için kullanıcı belirt.")
    await event.client.kick_participant(event.chat_id, user.id)
    await event.reply(f"{user.first_name} gruptan atıldı.")


@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?", func=lambda e: e.sender_id == admin_id))
async def ban_user(event):
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda kullanılabilir.")
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except errors.UsernameNotOccupiedError:
            return await event.reply("Kullanıcı bulunamadı.")
    else:
        return await event.reply("Banlamak için kullanıcı belirt.")
    rights = ChatBannedRights(until_date=None, view_messages=True)
    await client(EditBannedRequest(event.chat_id, user.id, rights))
    await event.reply(f"{user.first_name} gruptan banlandı.")


@client.on(events.NewMessage(pattern=r"^.eval (.+)", func=lambda e: e.sender_id == admin_id))
async def eval_handler(event):
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        await event.reply(str(result))
    except Exception as e:
        await event.reply(f"Hata: {e}")


# --- BOTU BAŞLAT ---
async def main():
    print("JudgeUserBot çalışıyor...")
    await client.start()
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
