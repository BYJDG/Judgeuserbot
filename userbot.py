import asyncio import os import json import re from telethon import TelegramClient, events from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

is_afk = False afk_reason = None notified_users = set() custom_commands = {}

Komutlar dosyası

CUSTOM_COMMANDS_FILE = "custom_commands.json" if os.path.exists(CUSTOM_COMMANDS_FILE): with open(CUSTOM_COMMANDS_FILE, "r") as f: custom_commands = json.load(f)

@client.on(events.NewMessage(pattern=r'^.alive$')) async def alive(event): if event.sender_id == (await client.get_me()).id: sender = await event.get_sender() await event.edit(f"Userbotunuz çalışıyor ve sana bir şey demek istiyor...\nSeni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r'^.afk(?:\s+(.*))?$')) async def set_afk(event): global is_afk, afk_reason, notified_users if event.sender_id == (await client.get_me()).id: is_afk = True afk_reason = event.pattern_match.group(1) notified_users = set() msg = afk_reason if afk_reason else "AFK modundayım." await event.edit(msg)

@client.on(events.NewMessage(pattern=r'^.back$')) async def back_from_afk(event): global is_afk, afk_reason, notified_users if event.sender_id == (await client.get_me()).id: is_afk = False afk_reason = None notified_users = set() await event.edit("AFK modundan çıktım.")

@client.on(events.NewMessage()) async def afk_auto_reply(event): global is_afk, afk_reason, notified_users if is_afk and event.sender_id != (await client.get_me()).id: if event.is_private or (event.is_group and (await event.get_sender()).mention in event.raw_text): if event.sender_id not in notified_users: notified_users.add(event.sender_id) await event.reply(afk_reason if afk_reason else "AFK modundayım.")

@client.on(events.NewMessage(pattern=r'^.filter\s+(\S+)\s+(.+)$')) async def add_filter(event): if event.sender_id == (await client.get_me()).id: keyword = event.pattern_match.group(1).lower() response = event.pattern_match.group(2) custom_commands[keyword] = response with open(CUSTOM_COMMANDS_FILE, "w") as f: json.dump(custom_commands, f) await event.reply(f"Filtre eklendi: {keyword}")

@client.on(events.NewMessage(pattern=r'^.unfilter\s+(\S+)$')) async def remove_filter(event): if event.sender_id == (await client.get_me()).id: keyword = event.pattern_match.group(1).lower() if keyword in custom_commands: del custom_commands[keyword] with open(CUSTOM_COMMANDS_FILE, "w") as f: json.dump(custom_commands, f) await event.reply(f"Filtre kaldırıldı: {keyword}")

@client.on(events.NewMessage(pattern=r'^.ekle\s+(\S+)\s+(.+)$')) async def add_custom_command(event): if event.sender_id == (await client.get_me()).id: cmd = event.pattern_match.group(1).lstrip(".") response = event.pattern_match.group(2) custom_commands[cmd] = response with open(CUSTOM_COMMANDS_FILE, "w") as f: json.dump(custom_commands, f) await event.reply(f"Komut eklendi: .{cmd}")

@client.on(events.NewMessage(pattern=r'^.sil\s+(\S+)$')) async def delete_custom_command(event): if event.sender_id == (await client.get_me()).id: cmd = event.pattern_match.group(1).lstrip(".") if cmd in custom_commands: del custom_commands[cmd] with open(CUSTOM_COMMANDS_FILE, "w") as f: json.dump(custom_commands, f) await event.reply(f"Komut silindi: .{cmd}") else: await event.reply("Böyle bir komut bulunamadı.")

@client.on(events.NewMessage(pattern=r'^.judge$')) async def list_commands(event): if event.sender_id == (await client.get_me()).id: msg = "Judge Userbot Komutları v1.0:\n\n" msg += ".alive - Botun çalışıp çalışmadığını kontrol eder.\n" msg += ".afk <sebep> - AFK moduna geçer, sebebi belirtir.\n" msg += ".back - AFK modundan çıkar.\n" msg += ".filter <kelime> <cevap> - Mesaj filtreleme.\n" msg += ".unfilter <kelime> - Filtreyi kaldır.\n" msg += ".ekle .komut <cevap> - Yeni komut ekle.\n" msg += ".sil .komut - Eklenen komutu sil.\n" msg += ".judge - Komut listesini gösterir.\n" msg += ".wlive - Global admin komutu.\n" await event.reply(msg)

@client.on(events.NewMessage(pattern=r'^.wlive$')) async def wlive(event): if event.sender_id == int(admin_id): await event.reply("✨ JudgeUserBot aktif!\nHer şey yolunda görünüyor.\nBot Versiyon: v1.0")

@client.on(events.NewMessage) async def custom_command_handler(event): if event.sender_id == (await client.get_me()).id: cmd = event.raw_text.lstrip(".") if cmd in custom_commands: await event.reply(custom_commands[cmd])

async def main(): await client.start() print("[JudgeUserBot] Bot başlatıldı.") await client.run_until_disconnected()

if name == 'main': asyncio.run(main())

