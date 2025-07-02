#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

if [ -d "Judgeuserbot" ]; then
    echo "Judgeuserbot klasörü zaten var, güncelleniyor..."
    cd Judgeuserbot && git pull
else
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
fi

pip install -r requirements.txt

SESSION_FILE="session.session"
if [ -f "$SESSION_FILE" ] || [ -f "$SESSION_FILE-journal" ]; then
    echo "Zaten kayıtlı bir oturumunuz mevcut."
    echo "Yeniden giriş yapmak ister misiniz? (Y/n)"
    stty sane
    read answer
    case "$answer" in
        [Yy]* )
            echo "Eski oturum siliniyor, yeni oturum oluşturulacak..."
            rm -f session.session session.session-journal
            python3 userbot.py
            ;;
        [Nn]* | "" )
            echo "Mevcut oturumdan devam ediliyor..."
            python3 userbot.py
            ;;
        * )
            echo "Geçersiz giriş. Mevcut oturumdan devam ediliyor..."
            python3 userbot.py
            ;;
    esac
else
    echo "Yeni oturum oluşturulacak."
    python3 userbot.py
fi
