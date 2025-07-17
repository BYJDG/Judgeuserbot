from telethon import events

help_data = {
    "filtre": [".ekle", ".sil"],
    "sistem": [".restart", ".log"],
    "gpt": [".sor <soru>"],
    "geliştirici": [".eval", ".exec", ".uptime"],
    "genel": [".ban", ".kick", ".yardım", ".ss", ".wlive"],
}

@events.register(events.NewMessage(pattern=r"^.yardım(?: (\w+))?"))
async def help(event):
    me = await event.client.get_me()
    if event.sender_id != me.id:
        return

    kategori = event.pattern_match.group(1)
    if kategori:
        cmds = help_data.get(kategori.lower())
        if cmds:
            mesaj = f"📂 **{kategori.title()}** komutları:\n" + "\n".join(cmds)
        else:
            mesaj = "❌ Böyle bir kategori bulunamadı."
    else:
        mesaj = "📚 **Komut Kategorileri:**\n"
        mesaj += "\n".join(f"- `{k}`" for k in help_data.keys())
        mesaj += "\n\nBir kategori görmek için: `.yardım <kategori>`"
    await event.reply(mesaj)
