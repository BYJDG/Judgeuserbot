#!/data/data/com.termux/files/usr/bin/bash

echo "📦 JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Gerekli paketleri yükle
pkg update -y && pkg upgrade -y
pkg install python -y
pkg install git -y
pkg install ffmpeg -y
pkg install libffi -y

# Pip engelini kaldır
termux-change-repo
yes | pip install --upgrade pip setuptools wheel

# Reponun zaten var olup olmadığını kontrol et
if [ -d "Judgeuserbot" ]; then
  echo "❗ Judgeuserbot klasörü zaten var. Devam ediliyor..."
else
  echo "📥 Reposu klonlanıyor..."
  git clone https://github.com/BYJDG/Judgeuserbot.git
fi

cd Judgeuserbot

# Session dosyası kontrolü
if [ -f "session.session" ]; then
    echo "🟡 Kayıtlı bir oturum bulundu."
    read -p "Bu oturumu kullanmak ister misiniz? (Y/n): " use_session
    if [[ "$use_session" =~ ^[Yy]$ ]]; then
        echo "🔁 Mevcut oturumla devam ediliyor."
    else
        rm session.session*
        echo "🔄 Yeni giriş yapılacak."
    fi
fi

# API bilgilerini al
read -p "🆔 API ID: " api_id
read -p "🔑 API Hash: " api_hash

# config.json oluştur
cat > config.json <<EOF
{
  "api_id": $api_id,
  "api_hash": "$api_hash"
}
EOF

# Gerekli Python paketleri
pip install -r requirements.txt

# Botu başlat
echo "🚀 Kurulum tamamlandı. Bot başlatılıyor..."
python userbot.py
