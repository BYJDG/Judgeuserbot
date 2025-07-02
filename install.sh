#!/bin/bash

clear
echo -e "\033[1;36m[ JUDGE USERBOT KURULUM ]\033[0m"
echo "-------------------------------------"

# 1. Sistem güncellemeleri
echo -e "\033[1;33m● Sistem güncellemeleri yapılıyor...\033[0m"
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi wget nano

# 2. Repo işlemleri
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
else
    cd Judgeuserbot
    git reset --hard
    git pull origin main
fi

# 3. Config dosyası kontrolü
if [ ! -f "config.py" ]; then
    cp config.py.example config.py
    echo -e "\033[1;31m✘ Lütfen API bilgilerini girin!\033[0m"
    nano config.py
    exit 1
elif grep -q "API_ID = 1234567" config.py; then
    echo -e "\033[1;31m✘ API bilgileri eksik!\033[0m"
    echo "Lütfen config.py dosyasını düzenleyin:"
    echo "1. nano config.py"
    echo "2. API_ID ve API_HASH girin"
    echo "3. CTRL+X -> Y -> Enter ile kaydedin"
    exit 1
fi

# 4. Session kontrolü (KESİN ÇÖZÜM)
SESSION_FILE="judge.session"

if [ -f "$SESSION_FILE" ]; then
    echo -e "\033[1;32m✔ Mevcut oturum dosyası bulundu!\033[0m"
    echo -e "Dosya: \033[1;33m$SESSION_FILE\033[0m"
    echo -e "Boyut: \033[1;33m$(du -h "$SESSION_FILE" | cut -f1)\033[0m"
    
    # Soru sorma kısmı (DÜZELTİLDİ)
    PS3='Mevcut oturumla devam etmek ister misiniz? '
    options=("Evet" "Hayır (Yeni oturum oluştur)")
    select opt in "${options[@]}"
    do
        case $opt in
            "Evet")
                echo "Mevcut oturumla devam ediliyor..."
                break
                ;;
            "Hayır (Yeni oturum oluştur)")
                rm -f "$SESSION_FILE"
                echo "Eski oturum silindi. Yeni giriş yapılacak..."
                break
                ;;
            *) echo "Geçersiz seçim! Lütfen 1 veya 2 yazın";;
        esac
    done
else
    echo "Yeni oturum oluşturulacak..."
fi

# 5. Bağımlılıklar
pip install -r requirements.txt

# 6. Botu başlat
echo -e "\n\033[1;32m✓ Bot başlatılıyor...\033[0m"
python userbot.py
