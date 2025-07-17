from telethon import events
import os
import requests
from config import admin_id

@events.register(events.NewMessage(pattern=r"^.ss (.+)"))
async def screenshot(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return
    url = event.pattern_match.group(1)
    try:
        api_url = f"https://image.thum.io/get/width/1280/crop/675/{url}"
        r = requests.get(api_url)
        if r.status_code == 200:
            with open("screenshot.png", "wb") as f:
                f.write(r.content)
            await event.reply(file="screenshot.png")
            os.remove("screenshot.png")
        else:
            await event.reply("Görsel alınamadı.")
    except Exception as e:
        await event.reply(f"Hata: {e}")
