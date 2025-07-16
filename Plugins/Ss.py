from telethon import events
from userbot import client

@client.on(events.NewMessage(pattern=r"^.ss (.+)"))
async def screenshot(event):
    if event.sender_id != (await client.get_me()).id:
        return
    url = event.pattern_match.group(1)
    api_url = f"https://image.thum.io/get/width/1200/{url}"
    try:
        await client.send_file(event.chat_id, api_url, caption=f"📸 Screenshot: {url}")
    except Exception as e:
        await event.reply(f"Ekran görüntüsü alınamadı: {str(e)}")
