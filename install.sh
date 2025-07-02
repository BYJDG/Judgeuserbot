#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Paketleri güncelle
pkg update -y && pkg upgrade -y

# Gerekli paketleri kur
pkg install python git ffmpeg libffi -y

# Repo varsa güncelle, yoksa klonla
if [ -d "Judgeuserbot" ]; then
    echo "Judgeuserbot klasörü zaten var, güncelleniyor..."
    cd Judgeuserbot && git pull
else
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
fi

# Python paketlerini kur
pip install -r requirements.txt

# Oturum dosyası kontrolü
SESSION_FILE="session.session"
if [ -f "$SESSION_FILE" ] || [ -f "$SESSION_FILE-journal" ]; then
    echo -n "Zaten kayıtlı bir oturumunuz mevcut. Yeniden giriş yapmak ister misiniz? (Y/n): "
    read -r answer
    if [[ "$answer" == "Y" || "$answer" == "y" ]]; then
        echo "Eski oturum siliniyor, yeni oturum oluşturulacak..."
        rm -f session.session session.session-journal
        python3 userbot.py
    elif [[ "$answer" == "N" || "$answer" == "n" || -z "$answer" ]]; then
        echo "Mevcut oturumdan devam ediliyor..."
        python3 userbot.py
    else
        echo "Geçersiz giriş. Mevcut oturumdan devam ediliyor..."
        python3 userbot.py
    fi
else
    echo "Yeni oturum oluşturulacak."
    python3 userbot.py
fi
