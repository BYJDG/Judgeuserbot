#!/bin/bash

clear
echo -e "\033[1;36m[ JudgeUserBot Kurulum ]\033[0m"
echo "-------------------------------------"

# 1. Gerekli paketler
echo -e "\033[1;33m● Paketler kontrol ediliyor...\033[0m"
pkg update -y
pkg install -y python git ffmpeg libffi wget

# 2. Repo işlemleri
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
else
    cd Judgeuserbot
    git pull origin main
fi

# 3. Config kontrolü
if [ ! -f "config.py" ]; then
    wget -q https://raw.githubusercontent.com/BYJDG/Judgeuserbot/main/config.py.example -O config.py
    echo -e "\033[1;31m✘ Lütfen config.py dosyasını düzenleyin (API bilgileri gerekli)\033[0m"
    nano config.py
    exit 1
fi

# 4. Session yönetimi (DÜZELTİLMİŞ KISIM)
SESSION_FILE="judge.session"

if [ -f "$SESSION_FILE" ]; then
    echo -e "\033[1;32m✔ Mevcut oturum bulundu!\033[0m"
    echo -e "Dosya: \033[1;33m$SESSION_FILE\033[0m"
    echo -e "Boyut: \033[1;33m$(du -h "$SESSION_FILE" | cut -f1)\033[0m"
    
    while true; do
        read -p "Mevcut oturumla devam etmek ister misiniz? (y/n): " choice
        case $choice in
            [Yy]* )
                echo "Mevcut oturumla devam ediliyor..."
                break
                ;;
            [Nn]* )
                rm -f "$SESSION_FILE"
                echo "Eski oturum silindi. Yeni oturum oluşturulacak..."
                break
                ;;
            * )
                echo "Lütfen y (evet) veya n (hayır) girin!"
                ;;
        esac
    done
else
    echo "Yeni oturum oluşturulacak..."
fi

# 5. Bağımlılıklar
pip install -r requirements.txt

# 6. Botu başlat
echo -e "\n\033[1;32m✓ Kurulum tamamlandı! Bot başlatılıyor...\033[0m"
python userbot.py
