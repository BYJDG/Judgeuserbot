#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Gerekli paketleri güncelle ve yükle
pkg update -y
pkg upgrade -y
pkg install python git ffmpeg libffi -y

# Repo kontrolü ve klonlama
if [ -d "Judgeuserbot" ]; then
    echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
    cd Judgeuserbot
    git pull
else
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
fi

# Python paketlerini yükle
pip install -r requirements.txt

# Config kontrolü ve API bilgilerini alma
if [ -f "config.json" ]; then
    echo "config.json dosyası zaten mevcut."
    read -p "Mevcut oturumu kullanmak istiyor musunuz? (Y/n): " answer
    if [[ "$answer" == "n" || "$answer" == "N" ]]; then
        echo "Yeni API bilgilerinizi giriniz."
        read -p "API ID: " api_id
        read -p "API HASH: " api_hash

        cat > config.json <<EOF
{
  "api_id": $api_id,
  "api_hash": "$api_hash"
}
EOF
    else
        echo "Mevcut ayarlarla devam ediliyor."
    fi
else
    echo "Lütfen Telegram API bilgilerinizi giriniz."
    read -p "API ID: " api_id
    read -p "API HASH: " api_hash

    cat > config.json <<EOF
{
  "api_id": $api_id,
  "api_hash": "$api_hash"
}
EOF
fi

echo "Kurulum tamamlandı. Bot başlatılıyor..."
python3 userbot.py
