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
pip install python-dotenv openai googletrans==4.0.0-rc1

echo "Lütfen Telegram API bilgilerinizi giriniz."
read -p "API ID: " API_ID
read -p "API HASH: " API_HASH
read -p "Botun admin kullanıcı adını giriniz (örn: byjudgee): " ADMIN_USERNAME
read -p "Admin kullanıcı ID'sini giriniz (örn: 1486645014): " ADMIN_ID

echo "OpenAI API keyiniz var mı? (y/n)"
read -r OPENAI_ANSWER

if [ "$OPENAI_ANSWER" = "y" ] || [ "$OPENAI_ANSWER" = "Y" ]; then
    read -p "OpenAI API Keyinizi girin (sk-... ile başlayan): " OPENAI_API_KEY
else
    OPENAI_API_KEY=""
fi

# config.py oluşturma
cat > config.py << EOL
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
admin_username = "$ADMIN_USERNAME"
admin_id = $ADMIN_ID
EOL

# .env dosyası oluşturma (OpenAI key için)
if [ -n "$OPENAI_API_KEY" ]; then
cat > .env << EOL
OPENAI_API_KEY=$OPENAI_API_KEY
EOL
fi

echo "Config dosyası ve .env dosyası oluşturuldu."

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
