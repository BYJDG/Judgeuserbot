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

# Session dosyası kontrolü
if [ -f "judge_session.session" ]; then
    read -p "Kayıtlı oturum bulundu. Devam etmek istiyor musunuz? (y/n): " SESSION_CHOICE
    if [ "$SESSION_CHOICE" != "y" ]; then
        echo "Oturum siliniyor..."
        rm judge_session.session
        read -p "API ID: " API_ID
        read -p "API HASH: " API_HASH

        cat > config.py << EOL
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
admin_username = "byjudgee"
admin_id = 1486645014
EOL
        echo "Config dosyası oluşturuldu."
    else
        echo "Kayıtlı oturum kullanılacak."
    fi
else
    echo "Lütfen Telegram API bilgilerinizi giriniz."
    read -p "API ID: " API_ID
    read -p "API HASH: " API_HASH

    cat > config.py << EOL
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
admin_username = "byjudgee"
admin_id = 1486645014
EOL
    echo "Config dosyası oluşturuldu."
fi

# .env kontrolü
if [ -f ".env" ]; then
    read -p ".env dosyası bulundu. Yeniden oluşturulsun mu? (y/n): " ENV_CHOICE
    if [ "$ENV_CHOICE" = "y" ]; then
        read -p "OpenAI API key'inizi giriniz (örnek: sk-...): " OPENAI_KEY
        echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
        echo ".env dosyası yeniden oluşturuldu."
    else
        echo "Var olan .env kullanılacak."
    fi
else
    read -p "OpenAI API key'inizi giriniz (örnek: sk-...): " OPENAI_KEY
    echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
    echo ".env dosyası oluşturuldu."
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
