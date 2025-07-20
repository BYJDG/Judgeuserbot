#!/bin/bash

# JudgeUserbot Kurulum Betiği

echo "🔍 JudgeUserbot Kurulumuna Hoşgeldin"

# Gerekli araçlar
echo "🔧 Gerekli paketler kuruluyor..."
sudo apt update -y > /dev/null 2>&1
sudo apt install -y python3 python3-pip git tmux > /dev/null 2>&1

# Repo indirme
if [ ! -d "Judgeuserbot" ]; then
    echo "📥 Repo indiriliyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git  > /dev/null 2>&1
else
    echo "🔄 Repo zaten mevcut, güncelleniyor..."
    cd Judgeuserbot && git pull > /dev/null 2>&1 && cd ..
fi

cd Judgeuserbot

# config.py kontrolü
if [ ! -f "config.py" ]; then
    touch config.py
fi

# Session dosyası kontrolü
if [ -f "session.session" ]; then
    echo "✅ Kayıtlı bir session dosyası bulundu. Otomatik başlatılıyor..."
    echo "API ID ve API HASH zaten girilmiş olmalı. Onaylıyor musun? (y/n)"
    read -r confirm
    if [[ "$confirm" != "y" ]]; then
        echo "❌ Kurulum iptal edildi."
        exit 1
    fi

    echo "⚙️ config.py oluşturuluyor..."
    echo "API_ID = 'dummy'" >> config.py
    echo "API_HASH = 'dummy'" >> config.py
    echo "Session dosyası bulunduğundan API bilgileri otomatik dolduruldu."
else
    echo "⚠️ Session dosyası bulunamadı."
    echo "Yeni session oluşturmak ister misin? (y/n)"
    read -r create_session
    if [[ "$create_session" != "y" ]]; then
        echo "❌ Kurulum iptal edildi."
        exit 1
    fi

    echo "⚙️ Lütfen Telegram API ID ve HASH girin (session oluşturmak için)"
    echo -n "API ID: "
    read api_id
    echo -n "API HASH: "
    read api_hash

    echo "⚙️ config.py oluşturuluyor..."
    echo "API_ID = '$api_id'" > config.py
    echo "API_HASH = '$api_hash'" >> config.py
fi

# Gerekli kütüphaneler
echo "📦 Gerekli kütüphaneler kuruluyor..."
pip3 install -r requirements.txt > /dev/null 2>&1

# Botu tmux ile başlat
if tmux has-session -t judgebot 2>/dev/null; then
    echo "🔄 Eski oturum kapatılıyor..."
    tmux kill-session -t judgebot
fi

echo "🚀 Bot başlatılıyor..."
tmux new -d -s judgebot "python3 userbot.py"

echo "✅ Kurulum tamamlandı!"
echo "Bot arka planda çalışıyor. tmux oturumuna katılmak için: tmux attach -t judgebot"
