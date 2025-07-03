import os
import sys
import asyncio
import subprocess
from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest

# Config importu (install.sh ile oluşturulan config.py içinden)
from config import api_id, api_hash, session_name, admin_username, admin_id

# Global değişkenler
afk = False
afk_reason = ""
afk_users_replied = set()

client = TelegramClient(session_name, api_id, api_hash)

# -- AFK komutları ve mekanizması --

@client.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?"))
async def set_afk(event):
    global afk, afk_reason, afk_users_replied
    if event.is_private or (event.is_group and event.out):
        afk = True
        afk_reason = event.pattern_match.group(1) or "AFK moduna geçtim."
        afk_users_replied.clear()
        await event.edit(f"AFK moduna aktif. Sebep: {afk_reason}")

@client.on(events.NewMessage(pattern=r"\.back"))
async def back_from_afk(event):
    global afk, afk_reason, afk_users_replied
    if afk:
        afk = False
        afk_reason = ""
        afk_users_replied.clear()
        await event.edit("AFK modundan çıktın, artık aktifsin!")

@client.on(events.NewMessage(pattern=r"\.alive"))
async def alive(event):
    if event.sender_id == (await client.get_me()).id:
        first_name = (await client.get_me()).first_name
        await event.edit(f"Userbotunuz çalışıyor ve sana bişey demek istiyor..\nSeni seviyorum {first_name} ❤️\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"\.wlive"))
async def wlive(event):
    if event.sender_id == admin_id:
        await event.reply("Bot çalışıyor ve her şey yolunda.\nBot Versiyonu: v1.0\n- JudgeUserBot Global Admin Komutu -")
    else:
        await event.reply("Yetkiniz yok!")

@client.on(events.NewMessage(pattern=r"\.judge"))
async def judge_help(event):
    if event.sender_id == (await client.get_me()).id:
        msg = (
            "Judge Userbot Komutları v1.0:\n\n"
            ".alive - Botun çalışıp çalışmadığını kontrol eder.\n"
            ".afk <sebep> - AFK moduna geçer, sebebi belirtir.\n"
            ".back - AFK modundan çıkar.\n"
            ".filter <mesaj> <cevap> - Filtreli otomatik cevap ekler.\n"
            ".unfilter <mesaj> - Filtreyi kaldırır.\n"
            ".judge - Komut listesini gösterir.\n"
            ".ekle <.komut> <cevap> - Kişisel komut ekler.\n"
            ".sil <.komut> - Kişisel komutu siler.\n"
        )
        await event.edit(msg)

# -- Kişisel komutlar için sözlük --
custom_cmds = {}

@client.on(events.NewMessage(pattern=r"\.ekle\s+(\.\S+)\s+(.+)"))
async def add_custom_cmd(event):
    if event.sender_id == (await client.get_me()).id:
        cmd = event.pattern_match.group(1).lower()
        response = event.pattern_match.group(2)
        custom_cmds[cmd] = response
        await event.edit(f"Kişisel komut {cmd} eklendi.")

@client.on(events.NewMessage(pattern=r"\.sil\s+(\.\S+)"))
async def del_custom_cmd(event):
    if event.sender_id == (await client.get_me()).id:
        cmd = event.pattern_match.group(1).lower()
        if cmd in custom_cmds:
            del custom_cmds[cmd]
            await event.edit(f"Kişisel komut {cmd} silindi.")
        else:
            await event.edit(f"{cmd} bulunamadı.")

@client.on(events.NewMessage())
async def custom_command_handler(event):
    if event.sender_id == (await client.get_me()).id:
        text = event.text.lower()
        if text in custom_cmds:
            await event.respond(custom_cmds[text])

# -- AFK kullanıcıya sadece bir kere cevap ver --
@client.on(events.NewMessage(incoming=True))
async def afk_reply(event):
    global afk, afk_reason, afk_users_replied
    if not afk:
        return

    sender = await event.get_sender()
    if sender and sender.bot:
        return  # botlara cevap verme

    # Bot sahibine gelen özel mesajlarda veya gruplarda kendisinden bahsedilince cevap verir
    me = await client.get_me()
    sender_id = event.sender_id

    if event.is_private:
        # Özel mesajda sadece 1 kere cevap ver
        if sender_id not in afk_users_replied:
            await event.reply(f" {afk_reason}")
            afk_users_replied.add(sender_id)
    elif event.is_group or event.is_channel:
        # Grup mesajlarında eğer bot sahibinden bahsediliyorsa
        if me.username and me.username.lower() in event.raw_text.lower():
            if sender_id not in afk_users_replied:
                await event.reply(f" {afk_reason}")
                afk_users_replied.add(sender_id)

# -- Otomatik güncelleme ve restart --

CHECK_INTERVAL = 300  # saniye, 5 dakika

async def auto_update_and_restart():
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        print("[AUTOUPDATE] Repoyu kontrol ediyorum...")
        fetch = subprocess.run(["git", "fetch"], cwd=".", capture_output=True, text=True)
        if fetch.returncode != 0:
            print("[AUTOUPDATE] Git fetch başarısız:", fetch.stderr)
            continue

        local = subprocess.run(["git", "rev-parse", "HEAD"], cwd=".", capture_output=True, text=True)
        remote = subprocess.run(["git", "rev-parse", "origin/main"], cwd=".", capture_output=True, text=True)

        if local.returncode != 0 or remote.returncode != 0:
            print("[AUTOUPDATE] Commit kontrolü yapılamadı.")
            continue

        if local.stdout.strip() != remote.stdout.strip():
            print("[AUTOUPDATE] Yeni güncelleme bulundu. Güncelleniyor...")
            pull = subprocess.run(["git", "pull"], cwd=".", capture_output=True, text=True)
            if pull.returncode == 0:
                print("[AUTOUPDATE] Güncelleme başarılı, bot yeniden başlatılıyor...")
                sys.exit(0)
            else:
                print("[AUTOUPDATE] Güncelleme başarısız:", pull.stderr)
        else:
            print("[AUTOUPDATE] Güncel. Değişiklik yok.")

# -- Main fonksiyon --

async def main():
    await client.start()
    print("Bot başladı ve otomatik güncelleme aktif.")
    asyncio.create_task(auto_update_and_restart())
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot durduruldu.")
