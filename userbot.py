import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events, Button
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
from telethon.errors.rpcerrorlist import UserAdminInvalidError
from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
afk_replied_users = set()

filtered_messages_private = {}
filtered_messages_all = {}

custom_commands = {}

WELCOME_MESSAGE = None
welcome_enabled = False

def save_filtered():
    with open("filtered_private.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages_private, f, ensure_ascii=False, indent=2)

def save_all_filtered():
    with open("filtered_all.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages_all, f, ensure_ascii=False, indent=2)

def save_custom_commands():
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)

def save_welcome():
    global WELCOME_MESSAGE, welcome_enabled
    with open("welcome.json", "w", encoding="utf-8") as f:
        json.dump({"enabled": welcome_enabled, "message": WELCOME_MESSAGE}, f, ensure_ascii=False, indent=2)

def load_all():
    global filtered_messages_private, filtered_messages_all, custom_commands, WELCOME_MESSAGE, welcome_enabled
    if os.path.exists("filtered_private.json"):
        with open("filtered_private.json", "r", encoding="utf-8") as f:
            filtered_messages_private = json.load(f)
    if os.path.exists("filtered_all.json"):
        with open("filtered_all.json", "r", encoding="utf-8") as f:
            filtered_messages_all = json.load(f)
    if os.path.exists("custom_commands.json"):
        with open("custom_commands.json", "r", encoding="utf-8") as f:
            custom_commands = json.load(f)
    if os.path.exists("welcome.json"):
        with open("welcome.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            welcome_enabled = data.get("enabled", False)
            WELCOME_MESSAGE = data.get("message", None)

def parse_command_arg(text):
    # Komut ve argümanları ayrıştırırken tırnak içindekini bir bütün alır
    # Örnek input: '.filter iban "uzun metin burada \n yeni satır"'
    # Döner: ('iban', 'uzun metin burada \n yeni satır')

    parts = text.strip().split(' ', 2)
    if len(parts) < 3:
        return None, None

    keyword = parts[1].lower()

    rest = parts[2].strip()

    # Tırnak içindeki metni yakala (çift ya da tek tırnak)
    m = re.match(r'^["\'](.*)["\']$', rest, flags=re.DOTALL)
    if m:
        value = m.group(1)
    else:
        value = rest

    return keyword, value

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
        ".filter <kelime> \"cevap\" - Özel mesajlarda otomatik yanıt ekler.\n"
        ".allfilter <kelime> \"cevap\" - Her yerde otomatik yanıt ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".unallfilter <kelime> - Tüm filtreyi kaldırır.\n"
        ".ekle <.komut> \"cevap\" - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar (bot sahibi).\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar (bot sahibi).\n"
        ".eval <kod> - Yalnızca admin çalıştırabilir.\n"
        ".wlive - Sadece owner kullanabilir.\n"
        ".welcome <mesaj> - Karşılama mesajını ayarlar ve aktif eder.\n"
        ".unwelcome - Karşılama mesajını kapatır."
    )
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    if event.pattern_match.group(1):
        afk_reason = event.pattern_match.group(1)
    else:
        afk_reason = "AFK"
    afk_mode = True
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
    # Özel mesaj veya grupta etiketlendiğinde
    if event.is_private or (event.is_group and event.is_reply):
        sender = event.sender_id
        if sender == (await event.client.get_me()).id:
            return
        if sender not in afk_replied_users:
            await event.reply(f"Şu anda AFK'yım. Sebep: {afk_reason}")
            afk_replied_users.add(sender)

@client.on(events.NewMessage(pattern=r"^.filter (.+)", func=lambda e: e.is_private))
async def filter_add(event):
    keyword, response = parse_command_arg(event.raw_text)
    if not keyword or not response:
        await event.reply("Kullanım: .filter <kelime> \"cevap\" (cevap tırnak içinde olabilir)")
        return
    filtered_messages_private[keyword] = response
    save_filtered()
    await event.reply(f"Özel mesaj filtresi eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.allfilter (.+)"))
async def allfilter_add(event):
    keyword, response = parse_command_arg(event.raw_text)
    if not keyword or not response:
        await event.reply("Kullanım: .allfilter <kelime> \"cevap\" (cevap tırnak içinde olabilir)")
        return
    filtered_messages_all[keyword] = response
    save_all_filtered()
    await event.reply(f"Tüm sohbetler için filtre eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.unfilter (.+)", func=lambda e: e.is_private))
