#!/data/data/com.termux/files/usr/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Paketleri güncelle ve gerekli olanları kur
pkg update -y
pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Python paketlerini kur
pip install telethon

# Repoyu klonla (eğer yoksa)
if [ ! -d "Judgeuserbot" ]; then
    git clone https://github.com/BYJDG/Judgeuserbot.git
else
    echo "Judgeuserbot klasörü zaten mevcut."
fi

cd Judgeuserbot

# Config bilgilerini kullanıcıdan al
read -p "API ID: " api_id
read -p "API HASH: " api_hash
read -p "Telefon numaranız (ülke kodu ile, örn: +90...): " phone
read -p "Admin kullanıcı adı (örn: byjudgee): " owner

# config.json oluştur
cat > config.json <<EOF
{
  "api_id": $api_id,
  "api_hash": "$api_hash",
  "phone": "$phone",
  "owner_username": "$owner"
}
EOF

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python3 userbot.py
