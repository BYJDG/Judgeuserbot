#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Termux mirror uyarısı (kullanıcıya hatırlatma)
echo "No mirror or mirror group selected. İstersen 'termux-change-repo' komutuyla mirror ayarlarını yapabilirsin."

pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

echo "Gerekli paketler yüklendi."

# Repo klonla veya güncelle
if [ -d "Judgeuserbot" ]; then
    echo "Repo zaten var, güncelleniyor..."
    cd Judgeuserbot
    git pull
    cd ..
else
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
fi

cd Judgeuserbot

# Gerekli python paketlerini yükle
pip install -r requirements.txt

# Config oluşturma
echo "Lütfen Telegram API bilgilerinizi giriniz."
read -p "API ID: " API_ID
read -p "API HASH: " API_HASH
read -p "Botun admin kullanıcı adını giriniz (örn: byjudgee): " ADMIN_USERNAME
read -p "Admin kullanıcı ID'sini giriniz (örn: 1486645014): " ADMIN_ID

# İstersen owners_ids gir
read -p "Ek yetkili kullanıcı ID'leri (virgül ile ayrılmış, boş bırakabilirsin): " OWNERS_INPUT

# Format owners_ids
if [ -z "$OWNERS_INPUT" ]; then
    OWNERS_IDS="[$ADMIN_ID]"
else
    # Virgüllü listeyi python listesine çevir
    OWNERS_IDS="[$ADMIN_ID"
    IFS=',' read -ra ADDR <<< "$OWNERS_INPUT"
    for i in "${ADDR[@]}"; do
        OWNERS_IDS+=",${i// /}"
    done
    OWNERS_IDS+="]"
fi

# config.py yaz
cat > config.py << EOL
api_id = $API_ID
api_hash = "$API_HASH"
session_name = "judge_session"
admin_username = "$ADMIN_USERNAME"
admin_id = $ADMIN_ID
owners_ids = $OWNERS_IDS
EOL

echo "Config dosyası oluşturuldu."

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
