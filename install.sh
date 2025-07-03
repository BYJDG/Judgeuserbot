#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Paketleri güncelle ve yükle
pkg update -y
pkg upgrade -y
pkg install python git ffmpeg libffi -y

# Repo klonla veya güncelle
if [ -d "Judgeuserbot" ]; then
    echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
    cd Judgeuserbot && git pull && cd ..
else
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
fi

# Gerekli python paketlerini kur
pip install -r Judgeuserbot/requirements.txt

# Oturum dosyası var mı kontrol et
SESSION_FILE="Judgeuserbot/session.session"
if [ -f "$SESSION_FILE" ]; then
    echo "Zaten kayıtlı bir oturumunuz mevcut. Bu oturumla devam etmek ister misiniz? (Y/n)"
    read -r answer
    if [[ "$answer" == "n" || "$answer" == "N" ]]; then
        echo "Eski oturum siliniyor..."
        rm -f "$SESSION_FILE"
        rm -f "Judgeuserbot/session.session-journal"
        CREATE_NEW_SESSION="yes"
    else
        CREATE_NEW_SESSION="no"
    fi
else
    CREATE_NEW_SESSION="yes"
fi

# API bilgilerini al
if [ "$CREATE_NEW_SESSION" == "yes" ]; then
    echo "Lütfen Telegram API bilgilerinizi giriniz."
    read -p "API ID: " API_ID
    read -p "API HASH: " API_HASH
    read -p "Admin kullanıcı adı (örn: byjudgee): " OWNER_USERNAME

    # config.py oluştur
    cat > Judgeuserbot/config.py <<EOL
API_ID = $API_ID
API_HASH = "$API_HASH"
OWNER_USERNAME = "$OWNER_USERNAME"
SESSION_NAME = "session"
EOL

else
    echo "Eski oturumla devam ediliyor, mevcut config.py kullanılacak."
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."
cd Judgeuserbot
python3 userbot.py
