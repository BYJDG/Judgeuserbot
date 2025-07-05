import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id, admin_username

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
afk_replied_users = set()  # Gruba özel afk'da kullanıcıya sadece 1 kere cevap vermek için

filtered_messages = {}     # Özel mesajlarda geçerli filtreler
all_filtered_messages = {} # Her yerde geçerli filtreler
custom_commands = {}       # Kullanıcıya özel komutlar

WELCOME_MESSAGE = None     # .welcome komutu ile ayarlanacak karşılamalar

# Load saved data (filterler, komutlar, welcome mesajı)
if os.path.exists("filtered_messages.json"):
    with open("filtered_messages.json", "r", encoding="utf-8") as f:
        filtered_messages = json.load(f)

if os.path.exists("all_filtered_messages.json"):
    with open("all_filtered_messages.json", "r", encoding="utf-8") as f:
        all_filtered_messages = json.load(f)

if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r", encoding="utf-8") as f:
        custom_commands = json.load(f)

if os.path.exists("welcome_message.txt"):
    with open("welcome_message.txt", "r", encoding="utf-8") as f:
        WELCOME_MESSAGE = f.read()

def save_filtered():
    with open("filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages, f, ensure_ascii=False, indent=2)

def save_all_filtered():
    with open("all_filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(all_filtered_messages, f, ensure_ascii=False, indent=2)

def save_custom_commands():
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)

def save_welcome():
    with open("welcome_message.txt", "w", encoding="utf-8") as f:
        f.write(WELCOME_MESSAGE if WELCOME_MESSAGE else "")


# --- KOMUTLAR ---

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    me = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {me.first_name} ❤️\n\nBot Versiyonu: v1.0")

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
        ".filter <kelime> <cevap> - Özel mesajlarda filtre ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".allfilter <kelime> <cevap> - Her yerde geçerli filtre ekler.\n"
        ".unallfilter <kelime> - Genel filtreyi kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".welcome <mesaj> - Karşılama mesajını ayarlar.\n"
        ".welcome_sil - Karşılama mesajını siler.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar (bot sahibi).\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar (bot sahibi).\n"
        ".eval <kod> - Yalnızca admin çalıştırabilir.\n"
        ".wlive - Global admin için sistem durumu."
    )
    await event.reply(help_text)

# --- AFK KOMUTLARI ---

@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    afk_mode = True
    afk_reason = event.pattern_match.group(1) or "AFK"
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

    if not afk_mode:
        return

    if event.is_private and event.sender_id != (await client.get_me()).id:
        # Özel mesajda direkt cevap ver
        await event.reply(f"Şuan AFK'yım. Sebep: {afk_reason}")
        return

    # Grup mesajlarında sadece kullanıcıya bir kere cevap ver
    if event.is_group or event.is_channel:
        if event.sender_id == (await client.get_me()).id:
            return  # Kendine cevap verme

        # Eğer mesajda bot etiketlenmiş ya da reply ile mesaj gelmişse cevap ver
        if event.message.mentioned or event.is_reply:
            if event.sender_id not in afk_replied_users:
                afk_replied_users.add(event.sender_id)
                await event.reply(f"Şuan AFK'yım. Sebep: {afk_reason}")

# --- FİLTRELER ---

@client.on(events.NewMessage(pattern=r"^.filter (\S+) (.+)", func=lambda e: e.is_private))
async def filter_add(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filtered_messages[keyword] = response
    save_filtered()
    await event.reply(f"Özel mesaj filtresi eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.unfilter (\S+)", func=lambda e: e.is_private))
async def filter_remove(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        save_filtered()
        await event.reply(f"Özel mesaj filtresi kaldırıldı: {keyword}")
    else:
        await event.reply("Böyle bir filtre bulunamadı.")

@client.on(events.NewMessage(pattern=r"^.allfilter (\S+) (.+)"))
async def allfilter_add(event):
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    all_filtered_messages[keyword] = response
    save_all_filtered()
    await event.reply(f"Genel filtre eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.unallfilter (\S+)"))
