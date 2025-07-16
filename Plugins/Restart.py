from telethon import events
import os
import sys

@events.register(events.NewMessage(pattern=r"^.restart$"))
async def restart(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return
    await event.reply("♻️ Bot yeniden başlatılıyor...")
    os.execv(sys.executable, [sys.executable] + sys.argv)
