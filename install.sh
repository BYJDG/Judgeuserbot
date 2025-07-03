#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Paketleri güncelle ve kur
pkg update -y
pkg upgrade -y
pkg install python git ffmpeg libffi -y

# Repo klonla ya da güncelle
if [ -d "Judgeuserbot" ]; then
  echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
  cd Judgeuserbot && git pull
  cd ..
else
  echo "JudgeUserBot repozitorisi klonlanıyor..."
  git clone https://github.com/BYJDG/Judgeuserbot.git
fi

# Python paketlerini kur
pip install -r Judgeuserbot/requirements.txt

# Kullanıcıdan config için bilgi al
echo "Lütfen Telegram API bilgilerinizi giriniz."
read -p "API ID: " api_id
read -p "API HASH: " api_hash
read -p "Admin kullanıcı adı (örn: byjudgee): " owner_username

# config.py dosyasını oluştur
cat > Judgeuserbot/config.py <<EOL
api_id = $api_id
api_hash = "$api_hash"
owner_username = "$owner_username"
session_name = "session"
EOL

# Session kontrolü
SESSION_PATH="Judgeuserbot/session.session"
if [ -f "$SESSION_PATH" ]; then
  echo "Zaten kayıtlı bir oturum dosyanız var."
  read -p "Bu oturumla devam etmek ister misiniz? (Y/n): " answer
  if [[ "$answer" == "n" || "$answer" == "N" ]]; then
    echo "Eski oturum dosyaları siliniyor..."
    rm -f Judgeuserbot/*.session Judgeuserbot/*.session-journal
    echo "Yeni oturum oluşturulacak."
  else
    echo "Kayıtlı oturum ile devam ediliyor."
  fi
else
  echo "Yeni oturum oluşturulacak."
fi

# Botu başlat
echo "Kurulum tamamlandı. Bot başlatılıyor..."
python3 Judgeuserbot/userbot.py
