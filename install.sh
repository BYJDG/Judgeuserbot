#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Termux paket güncelleme ve temel araçların kurulumu
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Python paketleri yükleniyor
pip install --upgrade pip
pip install telethon==1.40.0

# JudgeUserBot repozitorisini klonla veya güncelle
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
else
    echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
    cd Judgeuserbot
    git pull
    cd ..
fi

# config.py oluşturma (API ID, Hash, session_name, admin bilgileri)
CONFIG_FILE="Judgeuserbot/config.py"

echo ""
echo "Lütfen Telegram API bilgilerinizi giriniz."
read -p "API ID: " API_ID
read -p "API HASH: " API_HASH
read -p "Session adı (örnek: session): " SESSION_NAME
read -p "Admin kullanıcı adı (örn: byjudgee): " ADMIN_USERNAME
read -p "Admin kullanıcı ID'si (örnek: 1486645014): " ADMIN_ID

cat > $CONFIG_FILE << EOF
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "$SESSION_NAME"
admin_username = "$ADMIN_USERNAME"
admin_id = $ADMIN_ID
EOF

echo ""
echo "config.py dosyası oluşturuldu."
echo "Kurulum tamamlandı! Bot başlatılıyor..."

# Botu başlat
cd Judgeuserbot
python3 userbot.py
