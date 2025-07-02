#!/data/data/com.termux/files/usr/bin/bash

clear
echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Gerekli paketleri yükle (pip zaten python ile geliyor termuxta)
pkg update -y
pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Repo klonla veya güncelle
if [ -d "Judgeuserbot" ]; then
  echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
  cd Judgeuserbot
  git pull
else
  echo "JudgeUserBot repozitorisi klonlanıyor..."
  git clone https://github.com/BYJDG/Judgeuserbot.git
  cd Judgeuserbot
fi

# Gerekli python paketleri
echo "Gerekli Python paketleri yükleniyor..."
pip install -r requirements.txt

# Session dosyasını kontrol et
SESSION_FILE="session.session"
if [ -f "$SESSION_FILE" ]; then
  echo "Zaten kayıtlı bir oturum dosyanız var."
  echo "Yeniden giriş yapmak ister misiniz? (Y/n):"
  read -r answer
  if [[ "$answer" == "Y" || "$answer" == "y" ]]; then
    echo "Eski oturum dosyası siliniyor..."
    rm -f "$SESSION_FILE" "$SESSION_FILE-journal"
  else
    echo "Mevcut oturum dosyası kullanılacak."
  fi
else
  echo "Yeni oturum oluşturulacak."
fi

# API bilgileri isteme (config yoksa)
if [ ! -f "config.json" ]; then
  echo "Lütfen Telegram API bilgilerinizi giriniz."
  read -p "API ID: " api_id
  read -p "API HASH: " api_hash
  echo "{" > config.json
  echo "  \"api_id\": \"$api_id\"," >> config.json
  echo "  \"api_hash\": \"$api_hash\"" >> config.json
  echo "}" >> config.json
fi

echo "Kurulum tamamlandı. Bot başlatılıyor..."

python3 userbot.py
