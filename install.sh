#!/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Paketleri güncelle ve kurulumları yap
pkg update -y && pkg upgrade -y
pkg install python git ffmpeg libffi -y

# Reponun klasörü
REPO_DIR="Judgeuserbot"

# Repon varsa güncelle yoksa klonla
if [ -d "$REPO_DIR" ]; then
  echo "$REPO_DIR dizini zaten mevcut, güncelleniyor..."
  cd $REPO_DIR
  git pull
  cd ..
else
  echo "JudgeUserBot repozitorisi klonlanıyor..."
  git clone https://github.com/BYJDG/Judgeuserbot.git
fi

# Gerekli python paketlerini yükle
pip install -r $REPO_DIR/requirements.txt

# Config dosyası oluşturma fonksiyonu
create_config() {
  echo "Lütfen Telegram API bilgilerinizi giriniz."
  read -p "API ID: " api_id
  read -p "API HASH: " api_hash
  read -p "Admin kullanıcı adı (örn: byjudgee): " admin_user

  cat > $REPO_DIR/config.py <<EOF
api_id = $api_id
api_hash = "$api_hash"
session_name = "session"
global_admin_username = "$admin_user"
global_admin_id = 1486645014  # ByJudge'nin Telegram ID'si sabit
EOF
}

# Oturum kontrolü ve soru sorma
if [ -f "$REPO_DIR/session.session" ]; then
  echo "Kayıtlı bir oturum bulundu."
  read -p "Mevcut oturumla devam etmek ister misiniz? (Y/n): " answer
  case "$answer" in
    [Yy]* ) echo "Mevcut oturumla devam ediliyor.";;
    [Nn]* ) 
      echo "Yeni oturum oluşturmak için eski oturum dosyaları siliniyor..."
      rm -f $REPO_DIR/session.session $REPO_DIR/session.session-journal
      create_config
      ;;
    * ) echo "Geçersiz seçenek. Mevcut oturumla devam ediliyor.";;
  esac
else
  echo "Yeni oturum oluşturulacak."
  create_config
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."
cd $REPO_DIR
python3 userbot.py
