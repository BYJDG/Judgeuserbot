#!/bin/bash

clear
echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Güncelleme ve gerekli paketler
pkg update -y
pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Değişkenler
REPO="https://github.com/BYJDG/Judgeuserbot"
DIR="Judgeuserbot"
CONFIG_FILE="$DIR/config.py"

# Eğer klasör yoksa klonla, varsa güncelle
if [ ! -d "$DIR" ]; then
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone $REPO
else
    echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
    cd $DIR && git pull origin main && cd ..
fi

echo "Gerekli Python paketleri yükleniyor..."
pip install -r $DIR/requirements.txt

# Oturum dosyası var mı kontrol et
SESSION_FILES=$(ls $DIR/*.session 2>/dev/null)

if [ -n "$SESSION_FILES" ]; then
    echo "Kayıtlı bir oturum bulundu."
    read -p "Mevcut oturumla devam etmek ister misiniz? (Y/n): " answer
    if [[ "$answer" == "n" || "$answer" == "N" ]]; then
        echo "Eski oturum dosyaları siliniyor..."
        rm -f $DIR/*.session $DIR/*.session-journal
        NEW_SESSION=true
    else
        echo "Mevcut oturumla devam ediliyor."
        NEW_SESSION=false
    fi
else
    NEW_SESSION=true
fi

if [ "$NEW_SESSION" = true ]; then
    echo "Yeni oturum oluşturulacak."
    # API bilgilerini al
    read -p "Lütfen Telegram API bilgilerinizi giriniz." 
    read -p "API ID: " API_ID
    read -p "API HASH: " API_HASH
    read -p "Session adı (örnek: session): " SESSION_NAME
    read -p "Admin kullanıcı adı (örn: byjudgee): " ADMIN_USERNAME
    read -p "Admin kullanıcı ID'si (örnek: 1486645014): " ADMIN_ID

    # Config dosyası oluştur
    cat > $CONFIG_FILE << EOF
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "$SESSION_NAME"
admin_username = "$ADMIN_USERNAME"
admin_id = $ADMIN_ID
EOF
else
    echo "Config dosyanızın mevcut olduğundan emin olun."
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Uyarı: Config dosyası bulunamadı! Kurulum tamamlanamayabilir."
    fi
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."

cd $DIR
python3 userbot.py