async def allfilter_remove(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        save_all_filtered()
        await event.reply(f"Genel filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Böyle bir genel filtre bulunamadı.")

@client.on(events.NewMessage())
async def filter_response(event):
    text_lower = event.raw_text.lower()
    # Önce genel filtreler kontrol edilir
    for keyword, response in all_filtered_messages.items():
        if keyword in text_lower:
            await event.reply(response)
            return

    # Özel mesajda ise özel filtreler çalışır
    if event.is_private:
        for keyword, response in filtered_messages.items():
            if keyword in text_lower:
                await event.reply(response)
                return

# --- KİŞİSEL KOMUTLAR ---

@client.on(events.NewMessage(pattern=r"^.ekle (\.\S+) (.+)"))
async def add_custom_command(event):
    cmd = event.pattern_match.group(1).strip()
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    save_custom_commands()
    await event.reply(f"Kişisel komut eklendi: {cmd} → {reply}")

@client.on(events.NewMessage(pattern=r"^.sil (\.\S+)"))
async def del_custom_command(event):
    cmd = event.pattern_match.group(1).strip()
    if cmd in custom_commands:
        del custom_commands[cmd]
        save_custom_commands()
        await event.reply(f"Kişisel komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir kişisel komut bulunamadı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    text = event.raw_text.strip()
    if text in custom_commands:
        reply = custom_commands[text]
        # Kod blokları varsa kod bloğu olarak gönder
        if reply.startswith("```") and reply.endswith("```"):
            await event.reply(reply)
        else:
            await event.reply(reply)

# --- KARŞILAMA MESAJI ---

@client.on(events.NewMessage(pattern=r"^.welcome (.+)"))
async def set_welcome(event):
    global WELCOME_MESSAGE
    if event.sender_id != admin_id:
        return
    WELCOME_MESSAGE = event.pattern_match.group(1)
    save_welcome()
    await event.reply(f"Karşılama mesajı ayarlandı:\n{WELCOME_MESSAGE}")

@client.on(events.NewMessage(pattern=r"^.welcome_sil$"))
async def del_welcome(event):
    global WELCOME_MESSAGE
    if event.sender_id != admin_id:
        return
    WELCOME_MESSAGE = None
    save_welcome()
    await event.reply("Karşılama mesajı silindi.")

@client.on(events.ChatAction())
async def welcome_new_user(event):
    if WELCOME_MESSAGE and (event.user_added or event.user_joined):
        await event.reply(WELCOME_MESSAGE)

# --- YÖNETİCİ KOMUTLARI ---

@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    if event.sender_id != admin_id:
        return
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.eval (.+)"))
async def eval_handler(event):
    if event.sender_id != admin_id:
        return
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        await event.reply(str(result))
    except Exception as e:
        await event.reply(f"Hata: {e}")

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    # Sadece bot sahibi kullanabilir
    if event.sender_id != admin_id:
        return

    if not event.is_group and not event.is_channel:
        await event.reply("Bu komut sadece gruplarda kullanılabilir.")
        return

    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        user = await client.get_entity(event.pattern_match.group(1))
    else:
        await event.reply("Kicklemek için kullanıcı belirtmelisiniz.")
        return

    await event.chat.kick_participant(user.id)
    await event.reply(f"{user.first_name} gruptan atıldı.")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    # Sadece bot sahibi kullanabilir
    if event.sender_id != admin_id:
        return

    if not event.is_group and not event.is_channel:
        await event.reply("Bu komut sadece gruplarda kullanılabilir.")
        return

    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        user = await client.get_entity(event.pattern_match.group(1))
    else:
        await event.reply("Banlamak için kullanıcı belirtmelisiniz.")
        return

    rights = ChatBannedRights(until_date=None, view_messages=True)
    await client(EditBannedRequest(event.chat_id, user.id, rights))
    await event.reply(f"{user.first_name} gruptan banlandı.")

# --- MESAJLARI DÜZENLEYEREK YANIT ---

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_edit_handler(event):
    me = await event.client.get_me()
    await event.delete()
    await event.respond(f"Userbotunuz çalışıyor... Seni seviyorum {me.first_name} ❤️\n\nBot Versiyonu: v1.0")

# Komutları yalnızca bot kurulu hesabın kullanması için izin:
def is_owner(event):
    return event.sender_id == (client.session.user_id)

# Örnek diğer komutlarda da owner kontrolü eklenebilir.

# --- BOT BAŞLATMA ---

async def main():
    print("JudgeUserBot çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
