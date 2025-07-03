#!/data/data/com.termux/files/usr/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

pkg update -y
pkg upgrade -y

pkg install python git ffmpeg libffi -y

if [ -d "Judgeuserbot" ]; then
  echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
  cd Judgeuserbot
  git pull
  cd ..
else
  echo "JudgeUserBot repozitorisi klonlanıyor..."
  git clone https://github.com/BYJDG/Judgeuserbot
fi

echo "Gerekli Python paketleri yükleniyor..."
pip install -r Judgeuserbot/requirements.txt

# Session kontrolü
SESSION_FILE="Judgeuserbot/session.session"

if [ -f "$SESSION_FILE" ]; then
  echo "Önceden kayıtlı oturum tespit edildi."
  read -p "Bu oturumla devam etmek ister misiniz? (Y/n): " answer
  if [[ "$answer" == "n" || "$answer" == "N" ]]; then
    echo "Eski oturum siliniyor..."
    rm -f $SESSION_FILE
    rm -f Judgeuserbot/session.session-journal
    NEW_SESSION="true"
  else
    NEW_SESSION="false"
  fi
else
  NEW_SESSION="true"
fi

if [ "$NEW_SESSION" == "true" ]; then
  echo "Lütfen Telegram API bilgilerinizi giriniz."
  read -p "API ID: " API_ID
  read -p "API HASH: " API_HASH
  read -p "Admin kullanıcı adı (örn: byjudgee): " OWNER_USERNAME

  # config.py oluşturuluyor
  cat > Judgeuserbot/config.py <<EOL
API_ID = $API_ID
API_HASH = "$API_HASH"
OWNER_USERNAME = "$OWNER_USERNAME"
session_name = "session"
EOL

  echo "Yeni oturum oluşturulacak."
else
  echo "Var olan oturum ile devam edilecek."
fi

echo "Kurulum tamamlandı. Bot başlatılıyor..."
cd Judgeuserbot
python3 userbot.py
