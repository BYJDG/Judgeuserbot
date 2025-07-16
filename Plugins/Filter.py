import json
from telethon import events
from userbot import client

filtered_messages = {}

try:
    with open("filtered.json", "r") as f:
        filtered_messages = json.load(f)
except:
    filtered_messages = {}

@client.on(events.NewMessage(pattern=r"^.filter (\S+) ([\s\S]+)"))
async def filter_add(event):
    if event.sender_id != (await client.get_me()).id:
        return
    keyword = event.pattern_match.group(1).lower()
    response = event.pattern_match.group(2)
    filtered_messages[keyword] = response
    with open("filtered.json", "w") as f:
        json.dump(filtered_messages, f)
    await event.reply(f"Filtre eklendi: {keyword} → {response}")

@client.on(events.NewMessage(pattern=r"^.filters$"))
async def filter_list(event):
    if event.sender_id != (await client.get_me()).id:
        return
    if not filtered_messages:
        return await event.reply("📭 PM filtresi yok.")
    msg = "📥 PM Filtreleri:\n" + "\n".join(f"- {k}" for k in filtered_messages)
    await event.reply(msg)

@client.on(events.NewMessage(pattern=r"^.unfilter (.+)"))
async def filter_remove(event):
    if event.sender_id != (await client.get_me()).id:
        return
    keyword = event.pattern_match.group(1).lower()
    if keyword in filtered_messages:
        del filtered_messages[keyword]
        with open("filtered.json", "w") as f:
            json.dump(filtered_messages, f)
        await event.reply(f"{keyword} filtresi kaldırıldı.")
    else:
        await event.reply("Böyle bir filtre yok.")

@client.on(events.NewMessage())
async def filter_response(event):
    if event.is_private and event.sender_id != (await client.get_me()).id:
        for keyword, response in filtered_messages.items():
            if keyword.lower() in event.raw_text.lower():
                await event.reply(response)
                break
