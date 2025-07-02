# JudgeUserbot - Telegram Userbot

## Açıklama

JudgeUserbot, Telegram üzerinde çalışan basit ve modüler bir kullanıcı botudur.  
AFK modu, filtreli otomatik cevaplar ve temel komutlarla donatılmıştır.

## Kurulum

1. Repoyu klonlayın veya dosyaları indirin.
2. Termux ya da Ubuntu terminalinde:
    ```bash
    bash setup.sh
    ```
3. `config.json` dosyasını açıp kendi `api_id` ve `api_hash` değerlerinizi girin.  
   (https://my.telegram.org/apps adresinden alabilirsiniz)

4. Botu başlatın:
    ```bash
    python userbot.py
    ```

## Komutlar

- `.alive` → Botun çalıştığını kontrol eder.
- `.afk <sebep>` → AFK modunu açar.
- `.back` → AFK modunu kapatır.
- `.filter <mesaj> <cevap>` → Otomatik cevap ekler.
- `.unfilter <mesaj>` → Otomatik cevabı kaldırır.
- `.judge` → Yardım mesajını gösterir.

## Önemli Notlar

- Bot sadece kendi Telegram hesabınızda çalışır.
- AFK modu açıkken, her kullanıcıya sadece bir kez cevap verir.
- Filtreli cevaplar AFK modunda çalışmaz.

---

Geliştirmeler ve destek için iletişim: [t.me/Samilbots](https://t.me/Samilbots)
