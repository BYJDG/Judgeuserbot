#!/bin/bash

clear
echo -e "\033[1;36mJudgeUserBot Kurulum Scripti\033[0m"
echo -e "\033[1;33mhttps://github.com/BYJDG/Judgeuserbot\033[0m"
echo "-------------------------------------------"

# 1. Sistem Güncellemeleri
echo -e "\033[1;34m[1/4] Sistem güncellemeleri kontrol ediliyor...\033[0m"
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi wget

# 2. Repo İşlemleri
echo -e "\033[1;34m[2/4] Repo güncelleniyor...\033[0m"
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
else
    cd Judgeuserbot
    git reset --hard
    git pull origin main
fi

# 3. Config Dosyası Kontrolü
echo -e "\033[1;34m[3/4] Config dosyası kontrol ediliyor...\033[0m"
if [ ! -f "config.py" ]; then
    wget -q https://raw.githubusercontent.com/BYJDG/Judgeuserbot/main/config.py.example -O config.py
    echo -e "\033[1;31m❗ config.py oluşturuldu, lütfen API bilgilerini girin!\033[0m"
    nano config.py
elif grep -q "API_ID = 1234567" config.py; then
    echo -e "\033[1;31m❗ HATA: API bilgileri eksik!\033[0m"
    echo "Lütfen config.py dosyasını düzenleyin:"
    echo "1. nano config.py"
    echo "2. API_ID ve API_HASH değerlerini girin"
    echo "3. CTRL+X -> Y -> Enter ile kaydedin"
    exit 1
fi

# 4. Session Yönetimi
echo -e "\033[1;34m[4/4] Oturum kontrolü yapılıyor...\033[0m"
session_name=$(grep "session_name =" userbot.py | awk -F"'" '{print $2}')

if [ -f "$session_name.session" ]; then
    echo -e "\033[1;32m✔ Mevcut oturum bulundu: $session_name.session\033[0m"
    while true; do
        read -p "Mevcut oturumla devam etmek istiyor musunuz? (y/n): " choice
        case $choice in
            [Yy]* )
                echo "Mevcut oturumla devam ediliyor..."
                break
                ;;
            [Nn]* )
                rm -f "$session_name.session"
                echo "Yeni oturum oluşturulacak..."
                break
                ;;
            * )
                echo "Lütfen y veya n girin!"
                ;;
        esac
    done
else
    echo "Yeni oturum oluşturulacak..."
fi

# Gerekli Paketler
pip install -r requirements.txt

# Botu Başlat
echo -e "\n\033[1;32m✅ Kurulum tamamlandı! Bot başlatılıyor...\033[0m"
python userbot.py
