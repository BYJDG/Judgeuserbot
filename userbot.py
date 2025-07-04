import asyncio from telethon import TelegramClient, events import os import json import re from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash) afk = False afk_reason = "" afk_users = set() custom_commands = {}

Özel komutlar dosyası

def load_custom_commands(): global custom_commands if os.path.exists("commands.json"): with open("commands.json", "r") as f: custom_commands = json.load(f)

def save_custom_commands(): with open("commands.json", "w") as f: json.dump(custom_commands, f)

load_custom_commands()

@client.on(events.NewMessage(outgoing=True, pattern=r"^.ekle (.[a-zA-Z0-9_]+) (.+)")) async def add_command(event): cmd, response = event.pattern_match.group(1), event.pattern_match.group(2) custom_commands[cmd] = response save_custom_commands() await event.edit(f"✅ Komut eklendi: {cmd}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^.sil (.[a-zA-Z0-9_]+)")) async def delete_command(event): cmd = event.pattern_match.group(1) if cmd in custom_commands: del custom_commands[cmd] save_custom_commands() await event.edit(f"❌ Komut silindi: {cmd}") else: await event.edit("🚫 Böyle bir komut bulunamadı.")

@client.on(events.NewMessage(outgoing=True)) async def custom_cmd_handler(event): if event.raw_text in custom_commands: await event.respond(custom_commands[event.raw_text])

@client.on(events.NewMessage(outgoing=True, pattern=r"^.alive")) async def alive(event): me = await client.get_me() await event.edit(f"🤖 Userbotunuz çalışıyor!\n\nSeni seviyorum {me.first_name} ❤️\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(outgoing=True, pattern=r"^.judge")) async def judge_help(event): await event.edit(""" 📜 Judge Userbot Komutları v1.0:

.alive - Botun çalıştığını kontrol eder. .afk <sebep> - AFK moduna geç. .back - AFK modundan çık. .filter <kelime> <cevap> - Filtreli yanıt ekler. .unfilter <kelime> - Filtreyi kaldır. .judge - Tüm komutları listeler. .ekle <.komut> <cevap> - Özel komut tanımla. .sil <.komut> - Özel komutu sil. .eval <kod> - (Sadece admin) Python kodu çalıştır. .wlive - Bot durumu (sadece global admin). """)

@client.on(events.NewMessage(outgoing=True, pattern=r"^.afk (.+)")) async def afk_mode(event): global afk, afk_reason afk = True afk_reason = event.pattern_match.group(1) await event.edit("AFK moduna geçildi.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^.back")) async def back(event): global afk, afk_reason, afk_users afk = False afk_reason = "" afk_users.clear() await event.edit("Tekrar buradayım.")

@client.on(events.NewMessage(incoming=True)) async def afk_responder(event): global afk_users if afk: sender = await event.get_sender() if sender and sender.id not in afk_users: afk_users.add(sender.id) if event.is_private or (event.mentioned): await event.reply(afk_reason)

filters = {}

@client.on(events.NewMessage(outgoing=True, pattern=r"^.filter (\w+) (.+)")) async def add_filter(event): keyword, reply = event.pattern_match.group(1), event.pattern_match.group(2) filters[keyword.lower()] = reply await event.edit(f"✅ Filtre eklendi: {keyword}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^.unfilter (\w+)")) async def remove_filter(event): keyword = event.pattern_match.group(1).lower() if keyword in filters: del filters[keyword] await event.edit(f"❌ Filtre kaldırıldı: {keyword}") else: await event.edit("🚫 Böyle bir filtre yok.")

@client.on(events.NewMessage()) async def filter_checker(event): if not event.out: for keyword, reply in filters.items(): if keyword in event.raw_text.lower(): await event.reply(reply) break

@client.on(events.NewMessage(outgoing=True, pattern=r"^.wlive")) async def wlive(event): sender = await event.get_sender() if sender.id == admin_id: await event.edit("✅ JudgeUserBot aktif!\n⚙️ Sürüm: v1.0\n🔧 Sistem: Stabil şekilde çalışıyor.") else: await event.reply("🚫 Bu komut yalnızca global admin tarafından kullanılabilir.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^.eval (.+)")) async def evaluate(event): if (await event.get_sender()).id != admin_id: return try: result = str(eval(event.pattern_match.group(1))) await event.edit(f"📥 Sonuç:\n{result}") except Exception as e: await event.edit(f"🚫 Hata:\n{str(e)}")

async def main(): await client.start() print("Bot çalışıyor!") await client.run_until_disconnected()

if name == 'main': asyncio.run(main())

