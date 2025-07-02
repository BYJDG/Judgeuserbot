#!/bin/bash

echo "Kurulum başlatılıyor..."

pkg update -y && pkg upgrade -y
pkg install python git -y
pip install -r requirements.txt

cp config.json.example config.json

echo "Kurulum tamamlandı. Lütfen config.json dosyasını düzenleyin ve ardından:"
echo "python userbot.py"
