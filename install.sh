#!/data/data/com.termux/files/usr/bin/bash

echo "JudgeUserBot Kurulum Scriptine Hoşgeldiniz!"

# Bağımlılıkların kurulumu
echo "Gerekli paketler kontrol ediliyor..."
pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg libffi

# Pip kurulumu
echo "PIP kurulumu yapılıyor..."
curl -sS https://bootstrap.pypa.io/get-pip.py | python

# Gerekli Python paketleri
echo "Gerekli Python modülleri yükleniyor..."
pip install -r requirements.txt

# JudgeUserBot klasörü kontrolü
if [ ! -d "Judgeuserbot" ]; then
    echo "Repo klonlanıyor..."
    git clone https://github.com/BYJDG/Judgeuserbot.git
    cd Judgeuserbot
else
    cd Judgeuserbot
    echo "Repo zaten var, içine giriliyor..."
fi

# Oturum dosyası kontrolü
SESSION_FILE="session.session"

if [ -f "$SESSION_FILE" ]; then
    echo -n "Zaten bir oturum mevcut. Yeniden giriş yapmak ister misiniz? (Y/n): "
    read answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo "Eski oturum siliniyor..."
        rm -f "$SESSION_FILE" "$SESSION_FILE-journal"
    else
        echo "Kayıtlı oturumdan devam ediliyor..."
    fi
fi

# Giriş yapılmamışsa API bilgileri alınıyor
if [ ! -f "$SESSION_FILE" ]; then
    echo "Lütfen Telegram API bilgilerinizi giriniz."
    read -p "API ID: " api_id
    read -p "API HASH: " api_hash
    echo '{' > config.json
    echo "  \"api_id\": \"$api_id\"," >> config.json
    echo "  \"api_hash\": \"$api_hash\"" >> config.json
    echo '}' >> config.json
fi

# Bot başlatılıyor
echo "Kurulum tamamlandı. Bot başlatılıyor..."
python userbot.py
