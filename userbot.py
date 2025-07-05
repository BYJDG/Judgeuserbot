import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id  # admin_id = byjudgee user_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""

filtered_messages = {}        # Özel mesaj filtreleri {keyword: cevap}
all_filtered_messages = {}    # Genel filtreler (gruplar ve özel her yerde)
welcome_message = None        # Karşılama mesajı
welcome_active = False        # Karşılama aktif mi?

afk_responded_users = set()  # AFK moddayken kullanıcılara sadece 1 kez yanıt vermek için

# Dosyadan verileri yükleme/kaydetme fonksiyonları

def save_filtered():
    with open("filtered_messages.json", "w") as f:
        json.dump(filtered_messages, f, ensure_ascii=False, indent=2)

def load_filtered():
    global filtered_messages
    if os.path.exists("filtered_messages.json"):
        with open("filtered_messages.json", "r") as f:
            filtered_messages = json.load(f)

def save_all_filtered():
    with open("all_filtered_messages.json", "w") as f:
        json.dump(all_filtered_messages, f, ensure_ascii=False, indent=2)

def load_all_filtered():
    global all_filtered_messages
    if os.path.exists("all_filtered_messages.json"):
        with open("all_filtered_messages.json", "r") as f:
            all_filtered_messages = json.load(f)

def save_welcome():
    with open("welcome.json", "w") as f:
        json.dump({"message": welcome_message, "active": welcome_active}, f, ensure_ascii=False, indent=2)

def load_welcome():
    global welcome_message, welcome_active
    if os.path.exists("welcome.json"):
        with open("welcome.json", "r") as f:
            data = json.load(f)
            welcome_message = data.get("message", None)
            welcome_active = data.get("active", False)

# Yükleme
load_filtered()
load_all_filtered()
load_welcome()

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    me = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {me.first_name} ❤️\n\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return  # Sadece admin görebilir
    await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

@client.on(events.NewMessage(pattern=r"^.judge$"))
async def judge_help(event):
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalıştığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <kelime> <cevap> - Özel mesajlarda filtreli otomatik cevap ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".allfilter <kelime> <cevap> - Genel filtre ekler (her yerde çalışır).\n"
        ".unallfilter <kelime> - Genel filtreyi kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".welcome <mesaj> - Özel mesajlarda karşılama mesajı ayarlar.\n"
        ".welcome - Karşılama mesajını tekrar aktif eder.\n"
        ".unwelcome - Karşılama mesajını kapatır.\n"
        ".restart - Botu yeniden başlatır. (Sahip ve adminler)\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar. (Sahip ve adminler)\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar. (Sahip ve adminler)\n"
        ".eval <kod> - Sadece sahibi kullanabilir.\n"
        ".wlive - Sadece sahibi görebilir."
    )
    await event.reply(help_text)

# AFK Komutları
@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_responded_users
    afk_mode = True
    afk_reason = event.pattern_match.group(1) or "AFK modundayım."
    afk_responded_users.clear()
    await event.edit(f"AFK moduna geçtin. Sebep: {afk_reason}")

@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_responded_users
    afk_mode = False
    afk_reason = ""
    afk_responded_users.clear()
    await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason, afk_responded_users
    if not afk_mode:
        return
    sender_id = event.sender_id

    # Sadece özel mesajlarda veya gruplarda adınla etiketlendiğinde cevap verir
    if event.is_private or (event.is_group and (await event.get_entities())[0].id == client.get_me().id):
        # Yanıt veya etiketli mesaj kontrolü
        is_mentioned = False
        if event.is_group:
            # Mesajda botun kullanıcı adı etiketlendi mi?
            if client.get_me().username and client.get_me().username.lower() in event.raw_text.lower():
                is_mentioned = True
        if event.is_private or is_mentioned:
            if sender_id not in afk_responded_users:
                await event.reply(f"Şu anda AFK modundayım. Sebep: {afk_reason}")
                afk_responded_users.add(sender_id)

# Filtre Komutları
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
        await event.reply("Bu kelimeye ait filtre bulunamadı.")

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
        await event.reply("Bu kelimeye ait genel filtre bulunamadı.")

