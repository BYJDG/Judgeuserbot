from telethon import events
from config import openai_api_key
from userbot import client  # client nesnesi burada tanımlı olmalı
import openai

openai.api_key = openai_api_key

@client.on(events.NewMessage(pattern=r"^.sor (.+)"))
async def sor(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return

    soru = event.pattern_match.group(1)
    try:
        yanit = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": soru}],
            max_tokens=100,
        )
        cevap = yanit.choices[0].message.content
        await event.reply(cevap)
    except Exception as e:
        await event.reply(f"❌ Hata: {e}")
