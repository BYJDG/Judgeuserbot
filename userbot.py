import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id, owners_ids  # owners_ids: bot sahibi user_id listesi

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
filtered_messages = {}
all_filtered_messages = {}
custom_commands = {}
welcome_message = None  # Karşılama mesajı, başlangıçta yok

# Kullanıcıya bir kez afk mesajı için setler (private ve grup ayrı tutuluyor)
afk_replied_private = set()
afk_replied_group = set()

# Load saved data if exists
if os.path.exists("filtered_messages.json"):
    with open("filtered_messages.json", "r", encoding="utf-8") as f:
        filtered_messages = json.load(f)

if os.path.exists("all_filtered_messages.json"):
    with open("all_filtered_messages.json", "r", encoding="utf-8") as f:
        all_filtered_messages = json.load(f)

if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r", encoding="utf-8") as f:
        custom_commands = json.load(f)

if os.path.exists("welcome_message.json"):
    with open("welcome_message.json", "r", encoding="utf-8") as f:
        welcome_message = json.load(f).get("message")

# --- Komutlar ---

# .alive
@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

# .wlive (sadece owner/admin)
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
        ".filter <kelime> <cevap> - Özel mesajlarda filtreli otomatik cevap ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".allfilter <kelime> <cevap> - Her yerde geçerli global filtre ekler.\n"
        ".unallfilter <kelime> - Global filtreyi kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar. (Bot sahibi veya yetkililer)\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar. (Bot sahibi veya yetkililer)\n"
        ".eval <kod> - Yalnızca owner çalıştırabilir.\n"
        ".wlive - Owner için sistem durumu.\n"
        ".welcome <mesaj> - Karşılama mesajı ayarla (bot sahibi veya yetkili)\n"
    )
    await event.reply(help_text)

