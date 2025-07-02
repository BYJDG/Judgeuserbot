#!/bin/bash

clear
echo -e "\033[1;36m[ JUDGE USERBOT KURULUM ]\033[0m"
echo "-------------------------------------"

# 1. Gerekli paketler
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi

# 2. Repo işlemleri
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
else
    cd Judgeuserbot
    git reset --hard
    git pull origin main
fi

# 3. Config kontrolü
if [ ! -f "config.py" ]; then
    cp config.py.example config.py
    echo -e "\033[1;31m✘ Lütfen config.py dosyasını düzenleyin!\033[0m"
    nano config.py
    exit 1
fi

# 4. Session yönetimi (GÜNCELLENMİŞ)
SESSION_FILE="judge.session"

if [ -f "$SESSION_FILE" ]; then
    echo -e "\033[1;32m✔ Mevcut oturum bulundu:\033[0m"
    echo -e "Dosya: \033[1;33m$SESSION_FILE\033[0m"
    echo -e "Boyut: \033[1;33m$(du -h "$SESSION_FILE" | cut -f1)\033[0m"
    
    # Kullanıcı seçimi
    while true; do
        read -p "Mevcut oturumla devam etmek istiyor musunuz? (e/h): " choice
        case $choice in
            [Ee]* )
                echo "Mevcut oturumla devam ediliyor..."
                SESSION_CHOICE="existing"
                break
                ;;
            [Hh]* )
                rm -f "$SESSION_FILE"
                echo "Yeni oturum oluşturulacak..."
                SESSION_CHOICE="new"
                break
                ;;
            * )
                echo "Lütfen 'e' (evet) veya 'h' (hayır) girin!"
                ;;
        esac
    done
else
    echo "Yeni oturum oluşturulacak..."
    SESSION_CHOICE="new"
fi

# 5. Bağımlılıklar
pip install -r requirements.txt

# 6. Botu başlat
echo -e "\n\033[1;32m✓ Bot başlatılıyor...\033[0m"
if [ "$SESSION_CHOICE" = "existing" ]; then
    python userbot.py --existing-session
else
    python userbot.py
fi
