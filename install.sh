#!/bin/bash

clear
echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"
echo "==========================================="

# Paket güncellemeleri
pkg update -y
pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Repo kontrolü ve güncelleme
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
else
    cd Judgeuserbot
    git pull origin main
fi

# Config dosyası kontrolü
if [ ! -f "config.py" ]; then
    cp config.py.example config.py
fi

# API bilgilerini al
get_api_credentials() {
    echo -e "\n\033[1;36mTelegram API Bilgilerinizi Alın:\033[0m"
    echo "1. https://my.telegram.org adresine gidin"
    echo "2. 'API Development Tools' bölümüne girin"
    echo "3. 'App title' ve 'Short name' doldurup uygulama oluşturun"
    echo ""
}

# API ID ve HASH kontrolü
if grep -q 'API_ID = 1234567' config.py || grep -q 'API_HASH = "abcdefg"' config.py; then
    get_api_credentials
    read -p "API_ID: " api_id
    read -p "API_HASH: " api_hash
    sed -i "s/API_ID = 1234567/API_ID = $api_id/" config.py
    sed -i "s/API_HASH = \"abcdefg\"/API_HASH = \"$api_hash\"/" config.py
fi

# Gerekli Python paketleri
pip install -r requirements.txt

# Session yönetimi
session_name=$(grep "session_name =" userbot.py | awk -F"'" '{print $2}')
if [ -f "$session_name.session" ]; then
    echo -e "\n\033[1;33mMevcut oturum dosyası bulundu:\033[0m $session_name.session"
    read -p "Yeni hesap ile giriş yapmak istiyor musunuz? (E/H): " choice
    if [ "$choice" = "E" ] || [ "$choice" = "e" ]; then
        rm "$session_name.session"
        echo "Yeni oturum oluşturulacak..."
    else
        echo "Mevcut oturumla devam ediliyor..."
    fi
fi

# Botu başlatma
echo -e "\n\033[1;32mKurulum tamamlandı! Bot başlatılıyor...\033[0m"
python userbot.py
