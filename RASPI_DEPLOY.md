# Raspberry Pi Deployment Guide för AIM25 Intel Bot

## Förberedelser

### System Requirements
- Raspberry Pi (Model 3/4/5)
- Raspbian OS (Raspberry Pi OS)
- Internet-anslutning
- SSH aktiverat (för remote access)

---

## 📦 Installation på Raspberry Pi

### Steg 1: SSH in till din RasPi

```bash
# Från din vanliga dator
ssh pi@raspberrypi.local
# Eller: ssh pi@[IP-adress]
```

### Steg 2: Installera dependencies

```bash
# Uppdatera system
sudo apt update
sudo apt upgrade -y

# Installera Python 3 och pip (om inte redan installerat)
sudo apt install python3 python3-pip git -y

# Installera Discord.py
pip3 install discord.py python-dotenv
```

### Steg 3: Klona projektet

**Alternativ A: Från GitHub (rekommenderat)**
```bash
cd ~
git clone https://github.com/dittanvändarnamn/aim25-intel-bot.git
cd aim25-intel-bot
```

**Alternativ B: Manuell överföring**
```bash
# På din vanliga dator, kör från projektmappen:
scp discord_bot.py requirements.txt ai_companies.db pi@raspberrypi.local:~/aim25-bot/

# På RasPi:
cd ~/aim25-bot
pip3 install -r requirements.txt
```

### Steg 4: Konfigurera botten

```bash
# Skapa .env-fil
nano .env

# Lägg in (tryck Ctrl+O för att spara, Ctrl+X för att stänga):
DISCORD_BOT_TOKEN=din_token_här
DAILY_CHANNEL_ID=ditt_channel_id
DATABASE_PATH=ai_companies.db
```

---

## 🚀 Kör botten permanent med systemd

### Skapa systemd service

```bash
# Skapa service-fil
sudo nano /etc/systemd/system/discord-bot.service
```

Lägg in följande:

```ini
[Unit]
Description=AIM25 Intel Discord Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/aim25-intel-bot
ExecStart=/usr/bin/python3 /home/pi/aim25-intel-bot/discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Aktivera och starta service

```bash
# Ladda om systemd
sudo systemctl daemon-reload

# Aktivera vid boot
sudo systemctl enable discord-bot.service

# Starta nu
sudo systemctl start discord-bot.service

# Kolla status
sudo systemctl status discord-bot.service
```

---

## 📋 Hantera botten

### Vanliga kommandon:

```bash
# Starta
sudo systemctl start discord-bot.service

# Stoppa
sudo systemctl stop discord-bot.service

# Starta om
sudo systemctl restart discord-bot.service

# Se status
sudo systemctl status discord-bot.service

# Se loggar (live)
sudo journalctl -u discord-bot.service -f

# Se senaste 100 rader
sudo journalctl -u discord-bot.service -n 100
```

---

## 🔄 Uppdatera databasen från din vanliga dator

### Metod 1: Git (Rekommenderat)

**På din vanliga dator:**
```bash
# Uppdatera databas
python build_database.py

# Commit och push
git add ai_companies.db
git commit -m "Uppdaterad databas"
git push
```

**På Raspberry Pi (automatiskt eller manuellt):**
```bash
# SSH in
ssh pi@raspberrypi.local

# Gå till projektmapp
cd ~/aim25-intel-bot

# Hämta nya ändringar
git pull

# Starta om botten
sudo systemctl restart discord-bot.service
```

### Metod 2: SCP (Direktöverföring)

**Från din vanliga dator:**
```bash
# Uppdatera databas
python build_database.py

# Kopiera till RasPi
scp ai_companies.db pi@raspberrypi.local:~/aim25-intel-bot/

# Starta om botten via SSH
ssh pi@raspberrypi.local "sudo systemctl restart discord-bot.service"
```

### Metod 3: Automatisk sync-script

Skapa på din vanliga dator:

```bash
#!/bin/bash
# update_bot_database.sh

echo "🔄 Uppdaterar databas..."
python build_database.py

echo "📤 Skickar till Raspberry Pi..."
scp ai_companies.db pi@raspberrypi.local:~/aim25-intel-bot/

echo "🔄 Startar om bot..."
ssh pi@raspberrypi.local "sudo systemctl restart discord-bot.service"

echo "✅ Klart! Botten använder nu ny databas"
```

Gör körbar:
```bash
chmod +x update_bot_database.sh

# Kör när du vill uppdatera:
./update_bot_database.sh
```

---

## 🔐 SSH utan lösenord (Valfritt men smidigt)

```bash
# På din vanliga dator
ssh-keygen -t rsa  # Tryck Enter 3 gånger
ssh-copy-id pi@raspberrypi.local

# Nu kan du SSH utan lösenord!
```

---

## 📊 Övervaka botten

### Se om botten körs:
```bash
sudo systemctl status discord-bot.service
```

### Live-loggar:
```bash
sudo journalctl -u discord-bot.service -f
```

### Kolla CPU/minne:
```bash
top
# Tryck 'q' för att avsluta
```

---

## 🐛 Felsökning

### Botten startar inte:

```bash
# Kolla loggar
sudo journalctl -u discord-bot.service -n 50

# Vanliga problem:
# 1. Fel Python-path
which python3  # Kopiera denna path till ExecStart i service-filen

# 2. Saknas dependencies
pip3 install -r requirements.txt

# 3. Databas saknas
ls -la ai_companies.db
```

### Botten kraschar:

```bash
# Service startar om automatiskt, men kolla loggar:
sudo journalctl -u discord-bot.service -f
```

### Kan inte nå RasPi:

```bash
# Hitta IP-adress (kör på RasPi):
hostname -I

# Eller från router admin-panel
```

---

## ⚡ Extra: Auto-update från GitHub

Skapa cron-jobb för att hämta updates var 5:e minut:

```bash
# Öppna crontab
crontab -e

# Lägg till (längst ner):
*/5 * * * * cd ~/aim25-intel-bot && git pull && sudo systemctl restart discord-bot.service
```

Nu hämtar RasPi automatiskt nya ändringar från GitHub!

---

## 💰 Fördelar med Raspberry Pi

- ✅ Du äger hårdvaran
- ✅ Ingen månadskostnad (bara ström: ~3 kr/månad)
- ✅ Lokal kontroll
- ✅ Lär dig Linux och server-management

## ⚠️ Nackdelar

- ❌ Kräver mer setup
- ❌ Strömavbrott stoppar botten
- ❌ Du måste hantera updates manuellt
- ❌ Internetavbrott stoppar botten

---

## 🎯 Rekommendation

**För lärande:** Använd Raspberry Pi - det är värdefullt att lära sig!

**För produktion:** Använd Railway/Render - mer pålitligt och mindre underhåll.

**Bästa av två världar:** Använd båda! RasPi som backup om cloud har problem.

---

**Skapad:** 2025-10-15  
**För:** ITHS AIM25S  
**Status:** Redo att använda
