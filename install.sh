#!/data/data/com.termux/files/usr/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

pkg update -y
pkg upgrade -y
pkg install -y python git ffmpeg libffi

pip install --upgrade pip
pip install telethon

if [ -d "Judgeuserbot" ]; then
    echo "Eski Judgeuserbot klasörü bulunuyor, yedekleniyor..."
    mv Judgeuserbot Judgeuserbot_backup_$(date +%s)
fi

git clone https://github.com/BYJDG/Judgeuserbot.git
cd Judgeuserbot || exit

# **Burada kesin session dosyalarını bul ve sor**
session_files=$(ls *.session 2>/dev/null)
if [ -n "$session_files" ]; then
    echo "Zaten kayıtlı oturum dosyaları bulundu: $session_files"
    echo "Yeniden giriş yapmak ister misiniz? (Y/n)"
    read -r answer
    if [[ $answer == "Y" || $answer == "y" ]]; then
        echo "Eski oturum dosyaları siliniyor..."
        rm -f *.session
        rm -f *.session-journal 2>/dev/null
    else
        echo "Var olan oturum kullanılacak."
    fi
fi

echo "Telegram API ID'nizi girin:"
read -r api_id

echo "Telegram API HASH'inizi girin:"
read -r api_hash

echo "Bot sahibi Telegram kullanıcı adınızı (örn: byjudgee) girin:"
read -r owner_username

cat > config.json << EOL
{
  "api_id": $api_id,
  "api_hash": "$api_hash",
  "owner_username": "$owner_username"
}
EOL

echo "Kurulum tamamlandı. Bot başlatılıyor..."
python3 userbot.py
