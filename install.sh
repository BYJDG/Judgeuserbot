#!/bin/bash

echo "📦 JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

echo "✅ Gerekli paketler yüklendi."

# Reposu zaten varsa güncelle
if [ -d "Judgeuserbot" ]; then
    echo "📁 Reposu bulundu, güncelleniyor..."
    cd Judgeuserbot
    git pull
else
    echo "📥 Reposu klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
fi

echo "📦 Python bağımlılıkları kuruluyor..."
pip install -r requirements.txt || pip install telethon openai requests python-dotenv

# SESSION dosyasını kontrol et
SESSION_FILE="judge_session.session"
if [ -f "$SESSION_FILE" ]; then
    echo "🔐 Zaten bir session var: $SESSION_FILE"
    read -p "Bu oturumu kullanmak istiyor musunuz? (y/n): " use_session
else
    use_session="n"
fi

# .env dosyasını kontrol et
if [ -f ".env" ]; then
    echo "🧠 Kayıtlı .env bulundu."
    read -p "Mevcut OpenAI API key’i kullanmak istiyor musunuz? (y/n): " use_env
else
    use_env="n"
fi

# Eğer yeni session isteniyorsa
if [[ "$use_session" == "n" ]]; then
    echo "📲 Telegram API bilgilerini giriniz:"
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

    echo "🔐 Yeni session başlatılıyor..."
    python3 userbot.py --session
else
    echo "🟢 Kayıtlı session kullanılacak."
    if [ ! -f "config.py" ]; then
        echo "⚠️ config.py bulunamadı! Lütfen API ID ve HASH giriniz:"
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
    fi
fi

# Eğer yeni .env isteniyorsa
if [[ "$use_env" == "n" ]]; then
    read -p "OpenAI API Anahtarınızı giriniz: " OPENAI_KEY
    echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
    echo "🧠 Yeni .env dosyası oluşturuldu."
else
    echo "✅ Mevcut .env dosyası kullanılacak."
fi

echo "🚀 Kurulum tamamlandı, bot başlatılıyor..."
python3 userbot.py
