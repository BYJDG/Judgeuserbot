#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Paket güncelleme & kurulum
pkg update -y
pkg upgrade -y
pkg install python git ffmpeg libffi -y

# Repo klonlama veya güncelleme
if [ -d "Judgeuserbot" ]; then
  echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
  cd Judgeuserbot && git pull
  cd ..
else
  echo "JudgeUserBot repozitorisi klonlanıyor..."
  git clone https://github.com/BYJDG/Judgeuserbot.git
fi

# Python paketleri kurulumu
pip install -r Judgeuserbot/requirements.txt

# config.py kontrolü ve oluşturulması
if [ ! -f "Judgeuserbot/config.py" ]; then
  echo "config.py dosyası bulunamadı, varsayılan config.py oluşturuluyor..."
  cat > Judgeuserbot/config.py <<EOL
api_id = 123456
api_hash = "your_api_hash_here"
owner_username = "byjudgee"
session_name = "session"
EOL
  echo "Lütfen Judgeuserbot/config.py dosyasını düzenleyin ve gerçek API bilgilerinizi girin."
fi

# Session kontrolü ve kullanıcıya sorulması
SESSION_PATH="Judgeuserbot/session.session"
if [ -f "$SESSION_PATH" ]; then
  echo "Zaten kayıtlı bir session dosyanız var."
  read -p "Kayıtlı session ile devam etmek ister misiniz? (Y/n): " answer
  if [[ "$answer" == "n" || "$answer" == "N" ]]; then
    echo "Eski session dosyaları siliniyor..."
    rm -f Judgeuserbot/*.session Judgeuserbot/*.session-journal
    echo "Yeni oturum oluşturulacak."
  else
    echo "Kayıtlı session ile devam edilecek."
  fi
else
  echo "Yeni oturum oluşturulacak."
fi

# Bot başlatma
echo "Kurulum tamamlandı. Bot başlatılıyor..."
python3 Judgeuserbot/userbot.py
