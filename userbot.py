import asyncio from telethon import TelegramClient, events import os import json import re from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash) afk = {"status": False, "reason": ""} filters = {} personal_cmds = {}

.alive

@client.on(events.NewMessage(outgoing=True, pattern=r"^.alive")) async def alive_handler(event): user = await client.get_me() await event.edit(f"Userbotunuz çalışıyor ve sana bir şey demek istiyor...\nSeni seviyorum {user.first_name} ❤️\n\nBot Versiyonu: v1.0")

.wlive (admin-only)

@client.on(events.NewMessage(pattern=r"^.wlive")) async def wlive_handler(event): if event.sender_id == admin_id: await event.reply("⚡ JudgeUserBot çalışıyor!\n🚀 Sürüm: v1.0\n💻 Güçlü, stabil ve hazır!")

.afk <sebep>

@client.on(events.NewMessage(outgoing=True, pattern=r"^.afk (.+)")) async def afk_handler(event): reason = event.pattern_match.group(1) afk["status"] = True afk["reason"] = reason await event.edit("AFK moduna geçildi.")

.back

@client.on(events.NewMessage(outgoing=True, pattern=r"^.back")) async def back_handler(event): afk["status"] = False afk["reason"] = "" await event.edit("Tekrar buradayım!")

Mesaj geldiğinde afk kontrolü

@client.on(events.NewMessage(incoming=True)) async def afk_reply_handler(event): if afk["status"]: sender = await event.get_sender() if event.is_private or (event.mentioned and sender.bot is False): if not hasattr(event, "afk_replied"): await event.reply(afk["reason"]) event.afk_replied = True

.filter <mesaj> <cevap>

@client.on(events.NewMessage(outgoing=True, pattern=r"^.filter (.+?) (.+)")) async def filter_handler(event): key = event.pattern_match.group(1).lower() value = event.pattern_match.group(2) filters[key] = value await event.edit(f"'{key}' mesajı için otomatik cevap eklendi.")

.unfilter <mesaj>

@client.on(events.NewMessage(outgoing=True, pattern=r"^.unfilter (.+)")) async def unfilter_handler(event): key = event.pattern_match.group(1).lower() if key in filters: del filters[key] await event.edit(f"'{key}' filtresi kaldırıldı.") else: await event.edit(f"'{key}' filtresi bulunamadı.")

Filtre kontrolü

@client.on(events.NewMessage(incoming=True)) async def filter_reply(event): msg = event.raw_text.lower() for key in filters: if key in msg: await event.reply(filters[key]) break

.ekle <.komut> <cevap>

@client.on(events.NewMessage(outgoing=True, pattern=r"^.ekle (.[a-zA-Z0-9_]+) (.+)")) async def add_command(event): cmd = event.pattern_match.group(1) rsp = event.pattern_match.group(2) personal_cmds[cmd] = rsp await event.edit(f"'{cmd}' komutu eklendi.")

.sil <.komut>

@client.on(events.NewMessage(outgoing=True, pattern=r"^.sil (.[a-zA-Z0-9_]+)")) async def delete_command(event): cmd = event.pattern_match.group(1) if cmd in personal_cmds: del personal_cmds[cmd] await event.edit(f"'{cmd}' komutu silindi.") else: await event.edit(f"'{cmd}' komutu bulunamadı.")

Özel komut yanıtlayıcı

@client.on(events.NewMessage(outgoing=True)) async def personal_command_handler(event): if event.raw_text in personal_cmds: await event.reply(personal_cmds[event.raw_text])

.eval <kod> (owner-only)

@client.on(events.NewMessage(outgoing=True, pattern=r"^.eval (.+)")) async def eval_handler(event): if event.sender_id != admin_id: return try: result = str(eval(event.pattern_match.group(1))) await event.edit(f"Sonuç: {result}") except Exception as e: await event.edit(f"Hata: {e}")

.restart (owner-only)

@client.on(events.NewMessage(outgoing=True, pattern=r"^.restart")) async def restart_handler(event): if event.sender_id != admin_id: return await event.edit("♻️ Bot yeniden başlatılıyor...") os.execl(sys.executable, sys.executable, *sys.argv)

.update (owner-only)

@client.on(events.NewMessage(outgoing=True, pattern=r"^.update")) async def update_handler(event): if event.sender_id != admin_id: return os.system("cd Judgeuserbot && git pull") await event.edit("📥 Güncellemeler kontrol edildi.")

.judge komutu

@client.on(events.NewMessage(outgoing=True, pattern=r"^.judge")) async def judge_handler(event): await event.edit("""🎯 Judge Userbot Komutları v1.0:

.alive - Botun çalışıp çalışmadığını kontrol eder. .afk <sebep> - AFK moduna geçer. .back - AFK modundan çıkar. .filter <mesaj> <cevap> - Filtreli cevap ekler. .unfilter <mesaj> - Filtre kaldırır. .ekle <.komut> <cevap> - Özel komut tanımlar. .sil <.komut> - Özel komutu siler. .judge - Komut listesini gösterir. .wlive - Bot sahibi tarafından çalıştırılır. .restart - Botu yeniden başlatır (sadece owner). .update - Repo güncellemelerini çeker (sadece owner). .eval <kod> - Python kodu çalıştırır (sadece owner). """)

async def main(): await client.start() print("JudgeUserBot başarıyla başlatıldı.") await client.run_until_disconnected()

if name == "main": asyncio.run(main())

