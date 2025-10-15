# 🤖 AIM25 Intel Bot - Discord Bot för AI-företag

**Discord-bot för att hjälpa ITHS AIM25S studenter hitta praktikplatser inom AI**

## 📋 Översikt

Denna Discord-bot levererar:
- **Push**: Automatisk "Dagens AI-företag" kl 08:00 varje dag
- **Pull**: Kommandon för att söka och filtrera AI-företag

Databasen innehåller ~900+ svenska AI-företag från my.ai.se och EU-källor.

---

## 🚀 Snabbstart

### 1. Installera dependencies

```bash
pip install -r requirements.txt
```

### 2. Kolla att du har databasen

```bash
# Om ai_companies.db INTE finns, skapa den först:
python build_database.py
```

### 3. Konfigurera botten (valfritt)

För produktion, skapa en `.env`-fil:

```bash
cp .env.example .env
# Redigera .env och sätt DISCORD_BOT_TOKEN och DAILY_CHANNEL_ID
```

**OBS:** Just nu är bot-token hårdkodad i `discord_bot.py` för enklare testing. För produktion, använd `.env`!

### 4. Starta botten

```bash
python discord_bot.py
```

Du bör se:
```
🚀 Startar AIM25 Intel Bot...
✅ [BotNamn] är nu online!
✅ Ansluten till databas: ai_companies.db
✅ Daglig "Dagens AI-företag" är aktiv
🤖 Bot är redo att användas!
```

---

## 💬 Discord-kommandon

| Kommando | Beskrivning | Exempel |
|----------|-------------|---------|
| `/dagens` | Dagens AI-företag (slumpmässigt praktik-relevant) | `/dagens` |
| `/sok <namn>` | Sök efter företag | `/sok Vision` |
| `/typ <typ>` | Filtrera på företagstyp | `/typ startup` |
| `/stad <stad>` | Hitta företag i specifik stad | `/stad Stockholm` |
| `/stockholm` | Företag i Greater Stockholm | `/stockholm` |
| `/help` | Visa hjälp | `/help` |

### Exempel-användning

```
# Dagens företag
/dagens
→ Visar ett slumpmässigt praktik-relevant AI-företag

# Sök efter företag med "AI" i namnet
/sok AI
→ Visar max 5 företag som matchar

# Filtrera på startups
/typ startup
→ Visar 5 startups

# Hitta företag i Stockholm
/stad Stockholm
→ Visar företag i Stockholm (OBS: bara ~20% har location-data)

# Greater Stockholm-området
/stockholm
→ Visar företag i hela Stockholm-regionen
```

---

## ⏰ Automatisk daglig posting

Botten kan automatiskt posta "Dagens AI-företag" kl 08:00 varje dag.

### Konfigurera:

**Alternativ 1: Redigera discord_bot.py direkt**
```python
# Hitta denna rad i discord_bot.py (rad ~485):
CHANNEL_ID = None  # Ändra till ditt channel-ID
```

**Alternativ 2: Använd .env (rekommenderat för produktion)**
```bash
# .env
DAILY_CHANNEL_ID=1234567890123456789
```

### Hitta ditt Channel ID:
1. Aktivera Developer Mode i Discord (Settings → Advanced → Developer Mode)
2. Högerklicka på kanalen
3. Välj "Copy ID"

---

## 🏗️ Projektstruktur

```
.
├── discord_bot.py              # Huvudfil för Discord-botten
├── requirements.txt            # Python dependencies
├── .env.example                # Exempel på environment variables
├── ai_companies.db             # SQLite-databas (skapas av build_database.py)
├── build_database.py           # Script för att skapa/uppdatera databasen
├── query_database.py           # Interaktivt verktyg för att testa queries
└── README_DISCORD_BOT.md       # Denna fil
```

---

## 🔧 Tekniska detaljer

### Dependencies
- **discord.py** (>=2.3.0) - Discord API-bibliotek
- **python-dotenv** (>=1.0.0) - Environment variables (valfritt)
- **sqlite3** - Databas (inbyggt i Python)

### Bot-funktioner

#### Databas-interface (`CompanyDatabase`)
- `get_random_company()` - Hämta slumpmässigt företag
- `search_by_name()` - Sök efter namn
- `filter_by_type()` - Filtrera på typ
- `filter_by_city()` - Filtrera på stad
- `filter_greater_stockholm()` - Filtrera Greater Stockholm

