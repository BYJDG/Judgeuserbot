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

# Telegram session kontrol
if [ -f "judge_session.session" ]; then
    echo "Telegram session dosyası bulundu. Oturum zaten var, tekrar oturum açmanıza gerek yok."
    SESSION_EXISTS=true
else
    echo "Telegram session dosyası bulunamadı. Oturum açmanız gerekecek."
    SESSION_EXISTS=false
fi

# Config.py var mı kontrol (api_id, api_hash, admin bilgileri için)
if [ -f "config.py" ]; then
    echo "Config dosyası bulundu."
    CONFIG_EXISTS=true
else
    CONFIG_EXISTS=false
fi

# OpenAI API Key kontrolü
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY=" ".env"; then
        echo ".env dosyasında OpenAI API Key bulundu."
        OPENAI_KEY_EXISTS=true
    else
        OPENAI_KEY_EXISTS=false
    fi
else
    OPENAI_KEY_EXISTS=false
fi

# Config.py oluştur veya var olanı kullan
if [ "$CONFIG_EXISTS" = false ]; then
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
else
    echo "Mevcut config.py dosyası kullanılacak."
fi

# OpenAI key yoksa sor, varsa kullan
if [ "$OPENAI_KEY_EXISTS" = false ]; then
    echo "OpenAI API keyiniz var mı? (y/n)"
    read -r OPENAI_ANSWER

    if [ "$OPENAI_ANSWER" = "y" ] || [ "$OPENAI_ANSWER" = "Y" ]; then
        read -p "OpenAI API Keyinizi girin (sk-... ile başlayan): " OPENAI_API_KEY
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
        echo ".env dosyası oluşturuldu ve OpenAI API Key kaydedildi."
    else
        echo "OpenAI API Key girilmedi. .sor komutu çalışmayacaktır."
    fi
else
    echo "Mevcut .env dosyası kullanılacak."
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."

python3 userbot.py
