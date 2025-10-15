# 🚀 KOMPLETT DEPLOYMENT-GUIDE - Välj rätt lösning

**Alla sätt att köra din Discord-bot 24/7 + uppdatera databasen**

---

## 🎯 TL;DR - Snabba rekommendationen

### 🥇 **BÄST FÖR DIG: Railway + Git**

**Varför?**
- ✅ Enklast att sätta upp (10 min)
- ✅ Gratis för detta projekt
- ✅ Uppdatera databas från vilken dator som helst
- ✅ Automatisk deployment
- ✅ Inget underhåll
- ✅ Professionell lösning

**Hur?**
1. Pusha projektet till GitHub
2. Anslut GitHub till Railway
3. Sätt environment variables
4. Klart! 🎉

**För att uppdatera databas:**
```bash
python build_database.py
git push
# Railway deployer automatiskt!
```

---

## 📊 Alla alternativ jämfört

| Alternativ | Setup-tid | Kostnad/mån | Uppdatera DB | Pålitlighet | Lärande |
|------------|-----------|-------------|--------------|-------------|---------|
| **Railway + Git** | 10 min | Gratis | Git push | ⭐⭐⭐⭐⭐ | Git, CI/CD |
| **Render + Git** | 15 min | Gratis | Git push | ⭐⭐⭐⭐ | Git, CI/CD |
| **Raspberry Pi** | 30 min | ~3 kr | SCP/Git | ⭐⭐⭐ | Linux, systemd |
| **Din dator** | 0 min | Gratis | Lokal | ⭐⭐ | Inget nytt |
| **VPS (Hetzner)** | 60 min | 50 kr | SSH | ⭐⭐⭐⭐⭐ | Linux, server |

---

## 🎯 ALTERNATIV 1: Railway (Rekommenderat) ⭐

### Fördelar
- ✅ **Enklast** - Deploy på 10 minuter
- ✅ **Gratis** - 500h/månad (mer än nog)
- ✅ **Auto-deploy** - Git push → automatisk update
- ✅ **Pålitlig** - 99.9% uptime
- ✅ **Inget underhåll** - Railway sköter allt
- ✅ **Loggar** - Se vad som händer i realtid

### Nackdelar
- ❌ Begränsat gratis-tier (500h = 20 dagar, räcker för detta)
- ❌ Kräver kreditkort för verifiering (debiteras ej om inom free tier)

### Setup-steg

**1. Förbered Git repo (5 min)**
```bash
git init
git add .
git commit -m "Discord bot initial commit"
git push
```

**2. Railway setup (3 min)**
- Gå till https://railway.app
- "New Project" → "Deploy from GitHub"
- Välj ditt repo
- Vänta ~2 min (Railway bygger automatiskt)

**3. Environment variables (2 min)**
I Railway dashboard:
- Klicka "Variables"
- Lägg till:
  ```
  DISCORD_BOT_TOKEN=din_token
  DAILY_CHANNEL_ID=ditt_channel_id
  ```

**4. Klart!** ✅

### Uppdatera databas
```bash
python build_database.py
git add ai_companies.db
git commit -m "Uppdaterad databas"
git push
# Railway deployer automatiskt inom 1-2 min!
```

### Kostnad
- **Free tier:** 500 execution hours/månad
- Detta projekt: ~720h/månad (bot körs 24/7)
- **Lösning:** $5/månad för Hobby plan (unlimited)
- **Alternativ:** Använd Render istället (se nedan)

