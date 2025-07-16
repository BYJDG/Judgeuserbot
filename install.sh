#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

echo "Gerekli paketler yüklendi."

if [ -d "Judgeuserbot" ]; then
    echo "Repo zaten var, güncelleniyor..."
    cd Judgeuserbot
    git pull
    cd ..
else
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
fi

cd Judgeuserbot

pip install -r requirements.txt

echo "Lütfen Telegram API bilgilerinizi giriniz."
read -p "API ID: " API_ID
read -p "API HASH: " API_HASH
read -p "Botun admin kullanıcı adını giriniz (örn: byjudgee): " ADMIN_USERNAME
read -p "Admin kullanıcı ID'sini giriniz (örn: 1486645014): " ADMIN_ID

cat > config.py << EOL
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
admin_username = "$ADMIN_USERNAME"
admin_id = $ADMIN_ID
EOL

echo "Config dosyası oluşturuldu."

# === .sor Komutu Kurulumu ===
read -p ".sor komutu aktif edilsin mi? (y/n): " ENABLE_SOR
if [ "$ENABLE_SOR" == "y" ]; then
    # .env dosyasını kontrol et
    if [ ! -f ".env" ]; then
        touch .env
    fi

    if grep -q "OPENAI_API_KEY=" .env; then
        echo "API anahtarı zaten mevcut, atlanıyor..."
    else
        read -p "OpenAI API anahtarınızı girin: " API_KEY
        echo "OPENAI_API_KEY=$API_KEY" >> .env
        echo ".env dosyasına API anahtarı eklendi."
    fi

    # plugins klasörü yoksa oluştur
    if [ ! -d "userbot/plugins" ]; then
        mkdir -p userbot/plugins
    fi

    # sor.py dosyasını oluştur
    cat > userbot/plugins/sor.py << 'EOF'
import os
import openai
from telethon import events
from config import admin_id
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from userbot import client

@client.on(events.NewMessage(pattern=r"^.sor (.+)"))
async def gpt_sor(event):
    if event.sender_id != (await client.get_me()).id:
        return

    try:
        yanit = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": event.pattern_match.group(1)}],
            max_tokens=150,
            temperature=0.5
        )
        cevap = yanit.choices[0].message.content.strip()
        await event.reply(cevap)
    except Exception as e:
        await event.reply(f"Hata: {str(e)}")
EOF

    echo ".sor komutu başarıyla eklendi."
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
