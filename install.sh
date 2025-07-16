#!/bin/bash

echo "📦 JudgeUserBot Kurulumu Başlatılıyor..."

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

echo "✅ Gerekli paketler yüklendi."

if [ -d "Judgeuserbot" ]; then
    echo "🔄 Reposu zaten var, güncelleniyor..."
    cd Judgeuserbot
    git pull
    cd ..
else
    echo "📥 Reposu klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
fi

cd Judgeuserbot

pip install -r requirements.txt

# Zaten API ID varsa tekrar sorma
if [ ! -f config.py ]; then
    echo "📱 Lütfen Telegram API bilgilerini giriniz:"
    read -p "API ID: " API_ID
    read -p "API HASH: " API_HASH

    cat > config.py << EOL
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
EOL

    echo "✅ config.py oluşturuldu."
else
    echo "✅ config.py zaten var, atlanıyor."
fi

# .env dosyasını kontrol et
if [ ! -f .env ]; then
    read -p "🧠 OpenAI API Key (.sor komutu için) girin: " OPENAI_KEY
    echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
    echo "✅ .env oluşturuldu."
else
    echo "✅ .env zaten var, atlanıyor."
fi

echo "🚀 Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