📖 **Full guide:** [RAILWAY_DEPLOY.md](computer:///mnt/user-data/outputs/RAILWAY_DEPLOY.md)

---

## 🎯 ALTERNATIV 2: Render.com (Helt gratis!)

### Fördelar
- ✅ **100% gratis** - Ingen betalning krävs
- ✅ **Ingen kreditkort** - Inget kort behövs
- ✅ **Auto-deploy** - Git push → update
- ✅ **Enkel** - Liknande Railway

### Nackdelar
- ⚠️ **Spin down** - Inaktiv efter 15 min
- ⚠️ **Slow start** - Tar 30 sek att vakna
- ❌ **Problem för Discord-bot** - Botten disconnectar vid spin down

### Lösning för Render
**Lägg till "keep-alive" ping:**
```python
# Lägg till i discord_bot.py
@tasks.loop(minutes=10)
async def keep_alive():
    """Håll Render-instansen vaken"""
    print(f"⏰ Keep-alive ping: {datetime.now()}")

# I on_ready():
keep_alive.start()
```

### Setup
1. Gå till https://render.com
2. "New Web Service"
3. Anslut GitHub
4. Sätt environment variables
5. Deploy!

📝 **Render är bra backup om Railway kostar för mycket**

---

## 🎯 ALTERNATIV 3: Raspberry Pi (Lär dig Linux!) 🍓

### Fördelar
- ✅ **Du äger hårdvaran** - Full kontroll
- ✅ **Billigt** - ~3 kr/månad i ström
- ✅ **Lärande** - Linux, systemd, SSH, server management
- ✅ **Portfolio-värde** - Bra att kunna på CV

### Nackdelar
- ⚠️ **Kräver setup** - 30-60 min första gången
- ❌ **Strömavbrott** - Stoppar botten (men auto-restart)
- ❌ **Internet-beroende** - Ditt hemmanätverk
- ⚠️ **Underhåll** - Du måste uppdatera OS, etc.

### Setup-steg

**1. SSH till RasPi**
```bash
ssh pi@raspberrypi.local
```

**2. Klona projekt**
```bash
git clone https://github.com/ditt-användarnamn/aim25-intel-bot.git
cd aim25-intel-bot
pip3 install -r requirements.txt
```

**3. Skapa systemd service**
```bash
sudo nano /etc/systemd/system/discord-bot.service
# Lägg in service-config (se RASPI_DEPLOY.md)
sudo systemctl enable discord-bot.service
sudo systemctl start discord-bot.service
```

**4. Klart!** ✅

### Uppdatera databas

**Metod A: Git (rekommenderat)**
```bash
# Din dator
python build_database.py
git push

# RasPi (automatiskt via cron)
# Eller manuellt:
ssh pi@raspberrypi.local
cd aim25-intel-bot
git pull
sudo systemctl restart discord-bot.service
```

**Metod B: SCP (direkt)**
```bash
python build_database.py
scp ai_companies.db pi@raspberrypi.local:~/aim25-intel-bot/
ssh pi@raspberrypi.local "sudo systemctl restart discord-bot.service"
```

📖 **Full guide:** [RASPI_DEPLOY.md](computer:///mnt/user-data/outputs/RASPI_DEPLOY.md)

---

## 🎯 ALTERNATIV 4: Din vanliga dator (Inte rekommenderat)

### Fördelar
- ✅ **Ingen setup** - Bara kör scriptet
- ✅ **Gratis** - Ingen kostnad

### Nackdelar
- ❌ **Måste vara på** - Datorn måste vara igång 24/7
- ❌ **Ström** - Kostar mer än RasPi
- ❌ **Missar poster** - Om du stänger datorn eller glömmer
- ❌ **Opålitlig** - Ingen auto-restart vid crash

### När detta funkar
- Testing och development
- Inte för produktion!

---

## 🗄️ Hantera databas-uppdateringar

### Metod 1: Git (Alla cloud-alternativ) ⭐

**Setup en gång:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/...
git push
```

**Varje gång du uppdaterar:**
```bash
python build_database.py
git add ai_companies.db
git commit -m "Uppdaterad databas $(date)"
git push
# Cloud-tjänst deployer automatiskt!
```

**Fördelar:**
- ✅ Funkar från vilken dator som helst
- ✅ Versionshistorik
- ✅ Automatisk deployment
- ✅ Professionell workflow

### Metod 2: SCP (Raspberry Pi)

```bash
# En rad för att uppdatera allt:
python build_database.py && scp ai_companies.db pi@raspberrypi.local:~/aim25-intel-bot/ && ssh pi@raspberrypi.local "sudo systemctl restart discord-bot.service"
```

### Metod 3: Cloud-databas (Avancerat)

Se [CLOUD_DATABASE.md](computer:///mnt/user-data/outputs/CLOUD_DATABASE.md) för PostgreSQL/Supabase

---

## 💰 Kostnadsjämförelse (per månad)

| Alternativ | Kostnad | Kommentar |
|------------|---------|-----------|
| **Railway Free** | 0 kr | 500h/mån (räcker ej för 24/7) |
| **Railway Hobby** | ~55 kr | Unlimited, rekommenderat |
| **Render** | 0 kr | Helt gratis, men spin-down |
| **Raspberry Pi** | ~3 kr | Endast ström |
| **Din dator** | ~30 kr | Ström för laptop 24/7 |
| **VPS (Hetzner)** | 50 kr | Professionell server |

---

## 🎓 Lärande-värde

### Railway/Render
- ✅ Git och version control
- ✅ CI/CD (Continuous Integration/Deployment)
- ✅ Environment variables
- ✅ Cloud deployment
- ✅ Monitoring och logging

### Raspberry Pi
- ✅ Allt ovan PLUS:
- ✅ Linux server management
- ✅ SSH och remote access
- ✅ systemd services
- ✅ Cron jobs
- ✅ Networking

---

## ✅ MIN REKOMMENDATION FÖR DIG

### 🥇 **Primärt: Railway + Git**

**Varför:**
1. **Professionell** - Så här jobbar företag
2. **Pålitlig** - 99.9% uptime
3. **Lätt** - 10 minuter setup
4. **Portfolio** - Imponerande på CV
5. **Git** - Du lär dig essentiell skill

**Kostnad:** 
- Testa gratis först
- Om du gillar det: $5/månad (värt det!)

### 🥈 **Backup: Raspberry Pi**

**Använd RasPi som:**
1. **Lärande-projekt** - Värdefullt att kunna Linux
2. **Backup** - Om Railway har problem
3. **Portfolio** - Visa att du kan server-management

---

## 🚀 SNABBSTART: Railway + Git (10 minuter)

```bash
# 1. Git setup (2 min)
git init
git add .
git commit -m "Discord bot"
# Skapa repo på GitHub och:
git remote add origin https://github.com/ditt-användarnamn/aim25-intel-bot.git
git push -u origin main

# 2. Railway setup (5 min)
# - Gå till railway.app
# - New Project → GitHub
# - Välj ditt repo
# - Vänta på build

# 3. Environment variables (2 min)
# I Railway dashboard → Variables:
# DISCORD_BOT_TOKEN=din_token
# DAILY_CHANNEL_ID=ditt_channel_id

# 4. Klart! (1 min)
# Kolla loggar i Railway
# Testa i Discord: /help
```

### Uppdatera senare:
```bash
python build_database.py
git add ai_companies.db  
git commit -m "Updated database"
git push
# Railway deployer inom 2 minuter!
```

---

## 📞 Frågor?

**"Vilket alternativ ska JAG välja?"**
→ Railway (lättast) eller RasPi (mest lärande)

**"Kostar Railway pengar?"**
→ $5/mån efter free tier (500h), men värt det. Annars använd Render (gratis)

**"Kan jag byta senare?"**
→ Ja! Projektet funkar överallt. Börja med Railway, testa RasPi senare.

**"Vad lär jag mig mest av?"**
→ RasPi lär dig mest, Railway lär dig CI/CD (också värdefullt)

---

## 🎯 Nästa steg

1. **Välj alternativ** (jag rekommenderar Railway)
2. **Följ guiden** för ditt val:
   - Railway: [RAILWAY_DEPLOY.md](computer:///mnt/user-data/outputs/RAILWAY_DEPLOY.md)
   - RasPi: [RASPI_DEPLOY.md](computer:///mnt/user-data/outputs/RASPI_DEPLOY.md)
   - Cloud DB: [CLOUD_DATABASE.md](computer:///mnt/user-data/outputs/CLOUD_DATABASE.md)
3. **Testa** att allt fungerar
4. **Uppdatera databas** och se att det synkar

**Lycka till! 🚀**

---

**Skapad:** 2025-10-15  
**För:** ITHS AIM25S  
**Rekommendation:** Railway + Git (lättast) eller Raspberry Pi (mest lärande)
