#!/bin/bash

echo "JudgeUserBot Kurulumuna Hoşgeldin!"

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

if [ -d "Judgeuserbot" ]; then
    echo "Repo zaten klonlanmış, güncelleniyor..."
    cd Judgeuserbot
    git pull
    cd ..
else
    echo "JudgeUserBot klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
fi

cd Judgeuserbot

pip install -r requirements.txt

# Session dosyası var mı kontrol et
if [ -f "judge_session.session" ]; then
    echo "Zaten bir session bulundu. API ID ve HASH yeniden girilmeyecek."
else
    echo "Telegram API bilgilerinizi giriniz."
    read -p "API ID: " API_ID
    read -p "API HASH: " API_HASH

    cat > config.py << EOL
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
admin_username = "byjudgee"
admin_id = 1486645014
EOL
    echo "Yeni config.py oluşturuldu."
fi

# .env dosyası kontrolü
if [ -f ".env" ]; then
    echo ".env dosyası zaten var. Değiştirilmeyecek."
else
    echo "OpenAI API anahtarını giriniz (isteğe bağlı):"
    read -p "API_KEY (boş bırakmak için Enter): " API_KEY

    echo "OPENAI_API_KEY=$API_KEY" > .env
    echo ".env dosyası oluşturuldu."
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
