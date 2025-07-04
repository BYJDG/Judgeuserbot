import asyncio import os import json import re from telethon import TelegramClient, events from config import api_id, api_hash, session_name, admin_id

session_file = f"{session_name}.session" custom_commands_file = "custom_commands.json" afk_data = {"active": False, "reason": ""} filters = {}

if os.path.exists("filters.json"): with open("filters.json", "r") as f: filters = json.load(f)

if os.path.exists(custom_commands_file): with open(custom_commands_file, "r") as f: custom_commands = json.load(f) else: custom_commands = {}

client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(outgoing=True, pattern=r".alive")) async def alive(event): user = await client.get_me() await event.edit(f"Userbotunuz çalışıyor ve sana bir şey demek istiyor..\nSeni seviyorum {user.first_name} ❤️\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(outgoing=True, pattern=r".afk(?:\s+(.*))?")) async def afk(event): reason = event.pattern_match.group(1) afk_data["active"] = True afk_data["reason"] = reason if reason else "AFK" await event.edit(f"{afk_data['reason']}")

@client.on(events.NewMessage(outgoing=True, pattern=r".back")) async def back(event): afk_data["active"] = False afk_data["reason"] = "" await event.edit("AFK modundan çıktım.")

@client.on(events.NewMessage(incoming=True)) async def afk_reply(event): if afk_data["active"]: if event.is_private or (event.mentioned and event.chat): await event.reply(f"{afk_data['reason']}") afk_data["active"] = False afk_data["reason"] = ""

@client.on(events.NewMessage(outgoing=True, pattern=r".filter (.+?) (.+)")) async def add_filter(event): keyword, reply = event.pattern_match.group(1), event.pattern_match.group(2) filters[keyword] = reply with open("filters.json", "w") as f: json.dump(filters, f) await event.edit(f"'{keyword}' kelimesi için filtre eklendi.")

@client.on(events.NewMessage(outgoing=True, pattern=r".unfilter (.+)")) async def remove_filter(event): keyword = event.pattern_match.group(1) if keyword in filters: del filters[keyword] with open("filters.json", "w") as f: json.dump(filters, f) await event.edit(f"'{keyword}' filtresi kaldırıldı.") else: await event.edit("Bu filtre bulunamadı.")

@client.on(events.NewMessage(outgoing=True, pattern=r".ekle (\S+) (.+)")) async def add_command(event): cmd, response = event.pattern_match.group(1), event.pattern_match.group(2) custom_commands[cmd] = response with open(custom_commands_file, "w") as f: json.dump(custom_commands, f) await event.edit(f"{cmd} komutu eklendi.")

@client.on(events.NewMessage(outgoing=True, pattern=r".sil (\S+)")) async def delete_command(event): cmd = event.pattern_match.group(1) if cmd in custom_commands: del custom_commands[cmd] with open(custom_commands_file, "w") as f: json.dump(custom_commands, f) await event.edit(f"{cmd} komutu silindi.") else: await event.edit("Bu komut bulunamadı.")

@client.on(events.NewMessage(outgoing=True, pattern=r".judge")) async def show_commands(event): text = """Judge Userbot Komutları v1.0:

.alive - Botun çalışıp çalışmadığını kontrol eder. .afk <sebep> - AFK moduna geçer, sebebi belirtir. .back - AFK modundan çıkar. .filter <mesaj> <cevap> - Filtreli otomatik cevap ekler. .unfilter <mesaj> - Filtreyi kaldırır. .ekle <.komut> <cevap> - Kişisel komut eklersin. .sil <.komut> - Kişisel komutu silersin. .restart - Botu yeniden başlatır. .kick - Bir kullanıcıyı gruptan atar (yanıtla). .ban - Bir kullanıcıyı gruptan banlar (yanıtla). .wlive - Owner komutu, sadece admin kullanabilir. .eval - Sadece admin tarafından çalıştırılır. """ await event.edit(text)

@client.on(events.NewMessage(outgoing=True)) async def custom_cmd_handler(event): cmd = event.raw_text.strip() if cmd in custom_commands: await event.edit(custom_commands[cmd])

@client.on(events.NewMessage(outgoing=True, pattern=r".restart")) async def restart_bot(event): await event.edit("Bot yeniden başlatılıyor...") os.execl(sys.executable, sys.executable, *sys.argv)

@client.on(events.NewMessage(outgoing=True, pattern=r".kick")) async def kick_user(event): if event.is_group and event.reply_to_msg_id: reply_msg = await event.get_reply_message() await client.kick_participant(event.chat_id, reply_msg.sender_id) await event.edit("Kullanıcı atıldı.")

@client.on(events.NewMessage(outgoing=True, pattern=r".ban")) async def ban_user(event): if event.is_group and event.reply_to_msg_id: reply_msg = await event.get_reply_message() await client.edit_permissions(event.chat_id, reply_msg.sender_id, view_messages=False) await event.edit("Kullanıcı banlandı.")

@client.on(events.NewMessage(outgoing=True, pattern=r".eval")) async def eval_code(event): if event.sender_id == admin_id: code = event.raw_text.split(" ", 1)[1] try: result = eval(code) await event.edit(str(result)) except Exception as e: await event.edit(f"Hata: {e}") else: await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r".wlive")) async def wlive(event): if event.sender_id == admin_id: await event.edit("☑️ Bot aktif!\n⚙️ Versiyon: v1.0\n🔒 Sistem çalışıyor.") else: await event.delete()

async def main(): await client.start() print("Bot çalışıyor...") await client.run_until_disconnected()

if name == "main": asyncio.run(main())

