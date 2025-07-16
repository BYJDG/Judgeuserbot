from telethon import events
from userbot import client  # Eğer userbot.py ayrıysa importu ayarla

afk_mode = False
afk_reason = ""
afk_replied_users = set()

@client.on(events.NewMessage(pattern=r"^.afk (.+)"))
async def afk_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    if event.sender_id != (await client.get_me()).id:
        return
    afk_mode = True
    afk_reason = event.pattern_match.group(1)
    afk_replied_users.clear()
    await event.edit("AFK moduna geçildi.")

@client.on(events.NewMessage(pattern=r"^.back$"))
async def back_handler(event):
    global afk_mode, afk_reason, afk_replied_users
    if event.sender_id != (await client.get_me()).id:
        return
    afk_mode = False
    afk_reason = ""
    afk_replied_users.clear()
    await event.edit("Tekrar aktif oldum!")

@client.on(events.NewMessage())
async def afk_auto_reply(event):
    global afk_mode, afk_reason, afk_replied_users
    if afk_mode and event.sender_id != (await client.get_me()).id:
        if event.is_private or (event.is_group and (event.mentioned or event.is_reply)):
            if event.sender_id not in afk_replied_users:
                await event.reply(afk_reason)
                afk_replied_users.add(event.sender_id)
