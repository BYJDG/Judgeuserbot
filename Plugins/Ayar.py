import json
import os
from telethon import events
from userbot import client

SETTINGS_FILE = "settings.json"
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({}, f)

def load_settings():
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@client.on(events.NewMessage(pattern=r"^.ayar(?: (.+))?"))
async def ayar(event):
    if event.sender_id != (await client.get_me()).id:
        return
    args = event.pattern_match.group(1)
    settings = load_settings()
    user_id = str(event.sender_id)
    if args is None:
        # Ayarları göster
        user_settings = settings.get(user_id, {})
        if not user_settings:
            await event.reply("Henüz ayarınız yok.")
        else:
            ayarlar = "\n".join(f"{k}: {v}" for k,v in user_settings.items())
            await event.reply(f"Ayarlarınız:\n{ayarlar}")
    else:
        # Ayar değiştir - örn: .ayar dil tr
        parts = args.split(None, 1)
        if len(parts) != 2:
            await event.reply("Kullanım: .ayar <ayar_adı> <değer>")
            return
        key, value = parts
        if user_id not in settings:
            settings[user_id] = {}
        settings[user_id][key] = value
        save_settings(settings)
        await event.reply(f"Ayarınız kaydedildi: {key} = {value}")
