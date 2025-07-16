from telethon import events
from config import admin_id

from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

banned_rights = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

@events.register(events.NewMessage(pattern=r"^.ban(?: (.+))?"))
async def ban(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:  # sadece kendi hesabı kullanabilir
        return
    if not (event.is_group or event.is_channel):
        await event.reply("Bu komut sadece grup ve kanallarda çalışır.")
        return
    reply = await event.get_reply_message()
    target = None
    if reply:
        target = reply.sender_id
    else:
        args = event.pattern_match.group(1)
        if args:
            try:
                target = int(args)
            except:
                await event.reply("Geçerli bir kullanıcı ID'si girin veya kullanıcıyı yanıtlayın.")
                return
    if not target:
        await event.reply("Banlamak için kullanıcıyı yanıtlayın veya ID girin.")
        return
    try:
        await event.client(EditBannedRequest(event.chat_id, target, banned_rights))
        await event.reply("Kullanıcı banlandı.")
    except Exception as e:
        await event.reply(f"Banlama işlemi başarısız: {e}")

@events.register(events.NewMessage(pattern=r"^.kick(?: (.+))?"))
async def kick(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return
    if not (event.is_group or event.is_channel):
        await event.reply("Bu komut sadece grup ve kanallarda çalışır.")
        return
    reply = await event.get_reply_message()
    target = None
    if reply:
        target = reply.sender_id
    else:
        args = event.pattern_match.group(1)
        if args:
            try:
                target = int(args)
            except:
                await event.reply("Geçerli bir kullanıcı ID'si girin veya kullanıcıyı yanıtlayın.")
                return
    if not target:
        await event.reply("Atmak için kullanıcıyı yanıtlayın veya ID girin.")
        return
    try:
        from telethon.tl.types import ChatBannedRights
        # Kick için süresiz yasaklama (until_date=None)
        await event.client(EditBannedRequest(event.chat_id, target, ChatBannedRights(until_date=None)))
        await event.reply("Kullanıcı atıldı.")
    except Exception as e:
        await event.reply(f"Atma işlemi başarısız: {e}")
