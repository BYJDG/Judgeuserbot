import asyncio import os import json import re from telethon import TelegramClient, events from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

afk_mode = False afk_reason = "" filtered_messages = {} custom_commands = {}

Load custom commands if available

if os.path.exists("custom_commands.json"): with open("custom_commands.json", "r") as f: custom_commands = json.load(f)

@client.on(events.NewMessage(pattern=r"^.alive$")) async def alive_handler(event): sender = await event.client.get_me() await event.edit(f"Userbotunuz çalışıyor... Seni seviyorum {sender.first_name} ❤️\n\nBot Versiyonu: v1.0")

@client.on(events.NewMessage(pattern=r"^.wlive$")) async def wlive_handler(event): if event.sender_id != admin_id: return await event.reply("🔥 JudgeBot Aktif 🔥\nVersiyon: v1.0\nSorunsuz çalışıyor.")

@client.on(events.NewMessage(pattern=r"^.judge$")) async def judge_help(event): help_text = ( "Judge Userbot Komutları v1.0:\n\n" ".alive - Botun çalıştığını kontrol eder.\n" ".afk <sebep> - AFK moduna geçer.\n" ".back - AFK modundan çıkar.\n" ".filter <kelime> <cevap> - Otomatik yanıt ekler.\n" ".unfilter <kelime> - Filtreyi kaldırır.\n" ".ekle <.komut> <cevap> - Kişisel komut ekler.\n" ".sil <.komut> - Kişisel komutu siler.\n" ".restart - Botu yeniden başlatır.\n" ".kick <id veya reply> - Kullanıcıyı gruptan atar.\n" ".ban <id veya reply> - Kullanıcıyı gruptan banlar.\n" ".eval <kod> - Yalnızca admin çalıştırabilir.\n" ".wlive - Global admin için sistem durumu." ) await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"^.afk (.+)")) async def afk_handler(event): global afk_mode, afk_reason afk_mode = True afk_reason = event.pattern_match.group(1) await event.edit(afk_reason)

@client.on(events.NewMessage(pattern=r"^.back$")) async def back_handler(event): global afk_mode, afk_reason afk_mode = False afk_reason = "" await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage()) async def afk_auto_reply(event): if afk_mode and event.is_private: await event.reply(afk_reason) global afk_mode afk_mode = False

@client.on(events.NewMessage(pattern=r"^.filter (.+?) (.+)")) async def filter_handler(event): keyword, response = event.pattern_match.group(1), event.pattern_match.group(2) filtered_messages[keyword.lower()] = response await event.reply(f"Filtre eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.unfilter (.+)")) async def unfilter_handler(event): keyword = event.pattern_match.group(1) if keyword.lower() in filtered_messages: del filtered_messages[keyword.lower()] await event.reply(f"Filtre kaldırıldı: {keyword}") else: await event.reply("Bu kelimeye ait bir filtre bulunamadı.")

@client.on(events.NewMessage()) async def filter_response(event): for keyword, response in filtered_messages.items(): if keyword in event.raw_text.lower(): await event.reply(response) break

@client.on(events.NewMessage(pattern=r"^.ekle (..+?) (.+)")) async def add_command(event): cmd, reply = event.pattern_match.group(1), event.pattern_match.group(2) custom_commands[cmd] = reply with open("custom_commands.json", "w") as f: json.dump(custom_commands, f) await event.reply(f"Komut eklendi: {cmd} → {reply}")

@client.on(events.NewMessage(pattern=r"^.sil (..+)")) async def del_command(event): cmd = event.pattern_match.group(1) if cmd in custom_commands: del custom_commands[cmd] with open("custom_commands.json", "w") as f: json.dump(custom_commands, f) await event.reply(f"Komut silindi: {cmd}") else: await event.reply("Böyle bir komut bulunamadı.")

@client.on(events.NewMessage()) async def custom_command_handler(event): if event.raw_text.strip() in custom_commands: await event.reply(custom_commands[event.raw_text.strip()])

@client.on(events.NewMessage(pattern=r"^.restart$")) async def restart_handler(event): await event.reply("♻️ Bot yeniden başlatılıyor...") os.execv(sys.executable, [sys.executable] + sys.argv)

@client.on(events.NewMessage(pattern=r"^.kick(?: (.+))?")) async def kick_user(event): if event.is_group: if event.is_reply: user = await event.get_reply_message().get_sender() elif event.pattern_match.group(1): user = await client.get_entity(event.pattern_match.group(1)) else: return await event.reply("Kicklemek için kullanıcı belirt.") await event.chat.kick_participant(user.id) await event.reply(f"{user.first_name} gruptan atıldı.")

@client.on(events.NewMessage(pattern=r"^.ban(?: (.+))?")) async def ban_user(event): if event.is_group: if event.is_reply: user = await event.get_reply_message().get_sender() elif event.pattern_match.group(1): user = await client.get_entity(event.pattern_match.group(1)) else: return await event.reply("Banlamak için kullanıcı belirt.") await client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True))) await event.reply(f"{user.first_name} gruptan banlandı.")

@client.on(events.NewMessage(pattern=r"^.eval (.+)")) async def eval_handler(event): if event.sender_id != admin_id: return code = event.pattern_match.group(1) try: result = eval(code) await event.reply(str(result)) except Exception as e: await event.reply(f"Hata: {str(e)}")

async def main(): await client.start() print("JudgeUserBot çalışıyor...") await client.run_until_disconnected()

if name == "main": asyncio.run(main())