async def unfilter_remove(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages_private:
        del filtered_messages_private[keyword]
        save_filtered()
        await event.reply(f"Özel mesaj filtresi kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait özel mesaj filtresi bulunamadı.")

@client.on(events.NewMessage(pattern=r"^.unallfilter (.+)"))
async def unallfilter_remove(event):
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages_all:
        del filtered_messages_all[keyword]
        save_all_filtered()
        await event.reply(f"Tüm sohbetlerden filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait genel filtre bulunamadı.")

@client.on(events.NewMessage())
async def filter_response(event):
    # Özel mesaj filtresi
    if event.is_private:
        text_lower = event.raw_text.lower()
        for keyword, response in filtered_messages_private.items():
            if keyword.lower() in text_lower:
                await event.reply(response)
                return
    # Genel filtre (gruplar ve özel her yerde)
    text_lower = event.raw_text.lower()
    for keyword, response in filtered_messages_all.items():
        if keyword.lower() in text_lower:
            await event.reply(response)
            return

@client.on(events.NewMessage(pattern=r"^.ekle (.+)", func=lambda e: e.is_private))
async def add_custom_command(event):
    cmd, reply = parse_command_arg(event.raw_text)
    if not cmd or not reply:
        await event.reply("Kullanım: .ekle <.komut> \"cevap\" (cevap tırnak içinde olabilir)")
        return
    custom_commands[cmd] = reply
    save_custom_commands()
    await event.reply(f"Kişisel komut eklendi: {cmd} → {reply}")

@client.on(events.NewMessage(pattern=r"^.sil (.+)", func=lambda e: e.is_private))
async def del_custom_command(event):
    cmd = event.pattern_match.group(1)
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
        await event.reply(custom_commands[text])

@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    # restart sadece bot sahibi veya admin için değil, herkese açık olsun
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    # Sadece bot sahibi kullanabilir
    if event.sender_id != admin_id:
        return
    if event.is_group or event.is_channel:
        try:
            if event.is_reply:
                user = await event.get_reply_message().get_sender()
            elif event.pattern_match.group(1):
                user = await client.get_entity(event.pattern_match.group(1))
            else:
                return await event.reply("Kicklemek için kullanıcı belirtmelisin.")
            await event.chat.kick_participant(user.id)
            await event.reply(f"{user.first_name} gruptan atıldı.")
        except UserAdminInvalidError:
            await event.reply("Bu kullanıcıyı atmaya yetkim yok.")
        except Exception as e:
            await event.reply(f"Hata: {str(e)}")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    # Sadece bot sahibi kullanabilir
    if event.sender_id != admin_id:
        return
    if event.is_group or event.is_channel:
        try:
            if event.is_reply:
                user = await event.get_reply_message().get_sender()
            elif event.pattern_match.group(1):
                user = await client.get_entity(event.pattern_match.group(1))
            else:
                return await event.reply("Banlamak için kullanıcı belirtmelisin.")
            banned_rights = ChatBannedRights(until_date=None, view_messages=True)
            await client(EditBannedRequest(event.chat_id, user.id, banned_rights))
            await event.reply(f"{user.first_name} gruptan banlandı.")
        except UserAdminInvalidError:
            await event.reply("Bu kullanıcıyı banlamaya yetkim yok.")
        except Exception as e:
            await event.reply(f"Hata: {str(e)}")

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
    global WELCOME_MESSAGE, welcome_enabled
    if event.pattern_match.group(1):
        WELCOME_MESSAGE = event.pattern_match.group(1)
        welcome_enabled = True
        save_welcome()
        await event.reply(f"Karşılama mesajı ayarlandı ve aktif edildi:\n\n{WELCOME_MESSAGE}")
    else:
        if welcome_enabled and WELCOME_MESSAGE:
            await event.reply(f"Mevcut karşılama mesajı:\n\n{WELCOME_MESSAGE}")
        else:
            await event.reply("Karşılama mesajı ayarlanmamış veya kapalı.")

@client.on(events.NewMessage(pattern=r"^.unwelcome$"))
async def unwelcome_handler(event):
    global welcome_enabled
    welcome_enabled = False
    save_welcome()
    await event.reply("Karşılama mesajı devre dışı bırakıldı.")

@client.on(events.ChatAction)
async def welcome_new_user(event):
    global welcome_enabled, WELCOME_MESSAGE
    if welcome_enabled and WELCOME_MESSAGE:
        if event.user_added or event.user_joined:
            try:
                await event.reply(WELCOME_MESSAGE)
            except:
                pass

async def main():
    load_all()
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
