#!/bin/bash

echo "🔧 JudgeUserbot Sadeleştirilmiş Kurulumu Başlatılıyor..."

# Gerekli araçlar
sudo apt update -y > /dev/null 2>&1
sudo apt install -y python3 python3-pip git tmux > /dev/null 2>&1

# Repo indir
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git  -b BYJDG-patch-1 > /dev/null 2>&1
else
    cd Judgeuserbot && git pull > /dev/null 2>&1 && cd ..
fi

cd Judgeuserbot

# config.py yoksa oluştur
if [ ! -f "config.py" ]; then
    touch config.py
fi

# Session dosyası kontrolü
if [ -f "session.session" ]; then
    echo "✅ Kayıtlı bir session dosyası bulundu."
    echo "API ID ve HASH zaten girilmiş olmalı. Onaylıyor musun? (y/n)"
    read -r confirm
    if [[ "$confirm" != "y" ]]; then
        echo "❌ Kurulum iptal edildi."
        exit 1
    fi
else
    echo "⚠️ Session dosyası bulunamadı."
    echo "Yeni session oluşturmak ister misin? (y/n)"
    read -r create_session
    if [[ "$create_session" != "y" ]]; then
        echo "❌ Kurulum iptal edildi."
        exit 1
    fi

    echo -n "🔐 API ID: "
    read api_id
    echo -n "🔐 API HASH: "
    read api_hash

    echo "⚙️ config.py oluşturuluyor..."
    echo "API_ID = '$api_id'" > config.py
    echo "API_HASH = '$api_hash'" >> config.py
fi

# Gerekli kütüphaneler
pip3 install -r requirements.txt > /dev/null 2>&1

# Eski tmux oturumu varsa kapat
if tmux has-session -t judgebot 2>/dev/null; then
    tmux kill-session -t judgebot
fi

# Botu başlat
echo "🚀 Bot başlatılıyor..."
tmux new -d -s judgebot "python3 userbot.py"

echo "✅ Kurulum tamamlandı!"
echo "Bot arka planda çalışıyor. tmux oturumuna katılmak için: tmux attach -t judgebot"
