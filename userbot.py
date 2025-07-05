import asyncio
import os
import json
import re
import sys
from telethon import TelegramClient, events, errors
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

welcome_active = False
welcome_message = ""
welcomed_users = set()

# Veri yükleme fonksiyonu
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Veri kaydetme fonksiyonu
def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def main():
    global afk_mode, afk_reason, afk_replied_users
    global filtered_messages, all_filtered_messages
    global custom_commands
    global welcome_active, welcome_message, welcomed_users
    global me_id

    await client.start()
    me = await client.get_me()
    me_id = me.id

    # Load data
    filtered_messages = load_json("filtered_messages.json")
    all_filtered_messages = load_json("all_filtered_messages.json")
    custom_commands = load_json("custom_commands.json")
    welcomed_users = set(load_json("welcomed_users.json").get("users", []))

    print("JudgeUserBot çalışıyor...")

    # --- Komutlar ---

    # .alive
    @client.on(events.NewMessage(pattern=r"^.alive$", func=lambda e: e.sender_id == me_id))
    async def alive_handler(event):
        await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {me.first_name} ❤️\n\nBot Versiyonu: v1.0")

    # .wlive sadece admin
    @client.on(events.NewMessage(pattern=r"^.wlive$", func=lambda e: e.sender_id == admin_id))
    async def wlive_handler(event):
        await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

    # .judge komut listesi
    @client.on(events.NewMessage(pattern=r"^.judge$", func=lambda e: e.sender_id == me_id))
    async def judge_help(event):
        help_text = (
            "Judge Userbot Komutları v1.0:\n\n"
            ".alive - Botun çalıştığını kontrol eder.\n"
            ".afk <sebep> - AFK moduna geçer.\n"
            ".back - AFK modundan çıkar.\n"
            ".filter <kelime> <cevap> - Özel mesajlarda geçerli filtre ekler.\n"
            ".allfilter <kelime> <cevap> - Her yerde geçerli filtre ekler.\n"
            ".unfilter <kelime> - Özel mesaj filtresini kaldırır.\n"
            ".unallfilter <kelime> - Her yerdeki filtreyi kaldırır.\n"
            ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
            ".sil <.komut> - Kişisel komutu siler.\n"
            ".welcome <mesaj> - Karşılama mesajını ayarlar ve aktif eder.\n"
            ".unwelcome - Karşılama mesajını kapatır.\n"
            ".back - AFK modundan çıkar.\n"
            ".restart - Botu yeniden başlatır.\n"
            ".kick <id veya reply> - Kullanıcıyı gruptan atar (bot sahibi kullanabilir).\n"
            ".ban <id veya reply> - Kullanıcıyı gruptan banlar (bot sahibi kullanabilir).\n"
            ".eval <kod> - Yalnızca admin çalıştırabilir.\n"
            ".wlive - Global admin için sistem durumu."
        )
        await event.reply(help_text)

    # .afk <sebep>
    @client.on(events.NewMessage(pattern=r"^.afk (.+)", func=lambda e: e.sender_id == me_id))
    async def afk_handler(event):
        nonlocal afk_mode, afk_reason, afk_replied_users
        afk_mode = True
        afk_reason = event.pattern_match.group(1)
        afk_replied_users.clear()
        await event.edit(f"AFK moduna geçildi, sebep: {afk_reason}")

    # .back
    @client.on(events.NewMessage(pattern=r"^.back$", func=lambda e: e.sender_id == me_id))
    async def back_handler(event):
        nonlocal afk_mode, afk_reason, afk_replied_users
        afk_mode = False
        afk_reason = ""
        afk_replied_users.clear()
        await event.edit("Tekrar aktif oldum!")

    # AFK otomatik cevap (özel mesajlarda her kullanıcıya sadece 1 kere)
    @client.on(events.NewMessage(func=lambda e: afk_mode and e.sender_id != me_id))
    async def afk_auto_reply(event):
        if event.is_private:
            if event.sender_id not in afk_replied_users:
                await event.reply(f"Şu anda AFK modundayım. Sebep: {afk_reason}")
                afk_replied_users.add(event.sender_id)
        elif event.is_group or event.is_channel:
            if event.message.mentioned or (event.is_reply and (await event.get_reply_message()).sender_id == me_id):
                if event.sender_id not in afk_replied_users:
                    await event.reply(f"Şu anda AFK modundayım. Sebep: {afk_reason}")
                    afk_replied_users.add(event.sender_id)

    # .filter (özel mesajlar için, büyük-küçük harf duyarsız, tüm metni alır)
    @client.on(events.NewMessage(pattern=r"^.filter (\S+) (.+)", func=lambda e: e.is_private and e.sender_id == me_id))
    async def filter_add(event):
        keyword = event.pattern_match.group(1).lower()
        response = event.pattern_match.group(2)
        filtered_messages[keyword] = response
        save_json("filtered_messages.json", filtered_messages)
        await event.reply(f"Özel mesaj filtresi eklendi: {keyword}")

    # .unfilter (özel mesaj filtresi kaldırma)
    @client.on(events.NewMessage(pattern=r"^.unfilter (\S+)", func=lambda e: e.is_private and e.sender_id == me_id))
    async def filter_remove(event):
        keyword = event.pattern_match.group(1).lower()
        if keyword in filtered_messages:
            del filtered_messages[keyword]
            save_json("filtered_messages.json", filtered_messages)
            await event.reply(f"Özel mesaj filtresi kaldırıldı: {keyword}")
        else:
            await event.reply("Bu kelimeye ait filtre bulunamadı.")

    # .allfilter (her yerde geçerli)
    @client.on(events.NewMessage(pattern=r"^.allfilter (\S+) (.+)", func=lambda e: e.sender_id == me_id))
    async def allfilter_add(event):
        keyword = event.pattern_match.group(1).lower()
        response = event.pattern_match.group(2)
        all_filtered_messages[keyword] = response
        save_json("all_filtered_messages.json", all_filtered_messages)
        await event.reply(f"Tüm sohbetlerde geçerli filtre eklendi: {keyword}")

    # .unallfilter (her yerde geçerli filtre kaldırma)
    @client.on(events.NewMessage(pattern=r"^.unallfilter (\S+)", func=lambda e: e.sender_id == me_id))
    async def allfilter_remove(event):
        keyword = event.pattern_match.group(1).lower()
        if keyword in all_filtered_messages:
            del all_filtered_messages[keyword]
            save_json("all_filtered_messages.json", all_filtered_messages)
            await event.reply(f"Tüm sohbetlerde geçerli filtre kaldırıldı: {keyword}")
        else:
            await event.reply("Bu kelimeye ait filtre bulunamadı.")

    # .ekle <.komut> <cevap>
    @client.on(events.NewMessage(pattern=r"^.ekle (\.\S+) (.+)", func=lambda e: e.sender_id == me_id))
    async def add_command(event):
        cmd = event.pattern_match.group(1)
        reply = event.pattern_match.group(2)
        custom_commands[cmd] = reply
        save_json("custom_commands.json", custom_commands)
        await event.reply(f"Kişisel komut eklendi: {cmd}")

    # .sil <.komut>
    @client.on(events.NewMessage(pattern=r"^.sil (\.\S+)", func=lambda e: e.sender_id == me_id))
    async def del_command(event):
        cmd = event.pattern_match.group(1)
        if cmd in custom_commands:
            del custom_commands[cmd]
            save_json("custom_commands.json", custom_commands)
            await event.reply(f"Kişisel komut silindi: {cmd}")
        else:
            await event.reply("Böyle bir komut bulunamadı.")

    # Custom komutları yakala
    @client.on(events.NewMessage(func=lambda e: e.sender_id == me_id))
    async def custom_command_handler(event):
        text = event.raw_text.strip()
        if text in custom_commands:
            await event.reply(custom_commands[text])

    # .welcome <mesaj>
    @client.on(events.NewMessage(pattern=r"^.welcome(?: (.+))?", func=lambda e: e.sender_id == me_id))
    async def welcome_set(event):
        nonlocal welcome_active, welcome_message, welcomed_users
        arg = event.pattern_match.group(1)
        if arg:
            welcome_message = arg
            welcome_active = True
            save_json("welcome.json", {"active": welcome_active, "message": welcome_message})
            await event.reply("Karşılama mesajı ayarlandı ve aktif edildi.")
        else:
            if welcome_active and welcome_message:
                await event.reply(f"Mevcut karşılama mesajı:\n{welcome_message}")
            else:
                await event.reply("Karşılama mesajı ayarlanmadı.")

    # .unwelcome
    @client.on(events.NewMessage(pattern=r"^.unwelcome$", func=lambda e: e.sender_id == me_id))
    async def welcome_unset(event):
        nonlocal welcome_active, welcome_message, welcomed_users
        welcome_active = False
        welcome_message = ""
        welcomed_users.clear()
        save_json("welcome.json", {"active": welcome_active, "message": welcome_message})
        save_json("welcomed_users.json", {"users": list(welcomed_users)})
        await event.edit("Karşılama mesajı kapatıldı.")

    # Özelden gelen yeni mesajda karşılama mesajı gönder (sadece 1 kere kişiye)
    @client.on(events.NewMessage(func=lambda e: e.is_private and welcome_active and e.sender_id != me_id))
    async def welcome_message_send(event):
        nonlocal welcomed_users
        if event.sender_id not in welcomed_users:
            await event.reply(welcome_message)
            welcomed_users.add(event.sender_id)
            save_json("welcomed_users.json", {"users": list(welcomed_users)})

    # Filtreli mesajlara cevap (özel mesajlar için)
    @client.on(events.NewMessage(func=lambda e: e.is_private and e.sender_id != me_id))
    async def filtered_response(event):
        text = event.raw_text.lower()
        for keyword, response in filtered_messages.items():
            if keyword in text:
                await event.reply(response)
                return
        for keyword, response in all_filtered_messages.items():
            if keyword in text:
                await event.reply(response)
                return

    # .restart (botu yeniden başlatır, bot sahibi kullanabilir)
    @client.on(events.NewMessage(pattern=r"^.restart$", func=lambda e: e.sender_id == me_id))
    async def restart_handler(event):
        await event.reply("♻️ Bot yeniden başlatılıyor...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # .kick (bot sahibi kullanabilir)
    @client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?", func=lambda e: e.sender_id == me_id))
    async def kick_user(event):
        if event.is_group or event.is_channel:
            if event.is_reply:
                user = await event.get_reply_message().get_sender()
            elif event.pattern_match.group(1):
                user = await client.get_entity(event.pattern_match.group(1))
            else:
                return await event.reply("Kicklemek için kullanıcı belirt.")
            try:
                await event.chat.kick_participant(user.id)
                await event.reply(f"{user.first_name} gruptan atıldı.")
            except errors.rpcerrorlist.ChatAdminRequiredError:
                await event.reply("Bu işlemi yapmak için admin yetkisine ihtiyacım var.")

    # .ban (bot sahibi kullanabilir)
    @client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?", func=lambda e: e.sender_id == me_id))
    async def ban_user(event):
        if event.is_group or event.is_channel:
            if event.is_reply:
                user = await event.get_reply_message().get_sender()
            elif event.pattern_match.group(1):
                user = await client.get_entity(event.pattern_match.group(1))
            else:
                return await event.reply("Banlamak için kullanıcı belirt.")
            try:
                await client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
                await event.reply(f"{user.first_name} gruptan banlandı.")
            except errors.rpcerrorlist.ChatAdminRequiredError:
                await event.reply("Bu işlemi yapmak için admin yetkisine ihtiyacım var.")

    # .eval (sadece admin)
    @client.on(events.NewMessage(pattern=r"^.eval (.+)", func=lambda e: e.sender_id == admin_id))
    async def eval_handler(event):
        code = event.pattern_match.group(1)
        try:
            result = eval(code)
            await event.reply(str(result))
        except Exception as e:
            await event.reply(f"Hata: {str(e)}")

    # Genel filtre (tüm mesajlarda allfilter için)
    @client.on(events.NewMessage(func=lambda e: e.sender_id != me_id))
    async def allfilter_response(event):
        text = event.raw_text.lower()
        for keyword, response in all_filtered_messages.items():
            if keyword in text:
                await event.reply(response)
                return

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
