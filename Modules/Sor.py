import os
import openai
from dotenv import load_dotenv
from telethon import events

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from userbot import bot  # Eğer farklı isimliyse burayı düzenle

@bot.on(events.NewMessage(pattern=r"^.sor (.+)"))
async def sor_handler(event):
    question = event.pattern_match.group(1)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": question}
            ],
            temperature=0.2,
            max_tokens=100,
        )
        cevap = response['choices'][0]['message']['content'].strip()
        await event.reply(cevap)
    except Exception as e:
        await event.reply(f"❌ Hata: {e}")