# Filtrelere tepki verme
@client.on(events.NewMessage())
async def filter_response(event):
    text_lower = event.raw_text.lower()

    # Öncelikle genel filtre kontrolü (her yerde)
    for keyword, response in all_filtered_messages.items():
        if keyword in text_lower:
            await event.reply(response)
            return

    # Özel mesajlarda özel filtre kontrolü
    if event.is_private:
        for keyword, response in filtered_messages.items():
            if keyword in text_lower:
                await event.reply(response)
                return

# Kişisel Komutlar (.ekle, .sil, ve çalıştırma)
custom_commands = {}

def save_custom_commands():
    with open("custom_commands.json", "w") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)

def load_custom_commands():
    global custom_commands
    if os.path.exists("custom_commands.json"):
        with open("custom_commands.json", "r") as f:
            custom_commands = json.load(f)

load_custom_commands()

@client.on(events.NewMessage(pattern=r"^.ekle (\.\S+) (.+)"))
async def add_custom_command(event):
    cmd = event.pattern_match.group(1)
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    save_custom_commands()
    await event.reply(f"Kişisel komut eklendi: {cmd} → {reply}")

@client.on(events.NewMessage(pattern=r"^.sil (\.\S+)"))
async def del_custom_command(event):
    cmd = event.pattern_match.group(1)
    if cmd in custom_commands:
        del custom_commands[cmd]
        save_custom_commands()
        await event.reply(f"Kişisel komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    if event.raw_text.strip() in custom_commands:
        reply = custom_commands[event.raw_text.strip()]
        # Eğer kod formatı varsa kod bloğu içinde gönder
        if reply.startswith("```") and reply.endswith("```"):
            await event.reply(reply, parse_mode='md')
        else:
            await event.reply(reply)

# Karşılama Mesajı Komutları
@client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?"))
async def welcome_handler(event):
    global welcome_message, welcome_active
    arg = event.pattern_match.group(1)
    if arg:
        welcome_message = arg
        welcome_active = True
        save_welcome()
        await event.reply(f"Karşılama mesajı ayarlandı ve aktif edildi:\n{welcome_message}")
    else:
        if welcome_message:
            welcome_active = True
            save_welcome()
            await event.reply("Karşılama mesajı tekrar aktif edildi.")
        else:
            await event.reply("Önce bir karşılama mesajı ayarlamalısınız, örn: .welcome Hoş geldin!")

@client.on(events.NewMessage(pattern=r"^.unwelcome$"))
async def unwelcome_handler(event):
    global welcome_active
    welcome_active = False
    save_welcome()
    await event.reply("Karşılama mesajı kapatıldı.")

# Karşılama mesajı gönderme (özel mesajlarda ilk mesaj)
welcomed_users = set()

@client.on(events.NewMessage())
async def welcome_send(event):
    global welcome_active, welcome_message, welcomed_users
    if not welcome_active or not welcome_message:
        return
    if not event.is_private:
        return
    sender = event.sender_id
    if sender in welcomed_users:
        return
    welcomed_users.add(sender)
    await event.reply(welcome_message)

# Yönetici / Sahip komutları
def is_owner(user_id):
    return user_id == admin_id

def is_owner_or_admin(user_id):
    # Burada sadece sahip = admin_id var, istenirse başka adminler eklenebilir.
    return user_id == admin_id

@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    if not is_owner_or_admin(event.sender_id):
        return
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    if not is_owner_or_admin(event.sender_id):
        return
    if not event.is_group:
        await event.reply("Bu komut sadece gruplarda çalışır.")
        return
    user = None
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except:
            await event.reply("Kullanıcı bulunamadı.")
            return
    else:
        await event.reply("Kicklemek için kullanıcı belirtmelisin.")
        return
    await event.chat.kick_participant(user.id)
    await event.reply(f"{user.first_name} gruptan atıldı.")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    if not is_owner_or_admin(event.sender_id):
        return
    if not event.is_group:
        await event.reply("Bu komut sadece gruplarda çalışır.")
        return
    user = None
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except:
            await event.reply("Kullanıcı bulunamadı.")
            return
    else:
        await event.reply("Banlamak için kullanıcı belirtmelisin.")
        return
    await client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
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

async def main():
    print("JudgeUserBot çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
