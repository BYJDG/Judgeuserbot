from telethon import events
import json
import os

custom_commands = {}

if os.path.exists("custom_commands.json"):
    with open("custom_commands.json", "r") as f:
        custom_commands = json.load(f)

@events.register(events.NewMessage(pattern=r"^.ekle (.\S+) ([\s\S]+)"))
async def add_command(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return
    cmd = event.pattern_match.group(1)
    reply = event.pattern_match.group(2)
    custom_commands[cmd] = reply
    with open("custom_commands.json", "w") as f:
        json.dump(custom_commands, f)
    await event.reply(f"Komut eklendi: {cmd}")

@events.register(events.NewMessage(pattern=r"^.sil (.\S+)"))
async def del_command(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return
    cmd = event.pattern_match.group(1)
    if cmd in custom_commands:
        del custom_commands[cmd]
        with open("custom_commands.json", "w") as f:
            json.dump(custom_commands, f)
        await event.reply(f"{cmd} komutu silindi.")
    else:
        await event.reply("Böyle bir komut yok.")

@events.register(events.NewMessage())
async def custom_command_handler(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return
    text = event.raw_text.strip()
    if text in custom_commands:
        await event.reply(custom_commands[text])
