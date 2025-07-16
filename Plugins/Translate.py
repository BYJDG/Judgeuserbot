from telethon import events
from userbot import client
from googletrans import Translator

translator = Translator()

@client.on(events.NewMessage(pattern=r"^.translate (\S+) (.+)"))
async def translate_handler(event):
    if event.sender_id != (await client.get_me()).id:
        return
    lang = event.pattern_match.group(1)
    text = event.pattern_match.group(2)
    try:
        translated = translator.translate(text, dest=lang)
        await event.reply(f"{translated.text}")
    except Exception as e:
        await event.reply(f"Çeviri hatası: {str(e)}")
