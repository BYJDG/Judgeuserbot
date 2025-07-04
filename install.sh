#!/data/data/com.termux/files/usr/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Gerekli paketleri yükle
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Python bağımlılıklarını yükle
pip install --upgrade pip

# Repo kontrolü
if [ -d "Judgeuserbot" ]; then
    echo "Judgeuserbot dizini zaten mevcut, güncelleniyor..."
    cd Judgeuserbot
    git pull
else
    echo "JudgeUserBot repozitorisi klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
fi

# Gerekli python kütüphanelerini yükle
pip install -r requirements.txt

# Kayıtlı session kontrolü
if [ -f "session.session" ]; then
    echo "Kayıtlı bir oturum bulundu."
    read -p "Mevcut oturumla devam etmek ister misiniz? (Y/n): " choice
    if [[ "$choice" =~ ^[Yy]$ || "$choice" == "" ]]; then
        echo "Mevcut oturumla devam ediliyor."
        session_exist=true
    else
        echo "Yeni oturum oluşturulacak."
        rm -f session.session
        session_exist=false
    fi
else
    session_exist=false
fi

# Eğer config yoksa ya da yeni oturum seçildiyse config ayarlarını al
if [[ "$session_exist" = false || ! -f "config.py" ]]; then
    echo "Lütfen Telegram API bilgilerinizi giriniz."
    read -p "API ID: " api_id
    read -p "API HASH: " api_hash
    read -p "Botun kurulacağı Telegram kullanıcı adı (örn: byjudgee): " admin_username

    # config.py dosyasını oluştur
    cat <<EOF > config.py
api_id = $api_id
api_hash = "$api_hash"
session_name = "session"
admin_username = "$admin_username"
admin_id = 1486645014  # Sadece byjudgee için özel admin komutu
EOF
fi

echo "Kurulum tamamlandı! Bot başlatılıyor..."
python userbot.py
