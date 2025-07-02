#!/bin/bash

clear
echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"
echo "==========================================="

# Gerekli paketler
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi wget

# Repo işlemleri
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
else
    cd Judgeuserbot
    git pull origin main
fi

# Config dosyası kontrolü
if [ ! -f "config.py" ]; then
    wget https://raw.githubusercontent.com/BYJDG/Judgeuserbot/main/config.py.example -O config.py
    echo "Örnek config dosyası oluşturuldu, lütfen düzenleyin!"
    nano config.py
fi

# API bilgilerini kontrol et
if grep -q "API_ID = 1234567" config.py; then
    echo -e "\n\033[1;31mHATA: API bilgileri gerekli!\033[0m"
    echo "1. https://my.telegram.org adresinden API bilgilerinizi alın"
    echo "2. config.py dosyasını düzenleyin:"
    echo "   nano config.py"
    echo "3. API_ID ve API_HASH değerlerini girin"
    exit 1
fi

# Gerekli kütüphaneler
pip install -r requirements.txt

# Session yönetimi
session_name=$(grep "session_name =" userbot.py | awk -F"'" '{print $2}')
if [ -f "$session_name.session" ]; then
    echo -e "\n\033[1;33mMevcut oturum bulundu:\033[0m $session_name.session"
    read -p "Yeni oturum oluşturmak istiyor musunuz? (E/H): " choice
    if [[ "$choice" =~ [Ee] ]]; then
        rm "$session_name.session"
        echo "Yeni oturum oluşturulacak..."
    fi
fi

# Botu başlat
echo -e "\n\033[1;32mKurulum tamamlandı! Bot başlatılıyor...\033[0m"
python userbot.py
