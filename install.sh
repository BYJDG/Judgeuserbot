#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

if [ -d "Judgeuserbot" ]; then
    echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
    cd Judgeuserbot
    git pull
else
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
fi

pip install -r requirements.txt

if [ -f "config.json" ]; then
    echo "config.json zaten mevcut."
    read -p "Yeni API bilgileri ile tekrar giriş yapmak ister misiniz? (Y/n): " answer
    if [[ "$answer" == "Y" || "$answer" == "y" ]]; then
        echo "Yeni API bilgilerinizi giriniz."
        while true; do
            read -p "API ID (sadece rakam): " api_id
            if [[ "$api_id" =~ ^[0-9]+$ ]]; then
                break
            else
                echo "Lütfen sadece rakam giriniz!"
            fi
        done
        read -p "API HASH: " api_hash

        cat > config.json <<EOF
{
  "api_id": $api_id,
  "api_hash": "$api_hash"
}
EOF
    else
        echo "Mevcut config.json ile devam ediliyor."
    fi
else
    echo "Lütfen Telegram API bilgilerinizi giriniz."
    while true; do
        read -p "API ID (sadece rakam): " api_id
        if [[ "$api_id" =~ ^[0-9]+$ ]]; then
            break
        else
            echo "Lütfen sadece rakam giriniz!"
        fi
    done
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
