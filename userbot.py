import asyncio
import os
import json
import sys
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
afk_replied_users = set()

filtered_messages = {}
all_filtered_messages = {}
custom_commands = {}

welcome_message = ""
welcomed_users = set()

# Yükleme fonksiyonları
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

filtered_messages = load_json("filtered_messages.json", {})
all_filtered_messages = load_json("all_filtered_messages.json", {})
custom_commands = load_json("custom_commands.json", {})
welcome_data = load_json("welcome.json", {"message": "", "welcomed_users": []})
welcome_message = welcome_data.get("message", "")
welcomed_users = set(welcome_data.get("welcomed_users", []))


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
        ".unallfilter <kelime> - Her yerdeki filtresini kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".welcome <mesaj> - Karşılama mesajı ayarlar.\n"
        ".unwelcome - Karşılama mesajını kapatır.\n"
        ".back - AFK modundan çıkar.\n"
        ".afk <sebep> - AFK moduna geçer.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar. (Owner & Kullanıcı)\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar. (Owner & Kullanıcı)\n"
        ".eval <kod> - Yalnızca admin kullanabilir.\n"
        ".wlive - Global admin için sistem durumu.\n"
    )
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    reason = event.pattern_match.group(1)
    afk_mode = True
    afk_reason = reason if reason else "AFK modundayım."
    afk_replied_users = set()
    await event.edit(f"AFK moduna geçildi. Sebep: {afk_reason}")

@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = False
    afk_reason = ""
    afk_replied_users = set()
    await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason, afk_replied_users
    if afk_mode and event.sender_id != (await client.get_me()).id:
        # Özel mesaj veya grupta etiketleme durumları için
        if event.is_private or (event.is_group and (await event.get_reply_message()) and (await event.get_reply_message()).sender_id == (await client.get_me()).id) or (event.is_group and (await event.message.get_entities_text()) and f"@{(await client.get_me()).username}" in event.raw_text):
            if event.sender_id not in afk_replied_users:
                await event.reply(f"Şuan AFK sebebim: {afk_reason}")
                afk_replied_users.add(event.sender_id)

@client.on(events.NewMessage(pattern=r"^.filter (\S+) (.+)", func=lambda e: e.is_private and e.sender_id == (await client.get_me()).id))
async def filter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filtered_messages[keyword] = response
    save_json("filtered_messages.json", filtered_messages)
    await event.reply(f"Özel mesaj filtresi eklendi: {keyword}")

@client.on(events.NewMessage(pattern=r"^.allfilter (\S+) (.+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def allfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    all_filtered_messages[keyword] = response
    save_json("all_filtered_messages.json", all_filtered_messages)
    await event.reply(f"Genel filtre eklendi: {keyword}")

@client.on(events.NewMessage(pattern=r"^.unfilter (\S+)", func=lambda e: e.is_private and e.sender_id == (await client.get_me()).id))
async def unfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        save_json("filtered_messages.json", filtered_messages)
        await event.reply(f"Özel mesaj filtresi kaldırıldı: {keyword}")
    else:
        await event.reply(f"Özel mesaj filtresi bulunamadı: {keyword}")

@client.on(events.NewMessage(pattern=r"^.unallfilter (\S+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def unallfilter_handler(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        save_json("all_filtered_messages.json", all_filtered_messages)
        await event.reply(f"Genel filtre kaldırıldı: {keyword}")
    else:
        await event.reply(f"Genel filtre bulunamadı: {keyword}")

@client.on(events.NewMessage())
async def filter_auto_reply(event):
    text_lower = event.raw_text.lower()
    if event.is_private and event.sender_id == (await client.get_me()).id:
        # Botun kendisine yazılan mesajlara cevap verme
        return
    # Özel mesajlarda filtre
    if event.is_private:
        for keyword, response in filtered_messages.items():
            if keyword in text_lower:
                await event.reply(response)
                return
    # Genel filtre (gruplar dahil)
    for keyword, response in all_filtered_messages.items():
        if keyword in text_lower:
            await event.reply(response)
            return

@client.on(events.NewMessage(pattern=r"^.ekle (\.\S+) (.+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def add_command(event):
    cmd = event.pattern_match.group(1)
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    save_json("custom_commands.json", custom_commands)
    await event.reply(f"Kişisel komut eklendi: {cmd}")

@client.on(events.NewMessage(pattern=r"^.sil (\.\S+)", func=lambda e: e.sender_id == (await client.get_me()).id))
async def del_command(event):
    cmd = event.pattern_match.group(1)
    if cmd in custom_commands:
        del custom_commands[cmd]
        save_json("custom_commands.json", custom_commands)
        await event.reply(f"Kişisel komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    text = event.raw_text.strip()
    if text in custom_commands:
        reply = custom_commands[text]
        if reply.startswith("```") and reply.endswith("```"):
            # Kod bloğu ise kod olarak gönder
            await event.reply(reply, parse_mode='md')
        else:
            await event.reply(reply)

@client.on(events.NewMessage(pattern=r"^.restart$", func=lambda e: e.sender_id == (await client.get_me()).id))
async def restart_handler(event):
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda çalışır.")
    if event.sender_id != (await client.get_me()).id and event.sender_id != admin_id:
        return await event.reply("Bu komutu sadece owner kullanabilir.")
    user = None
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except Exception:
            return await event.reply("Geçerli bir kullanıcı belirtmelisiniz.")
    else:
        return await event.reply("Kicklemek için kullanıcı belirtin veya mesajı yanıtlayın.")
    await event.chat.kick_participant(user.id)
    await event.reply(f"{user.first_name} gruptan atıldı.")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda çalışır.")
    if event.sender_id != (await client.get_me()).id and event.sender_id != admin_id:
        return await event.reply("Bu komutu sadece owner kullanabilir.")
    user = None
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except Exception:
            return await event.reply("Geçerli bir kullanıcı belirtmelisiniz.")
    else:
        return await event.reply("Banlamak için kullanıcı belirtin veya mesajı yanıtlayın.")
    rights = ChatBannedRights(until_date=None, view_messages=True)
    await client(EditBannedRequest(event.chat_id, user.id, rights))
    await event.reply(f"{user.first_name} gruptan banlandı.")

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

@client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?"))
async def welcome_handler(event):
    global welcome_message, welcomed_users
    msg = event.pattern_match.group(1)
    if msg:
        welcome_message = msg
        welcomed_users = set()
        save_json("welcome.json", {"message": welcome_message, "welcomed_users": list(welcomed_users)})
        await event.reply(f"Karşılama mesajı ayarlandı:\n{welcome_message}")
    else:
        if welcome_message:
            await event.reply(f"Mevcut karşılama mesajı:\n{welcome_message}")
        else:
            await event.reply("Henüz karşılama mesajı ayarlanmadı.")

@client.on(events.NewMessage(pattern=r"^.unwelcome$"))
async def unwelcome_handler(event):
    global welcome_message, welcomed_users
    welcome_message = ""
    welcomed_users = set()
    save_json("welcome.json", {"message": welcome_message, "welcomed_users": list(welcomed_users)})
    await event.reply("Karşılama mesajı kapatıldı ve kayıtlı kullanıcılar sıfırlandı.")

@client.on(events.NewMessage())
async def welcome_auto_reply(event):
    global welcomed_users, welcome_message
    if not welcome_message:
        return
    if event.is_private and event.sender_id not in welcomed_users:
        await event.reply(welcome_message)
        welcomed_users.add(event.sender_id)
        save_json("welcome.json", {"message": welcome_message, "welcomed_users": list(welcomed_users)})

async def main():
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
