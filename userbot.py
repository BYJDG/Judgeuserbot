import asyncio import os import json import re from telethon import TelegramClient, events from config import api_id, api_hash, session_name, admin_id

client = TelegramClient(session_name, api_id, api_hash)

Oturum bilgisi

me = None

AFK bilgisi

afk = False afk_reason = None afk_notified_users = set()

Filtreler ve özel komutlar

filters = {} custom_commands = {}

.alive komutu

@client.on(events.NewMessage(pattern=r"^.alive$")) async def alive_handler(event): global me if event.sender_id != me.id: return await event.edit(f"Userbotunuz çalışıyor ve sana bişey demek istiyor..\nSeni seviyorum {me.first_name} ❤️\n\nBot Versiyonu: v1.0")

.afk komutu

@client.on(events.NewMessage(pattern=r"^.afk (.+)$")) async def afk_handler(event): global afk, afk_reason, afk_notified_users, me if event.sender_id != me.id: return afk = True afk_reason = event.pattern_match.group(1) afk_notified_users = set() await event.edit(f"AFK moduna geçtiniz: {afk_reason}")

.back komutu

@client.on(events.NewMessage(pattern=r"^.back$")) async def back_handler(event): global afk, afk_reason, afk_notified_users, me if event.sender_id != me.id: return afk = False afk_reason = None afk_notified_users = set() await event.edit("Tekrar buradayım!")

Mesajlara AFK bildirimi

@client.on(events.NewMessage()) async def afk_response(event): global afk, afk_reason, afk_notified_users, me if not afk: return if not event.is_private and me.id not in event.message.entities and not event.message.mentioned: return if event.sender_id in afk_notified_users: return afk_notified_users.add(event.sender_id) await event.reply(f"{afk_reason}")

.filter komutu

@client.on(events.NewMessage(pattern=r"^.filter (.+?) (.+)$")) async def add_filter(event): if event.sender_id != me.id: return keyword = event.pattern_match.group(1).lower() response = event.pattern_match.group(2) filters[keyword] = response await event.reply(f"Filtre eklendi: '{keyword}' => '{response}'")

.unfilter komutu

@client.on(events.NewMessage(pattern=r"^.unfilter (.+)$")) async def remove_filter(event): if event.sender_id != me.id: return keyword = event.pattern_match.group(1).lower() if keyword in filters: del filters[keyword] await event.reply(f"Filtre kaldırıldı: '{keyword}'")

Filtreleme cevap sistemi

@client.on(events.NewMessage()) async def filter_response(event): if event.sender_id == me.id: return message = event.message.message.lower() for keyword, response in filters.items(): if keyword in message: await event.reply(response) break

.ekle komutu

@client.on(events.NewMessage(pattern=r"^.ekle \.(\w+) (.+)$")) async def add_command(event): if event.sender_id != me.id: return cmd = event.pattern_match.group(1) response = event.pattern_match.group(2) custom_commands[cmd] = response await event.reply(f"Komut eklendi: .{cmd} => {response}")

.sil komutu

@client.on(events.NewMessage(pattern=r"^.sil \.(\w+)$")) async def del_command(event): if event.sender_id != me.id: return cmd = event.pattern_match.group(1) if cmd in custom_commands: del custom_commands[cmd] await event.reply(f"Komut silindi: .{cmd}")

Kişisel komutlara cevap

@client.on(events.NewMessage()) async def custom_command_response(event): if event.sender_id == me.id: message = event.message.message if message.startswith('.'): cmd = message[1:].split(' ')[0] if cmd in custom_commands: await event.reply(custom_commands[cmd])

.wlive komutu

@client.on(events.NewMessage(pattern=r"^.wlive$")) async def wlive_handler(event): if event.sender_id != admin_id: return await event.reply("🚀 JudgeUserBot Aktif!\nSistem stabil çalışıyor.\nVersiyon: v1.0")

.judge komutu

@client.on(events.NewMessage(pattern=r"^.judge$")) async def help_handler(event): if event.sender_id != me.id: return help_text = ( "🤖 JudgeUserBot Komutları v1.0:\n\n" ".alive - Botun çalışıp çalışmadığını kontrol eder.\n" ".afk <sebep> - AFK moduna geçer, sebebi belirtir.\n" ".back - AFK modundan çıkar.\n" ".filter <kelime> <cevap> - Filtreli otomatik cevap ekler.\n" ".unfilter <kelime> - Filtreyi kaldırır.\n" ".ekle .komut <cevap> - Kişisel komut tanımlar.\n" ".sil .komut - Kişisel komutu kaldırır.\n" ".wlive - Owner komutu (sadece @byjudgee kullanabilir).\n" ) await event.reply(help_text)

Başlatma

async def main(): global me await client.start() me = await client.get_me() print("JudgeUserBot çalışıyor!") await client.run_until_disconnected()

if name == 'main': asyncio.run(main())

           
