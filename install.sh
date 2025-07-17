#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

pkg update -y && pkg upgrade -y pkg install python git ffmpeg libffi -y

echo "Gerekli paketler yüklendi."

if [ -d "Judgeuserbot" ]; then echo "Repo zaten var, güncelleniyor..." cd Judgeuserbot git pull cd .. else echo "JudgeUserBot repozitorisi klonlanıyor..." git clone https://github.com/BYJDG/Judgeuserbot.git fi

cd Judgeuserbot

pip install -r requirements.txt

if [ -f "judge_session.session" ]; then echo "Kayıtlı session bulundu. API bilgileri sorulmayacak." else echo "Lütfen Telegram API bilgilerinizi giriniz." read -p "API ID: " API_ID read -p "API HASH: " API_HASH

cat > config.py << EOL

api_id = $API_ID api_hash = "$API_HASH" session_name = "judge_session" admin_username = "" admin_id = 1486645014 EOL

echo "Config dosyası oluşturuldu."

fi

if [ -f ".env" ]; then echo ".env dosyası zaten mevcut." else echo "OpenAI API anahtarınızı giriniz (.sor komutu için):" read -p "API Key (sk-...): " OPENAI_KEY echo "OPENAI_API_KEY=$OPENAI_KEY" > .env echo ".env dosyası oluşturuldu." fi

echo "Kurulum tamamlandı! Bot başlatılıyor..." python3 userbot.py

