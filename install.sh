#!/bin/bash

echo "📦 JudgeUserBot Kurulum Scripti"

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

echo "✅ Paketler tamam."

# Reposu kontrol et
if [ -d "Judgeuserbot" ]; then
    cd Judgeuserbot
    git pull
else
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
fi

pip install -r requirements.txt || pip install telethon openai requests python-dotenv

SESSION_FILE="judge_session.session"
CONFIG_FILE="config.py"
ENV_FILE=".env"

# SESSION VARSA TEKRAR SORMA
if [ -f "$SESSION_FILE" ]; then
    echo "✅ Session bulundu: $SESSION_FILE"
    USE_SESSION="y"
else
    read -p "Yeni bir Telegram oturumu başlatılsın mı? (y/n): " USE_SESSION
fi

# Session oluşturulacaksa API'yi sor
if [[ "$USE_SESSION" == "y" && ! -f "$CONFIG_FILE" ]]; then
    read -p "API ID: " API_ID
    read -p "API HASH: " API_HASH

    cat > config.py << EOL
import os
from dotenv import load_dotenv
load_dotenv()

api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
EOL

    echo "🔐 Session başlatılıyor..."
    python3 userbot.py --session
fi

# .env kontrolü
if [ -f "$ENV_FILE" ]; then
    echo "✅ .env bulundu."
else
    read -p "OpenAI API KEY: " OPENAI_KEY
    echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
fi

echo "🚀 Bot başlatılıyor..."
python3 userbot.py