#### Discord-kommandon
- Alla kommandon använder Discord embeds för snygg presentation
- Error-handling för felaktiga kommandon
- Automatisk help-command

#### Scheduling
- `@tasks.loop()` för daglig posting kl 08:00
- Väntar tills botten är redo innan schemat startar

---

## 🔐 Bot Setup (Discord Developer Portal)

Botten är redan skapad med följande credentials:

```
Name: AIM25_intel_bot
Application ID: 1423667681940344873
Public key: 5cab94d0c8a9b8db5f78f5130719ac84f5e14f290f993040b23ddc07ec4d777e
Bot token: [Se i discord_bot.py eller .env]
```

### Bot Permissions

Botten behöver följande permissions:
- **Read Messages/View Channels** - För att se kommandon
- **Send Messages** - För att svara på kommandon
- **Embed Links** - För snygga embed-meddelanden
- **Read Message History** - För att se kontext

### Invite Link

```
https://discord.com/api/oauth2/authorize?client_id=1423667681940344873&permissions=274877958144&scope=bot
```

---

## 🐛 Felsökning

### "Kunde inte ansluta till databas"

**Problem:** `ai_companies.db` finns inte

**Lösning:**
```bash
python build_database.py
```

### "Bot token saknas"

**Problem:** Token är inte satt

**Lösning:** 
- För development: Token är redan hårdkodad i `discord_bot.py`
- För produktion: Skapa `.env` och sätt `DISCORD_BOT_TOKEN`

### "Kommando fungerar inte"

**Problem:** Botten har inte rätt permissions

**Lösning:**
1. Kolla att botten har permissions i kanalen
2. Kolla att command prefix är `/` (slash)

### "Daglig posting fungerar inte"

**Problem:** `CHANNEL_ID` är inte satt

**Lösning:**
```python
# I discord_bot.py, rad ~485:
CHANNEL_ID = 1234567890123456789  # Ditt channel-ID
```

### "Botten hittar inga företag i stad"

**Problem:** Bara ~20% av företagen har location-data

**Förklaring:** 
- my.ai.se-data (80%) saknar location
- EU-data (20%) har location
- Detta är normalt och förväntat!

---

## 📊 Datastatistik

Efter setup har du:
- **~897 organisationer** från my.ai.se
- **~264 företag** från EU-källor (om du kört EU-import)
- **~524 praktik-relevanta** (corporations, startups, suppliers)
- **Location-data** för ~20% av företagen

---

## 🎯 Användningsfall

### För studenter
- Hitta praktikplatser inom AI
- Daglig inspiration med "Dagens AI-företag"
- Sök efter företag i specifika städer
- Filtrera på typ och AI-förmågor

### För lärare
- Automatisk information till klassen
- Inget manuellt arbete efter setup
- Portfolio-projekt för studenter

---

## 🔮 Framtida förbättringar

Idéer för vidareutveckling:

1. **Slash Commands** - Migrera till Discord's officiella slash commands
2. **Favoriter** - Låt studenter spara favorit-företag
3. **Notifikationer** - Notifiera när nya företag läggs till
4. **Avancerad filtrering** - Kombinera flera filter (stad + AI-förmåga)
5. **Statistik** - Visa trender och populära företag
6. **Praktik-status** - Markera vilka företag som tar praktikanter just nu

---

## 🤝 Bidra

Om du vill förbättra botten:
1. Forka projektet
2. Gör dina ändringar
3. Testa lokalt
4. Skicka en pull request

---

## 📝 Licens

Detta projekt är skapat för ITHS AIM25S och är fritt att använda och modifiera.

---

## 📞 Support

**Problem med botten?**
- Kolla först Felsökning-sektionen ovan
- Kolla att `ai_companies.db` finns
- Kolla att dependencies är installerade

**Databas-relaterade frågor?**
- Se `README_DATABASE.md`

---

**Skapad:** 2025-10-15  
**För:** ITHS AIM25S praktikprojekt  
**Version:** 1.0  
**Status:** ✅ REDO ATT ANVÄNDA

🚀 **Lycka till med praktikjakten!** 🚀
