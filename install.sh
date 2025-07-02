#!/data/data/com.termux/files/usr/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Gerekli paketlerin kurulumu
pkg update -y
pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Python paketleri
pip install --upgrade pip
pip install telethon

# Repo klonlama (varsa eskiyi yedekle)
if [ -d "Judgeuserbot" ]; then
    echo "Eski Judgeuserbot klasörü bulunuyor, yedekleniyor..."
    mv Judgeuserbot Judgeuserbot_backup_$(date +%s)
fi

git clone https://github.com/BYJDG/Judgeuserbot.git
cd Judgeuserbot || exit

# Session kontrolü
if ls *.session 1> /dev/null 2>&1; then
    echo "Zaten kayıtlı bir oturumunuz var. Yeniden giriş yapmak ister misiniz? (Y/n)"
    read -r answer
    if [[ $answer == "Y" || $answer == "y" ]]; then
        echo "Eski oturum dosyaları siliniyor..."
        rm *.session
        rm *.session-journal 2>/dev/null
    else
        echo "Var olan oturum kullanılacak."
    fi
fi

# API bilgileri ve owner username girişi
echo "Telegram API ID'nizi girin:"
read -r api_id

echo "Telegram API HASH'inizi girin:"
read -r api_hash

echo "Bot sahibi Telegram kullanıcı adınızı (örn: byjudgee) girin:"
read -r owner_username

# config.json dosyasını oluştur
cat > config.json << EOL
{
  "api_id": $api_id,
  "api_hash": "$api_hash",
  "owner_username": "$owner_username"
}
EOL

echo "Kurulum tamamlandı. Bot başlatılıyor..."
python3 userbot.py