# .afk <sebep>
@client.on(events.NewMessage(pattern=r"^.afk(?: (.+))?"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_private, afk_replied_group
    afk_mode = True
    afk_reason = event.pattern_match.group(1) if event.pattern_match.group(1) else "AFK modundayım."
    afk_replied_private.clear()
    afk_replied_group.clear()
    await event.edit(f"AFK moduna geçildi. Sebep: {afk_reason}")

# .back
@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_replied_private, afk_replied_group
    afk_mode = False
    afk_reason = ""
    afk_replied_private.clear()
    afk_replied_group.clear()
    await event.edit("Tekrar aktif oldum!")

# AFK otomatik cevap (her kullanıcıya özel mesaj ve grup için farklı mantık)
@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason
    me = await client.get_me()
    if not afk_mode:
        return
    if event.sender_id == me.id:
        return

    # Özel mesajlarda
    if event.is_private:
        if event.sender_id not in afk_replied_private:
            await event.reply(f"Şuan AFK'yım. Sebep: {afk_reason}")
            afk_replied_private.add(event.sender_id)
    # Gruplarda
    elif event.is_group or event.is_channel:
        # Sadece bot mention veya reply ise yanıtla
        is_mentioned = False
        if event.message.mentioned or (event.is_reply and (await event.get_reply_message()).sender_id == me.id):
            is_mentioned = True

        if is_mentioned and event.sender_id not in afk_replied_group:
            await event.reply(f"Şuan AFK'yım. Sebep: {afk_reason}")
            afk_replied_group.add(event.sender_id)

# .filter komutu - sadece özel mesajlarda filtre ekle
@client.on(events.NewMessage(pattern=r"^.filter "))
async def filter_handler(event):
    if not event.is_private:
        return
    text = event.raw_text
    parts = text.split(" ", 2)
    if len(parts) < 3:
        return await event.reply("Kullanım: .filter <kelime> <cevap>")
    keyword = parts[1].casefold()
    response = parts[2]
    filtered_messages[keyword] = response
    with open("filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
    await event.reply(f"Özel filtre eklendi: {keyword} → {response}")

# .allfilter komutu - her yerde geçerli global filtre ekle
@client.on(events.NewMessage(pattern=r"^.allfilter "))
async def allfilter_handler(event):
    text = event.raw_text
    parts = text.split(" ", 2)
    if len(parts) < 3:
        return await event.reply("Kullanım: .allfilter <kelime> <cevap>")
    keyword = parts[1].casefold()
    response = parts[2]
    all_filtered_messages[keyword] = response
    with open("all_filtered_messages.json", "w", encoding="utf-8") as f:
        json.dump(all_filtered_messages, f, ensure_ascii=False, indent=2)
    await event.reply(f"Global filtre eklendi: {keyword} → {response}")

# .unfilter komutu - özel mesaj filtresini kaldır
@client.on(events.NewMessage(pattern=r"^.unfilter "))
async def unfilter_handler(event):
    if not event.is_private:
        return
    keyword = event.raw_text.split(" ", 1)[1].casefold()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        with open("filtered_messages.json", "w", encoding="utf-8") as f:
            json.dump(filtered_messages, f, ensure_ascii=False, indent=2)
        await event.reply(f"Özel filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait özel filtre bulunamadı.")

# .unallfilter komutu - global filtreyi kaldır
@client.on(events.NewMessage(pattern=r"^.unallfilter "))
async def unallfilter_handler(event):
    keyword = event.raw_text.split(" ", 1)[1].casefold()
    if keyword in all_filtered_messages:
        del all_filtered_messages[keyword]
        with open("all_filtered_messages.json", "w", encoding="utf-8") as f:
            json.dump(all_filtered_messages, f, ensure_ascii=False, indent=2)
        await event.reply(f"Global filtre kaldırıldı: {keyword}")
    else:
        await event.reply("Bu kelimeye ait global filtre bulunamadı.")

# Filtrelere göre cevap ver (öncelik global, sonra özel - büyük/küçük harfe duyarsız)
@client.on(events.NewMessage())
async def filter_response(event):
    text_cf = event.raw_text.casefold()
    # Global filtre kontrolü
    for keyword, response in all_filtered_messages.items():
        if keyword in text_cf:
            await event.reply(response)
            return
    # Özel mesaj filtre kontrolü
    if event.is_private:
        for keyword, response in filtered_messages.items():
            if keyword in text_cf:
                await event.reply(response)
                return

# .ekle komutu - kişisel komut ekle
@client.on(events.NewMessage(pattern=r"^.ekle "))
async def add_command(event):
    text = event.raw_text
    parts = text.split(" ", 2)
    if len(parts) < 3:
        return await event.reply("Kullanım: .ekle <.komut> <cevap>")
    cmd = parts[1]
    reply = parts[2]
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w", encoding="utf-8") as f:
        json.dump(custom_commands, f, ensure_ascii=False, indent=2)
    await event.reply(f"Komut eklendi: {cmd} → {reply}")

# .sil komutu - kişisel komut sil
@client.on(events.NewMessage(pattern=r"^.sil "))
async def del_command(event):
    cmd = event.raw_text.split(" ", 1)[1]
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w", encoding="utf-8") as f:
            json.dump(custom_commands, f, ensure_ascii=False, indent=2)
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

# Kişisel komutları yakala ve cevapla
@client.on(events.NewMessage())
async def custom_command_handler(event):
    txt = event.raw_text.strip()
    if txt in custom_commands:
        msg = custom_commands[txt]
        # Kod bloğu varsa, kod olarak gönder
        if msg.startswith("```") and msg.endswith("```"):
            await event.reply(msg, parse_mode='md')
        else:
            await event.reply(msg)

# .restart komutu (bot sahibi veya yetkililer)
@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    if event.sender_id not in owners_ids:
        return await event.reply("Bu komutu kullanmaya yetkiniz yok.")
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# .kick komutu (bot sahibi veya yetkililer)
@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    if event.sender_id not in owners_ids:
        return await event.reply("Bu komutu kullanmaya yetkiniz yok.")
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda kullanılabilir.")
    user = None
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except Exception:
            return await event.reply("Kullanıcı bulunamadı.")
    else:
        return await event.reply("Kicklemek için kullanıcı belirtmelisin.")
    try:
        await event.chat.kick_participant(user.id)
        await event.reply(f"{user.first_name} gruptan atıldı.")
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")

# .ban komutu (bot sahibi veya yetkililer)
@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban_user(event):
    if event.sender_id not in owners_ids:
        return await event.reply("Bu komutu kullanmaya yetkiniz yok.")
    if not event.is_group:
        return await event.reply("Bu komut sadece gruplarda kullanılabilir.")
    user = None
    if event.is_reply:
        user = await event.get_reply_message().get_sender()
    elif event.pattern_match.group(1):
        try:
            user = await client.get_entity(event.pattern_match.group(1))
        except Exception:
            return await event.reply("Kullanıcı bulunamadı.")
    else:
        return await event.reply("Banlamak için kullanıcı belirtmelisin.")
    try:
        await client(EditBannedRequest(
            event.chat_id,
            user.id,
            ChatBannedRights(until_date=None, view_messages=True)
        ))
        await event.reply(f"{user.first_name} gruptan banlandı.")
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")

# .eval komutu (sadece owner)
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

# .welcome komutu (bot sahibi veya yetkililer)
@client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?"))
async def welcome_handler(event):
    global welcome_message
    if event.sender_id not in owners_ids:
        return await event.reply("Bu komutu kullanmaya yetkiniz yok.")
    text = event.pattern_match.group(1)
    if not text:
        welcome_message = None
        if os.path.exists("welcome_message.json"):
            os.remove("welcome_message.json")
        await event.reply("Karşılama mesajı kaldırıldı.")
    else:
        welcome_message = text
        with open("welcome_message.json", "w", encoding="utf-8") as f:
            json.dump({"message": welcome_message}, f, ensure_ascii=False, indent=2)
        await event.reply(f"Karşılama mesajı ayarlandı:\n{welcome_message}")

# Yeni üye katıldığında karşılama mesajı gönder (gruplarda)
@client.on(events.ChatAction())
async def welcome_new_member(event):
    global welcome_message
    if welcome_message is None:
        return
    if event.user_joined or event.user_added:
        if event.user and event.chat:
            try:
                await event.reply(welcome_message)
            except Exception:
                pass

# Ana async fonksiyon
async def main():
    await client.start()
    print("JudgeUserBot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
