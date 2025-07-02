#!/data/data/com.termux/files/usr/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Paketler
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi

pip install --upgrade pip
pip install telethon

# Repo varsa yedekle
if [ -d "Judgeuserbot" ]; then
    echo "Eski Judgeuserbot klasörü bulunuyor, yedekleniyor..."
    mv Judgeuserbot Judgeuserbot_backup_$(date +%s)
fi

git clone https://github.com/BYJDG/Judgeuserbot.git
cd Judgeuserbot || exit

# Session dosyaları var mı kontrol et
session_files=$(ls *.session 2>/dev/null)

if [ ! -z "$session_files" ]; then
    echo "Zaten kayıtlı oturum dosyaları bulundu:"
    echo "$session_files"
    echo "Yeniden giriş yapmak ister misiniz? (Y/n)"
    # Burada kullanıcı girişi bekle
    read answer
    case $answer in
        [Yy]* )
            echo "Eski oturum dosyaları siliniyor..."
            rm -f *.session
            rm -f *.session-journal 2>/dev/null
            ;;
        * )
            echo "Var olan oturum kullanılacak."
            ;;
    esac
fi

# Config alma
read -p "Telegram API ID'nizi girin: " api_id
read -p "Telegram API HASH'inizi girin: " api_hash
read -p "Bot sahibi Telegram kullanıcı adınızı (örn: byjudgee) girin: " owner_username

# config.json yaz
cat > config.json <<EOL
{
  "api_id": $api_id,
  "api_hash": "$api_hash",
  "owner_username": "$owner_username"
}
EOL

echo "Kurulum tamamlandı. Bot başlatılıyor..."
python3 userbot.py
