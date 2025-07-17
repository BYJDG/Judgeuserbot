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

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
