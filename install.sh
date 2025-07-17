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

# Session kontrolü
if [ -f "judge_session.session" ]; then
    echo "Kayıtlı session dosyası bulundu. Yeni API bilgisi girmek ister misiniz? (y/n)"
    read -p "Seçiminiz: " SECIM
    if [ "$SECIM" == "y" ]; then
        read -p "API ID: " API_ID
        read -p "API HASH: " API_HASH
    else
        echo "Mevcut session kullanılacak."
    fi
else
    echo "Yeni bir oturum oluşturulacak, API bilgilerinizi giriniz:"
    read -p "API ID: " API_ID
    read -p "API HASH: " API_HASH
fi

# config.py oluşturma
if [ ! -f "config.py" ]; then
    echo "config.py oluşturuluyor..."
    cat > config.py << EOL
api_id = ${API_ID:-0}
api_hash = "${API_HASH:-""}"
session_name = "judge_session"
admin_id = 1486645014
EOL
    echo "config.py dosyası oluşturuldu."
else
    echo "config.py zaten mevcut, atlanıyor."
fi

# .env dosyası oluşturma
if [ ! -f ".env" ]; then
    echo "OpenAI API anahtarınızı girin (GPT komutu için gerekliyse):"
    read -p "OpenAI_API_Key: " OPENAI_KEY

    echo "OPENAI_API_KEY=${OPENAI_KEY}" > .env
    echo ".env dosyası oluşturuldu."
else
    echo ".env zaten mevcut, atlanıyor."
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
