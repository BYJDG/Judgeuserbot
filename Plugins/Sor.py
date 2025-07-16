import os
import openai
from telethon import events
from dotenv import load_dotenv
from userbot import client

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@client.on(events.NewMessage(pattern=r"^.sor (.+)"))
async def gpt_sor(event):
    if event.sender_id != (await client.get_me()).id:
        return
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": event.pattern_match.group(1)}],
            max_tokens=100,
            temperature=0.5
        )
        answer = response.choices[0].message.content.strip()
        await event.reply(answer)
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")
