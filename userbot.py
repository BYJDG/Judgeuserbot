import asyncio
import os
import sys
import json
import re
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from config import api_id, api_hash, session_name, admin_id  # admin_id: global admin kullanıcı id'si

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False
afk_reason = ""
afk_users_replied = set()

filtered_messages = {}
all_filtered_messages = {}
custom_commands = {}

# Dosyaya kayıt yükleme fonksiyonları
def save_filtered():
    with open("filtered_messages.json", "w") as f:
        json.dump(filtered_messages, f)

def load_filtered():
    global filtered_messages
    if os.path.exists("filtered_messages.json"):
        with open("filtered_messages.json", "r") as f:
            filtered_messages = json.load(f)

def save_all_filtered():
    with open("all_filtered_messages.json", "w") as f:
        json.dump(all_filtered_messages, f)

def load_all_filtered():
    global all_filtered_messages
    if os.path.exists("all_filtered_messages.json"):
        with open("all_filtered_messages.json", "r") as f:
            all_filtered_messages = json.load(f)

def save_custom_commands():
    with open("custom_commands.json", "w") as f:
        json.dump(custom_commands, f)

def load_custom_commands():
    global custom_commands
    if os.path.exists("custom_commands.json"):
        with open("custom_commands.json", "r") as f:
            custom_commands = json.load(f)

load_filtered()
load_all_filtered()
load_custom_commands()

@client.on(events.NewMessage(pattern=r"^.alive$"))
async def alive_handler(event):
    sender = await event.client.get_me()
    await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"^.wlive$"))
async def wlive_handler(event):
    if event.sender_id != admin_id:
        return await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")
    else:
        await event.reply("Owner olarak bu komutu kullandın. Bot sorunsuz çalışıyor.")

@client.on(events.NewMessage(pattern=r"^.judge$"))
async def judge_help(event):
    help_text = (
        "Judge Userbot Komutları v1.0:\n\n"
        ".alive - Botun çalıştığını kontrol eder.\n"
        ".afk <sebep> - AFK moduna geçer.\n"
        ".back - AFK modundan çıkar.\n"
        ".filter <kelime> <cevap> - Özel mesajda otomatik yanıt ekler.\n"
        ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
        ".allfilter <kelime> <cevap> - Genel filtre ekler (her yerde geçerli).\n"
        ".unallfilter <kelime> - Genel filtreyi kaldırır.\n"
        ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
        ".sil <.komut> - Kişisel komutu siler.\n"
        ".restart - Botu yeniden başlatır.\n"
        ".kick <id veya reply> - Kullanıcıyı gruptan atar (bot sahibi ve adminler kullanabilir).\n"
        ".ban <id veya reply> - Kullanıcıyı gruptan banlar (bot sahibi ve adminler kullanabilir).\n"
        ".eval <kod> - Yalnızca owner (admin_id) çalıştırabilir.\n"
        ".wlive - Owner komutu, bot durumu gösterir."
    )
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^.afk (.+)"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_users_replied
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    afk_users_replied = set()
    await event.edit(f"AFK moduna geçtin. Sebep: {afk_reason}")

@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_users_replied
    afk_mode = False
    afk_reason = ""
    afk_users_replied = set()
    await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason, afk_users_replied
    if not afk_mode:
        return

    sender_id = event.sender_id
    me = await client.get_me()
    if sender_id == me.id:
        return  # Kendine cevap verme

    # Özel mesaj veya gruplarda bahsetme/reply durumlarında cevap ver, ama her kullanıcıya bir kere
    if event.is_private or (event.is_group and (event.message.mentioned or event.is_reply)):
        if sender_id not in afk_users_replied:
            await event.reply(f"Şu anda AFK'yım. Sebep: {afk_reason}")
            afk_users_replied.add(sender_id)

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

    # Öncelikle genel filtre kontrolü
    for keyword, response in all_filtered_messages.items():
        if keyword in text_lower:
            await event.reply(response)
            return

    # Özel mesajda ise özel filtreler kontrol edilir
    if event.is_private:
        for keyword, response in filtered_messages.items():
            if keyword in text_lower:
                await event.reply(response)
                return

@client.on(events.NewMessage(pattern=r"^.ekle (\.\S+) (.+)"))
async def add_command(event):
    cmd = event.pattern_match.group(1)
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    save_custom_commands()
    await event.reply(f"Komut eklendi: {cmd} → {reply}")

@client.on(events.NewMessage(pattern=r"^.sil (\.\S+)"))
async def del_command(event):
    cmd = event.pattern_match.group(1)
    if cmd in custom_commands:
        del custom_commands[cmd]
        save_custom_commands()
        await event.reply(f"Komut silindi: {cmd}")
    else:
        await event.reply("Böyle bir komut bulunamadı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    text = event.raw_text.strip()
    if text in custom_commands:
        reply = custom_commands[text]
        # Kod formatında göndermek için markdown (```) kullanabiliriz
        if reply.startswith("```") and reply.endswith("```"):
            await event.reply(reply, parse_mode="md")
        else:
            await event.reply(reply)

@client.on(events.NewMessage(pattern=r"^.restart$"))
async def restart_handler(event):
    # restart komutu bot sahibi ve adminlerin kullanımı için
    if event.sender_id != admin_id:
        return await event.reply("Bu komutu sadece owner kullanabilir.")
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick_user(event):
    # Sadece bot sahibi ve admin kullanabilir
    if event.sender_id != admin_id:
        return await event.reply("Bu komutu sadece owner kullanabilir.")
    if event.is_group:
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
    # Sadece bot sahibi ve admin kullanabilir
    if event.sender_id != admin_id:
        return await event.reply("Bu komutu sadece owner kullanabilir.")
    if event.is_group:
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
        return await event.reply("Bu komutu sadece owner kullanabilir.")
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
