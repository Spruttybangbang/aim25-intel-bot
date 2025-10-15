# 🚀 DISCORD-BOT IMPLEMENTATIONSGUIDE

**Snabbstart för att få igång din Discord-bot på 5 minuter**

---

## ✅ CHECKLISTA

### Steg 1: Förberedelser (1 min)
- [ ] Ladda ner alla filer från `/outputs/`
- [ ] Se till att du har Python 3.7+ installerat
- [ ] Verifiera att du har `ai_companies.db` (om inte, kör `build_database.py`)

### Steg 2: Setup (2 min)
- [ ] Kör: `pip install -r requirements.txt`
- [ ] (Valfritt) Skapa `.env` från `.env.example`
- [ ] Verifiera databas: `python test_bot_database.py`

### Steg 3: Starta botten (1 min)
- [ ] Kör: `python discord_bot.py`
- [ ] Verifiera att du ser "✅ Bot är redo att användas!"
- [ ] Testa i Discord med `/help`

### Steg 4: Konfigurera daglig posting (1 min)
- [ ] Hitta ditt channel-ID i Discord (högerklicka → Copy ID)
- [ ] Redigera `discord_bot.py` rad ~485: `CHANNEL_ID = ditt_id`
- [ ] Starta om botten

---

## 📦 FILER DU HAR SKAPAT

```
✅ discord_bot.py            - Huvudfil (500+ rader)
✅ requirements.txt          - Dependencies
✅ .env.example              - Environment variables-mall
✅ README_DISCORD_BOT.md     - Komplett dokumentation
✅ setup.sh                  - Automatiskt setup-script (Linux/Mac)
✅ test_bot_database.py      - Test databas-interface
```

---

## 🎯 VAD BOTTEN KAN GÖRA

### Push-funktioner (Automatiskt)
- ⏰ Posta "Dagens AI-företag" kl 08:00 varje dag
- 🎲 Slumpmässigt praktik-relevant företag
- 🎨 Snygga Discord embeds med logotyp

### Pull-funktioner (Kommandon)
- `/dagens` - Dagens AI-företag (när som helst)
- `/sok <namn>` - Sök efter företag
- `/typ <typ>` - Filtrera på typ (startup, corporation, etc.)
- `/stad <stad>` - Hitta företag i specifik stad
- `/stockholm` - Greater Stockholm-området
- `/help` - Visa hjälp

---

## 🔧 SNABB FELSÖKNING

### "Kunde inte ansluta till databas"
**Lösning:** Kör `python build_database.py` först

### "Inga företag i Stockholm"
**Normal:** my.ai.se-data (80%) saknar location. EU-import krävs.

### "Bot svarar inte på kommandon"
**Lösning:** Kolla att botten har rätt permissions i Discord-kanalen

### "Daglig posting fungerar inte"
**Lösning:** Sätt `CHANNEL_ID` i `discord_bot.py` (rad ~485)

---

## 📊 DATABAS-STATUS

**Efter build_database.py:**
- ✅ 897 organisationer från my.ai.se
- ✅ ~524 praktik-relevanta företag
- ⚠️  Location-data saknas (bara my.ai.se)

**Efter EU-import (valfritt):**
- ✅ ~1050-1150 totalt företag
- ✅ ~720-780 praktik-relevanta
- ✅ Location-data för ~20%

---

## 🎓 BOT-ARKITEKTUR

### Klasser
```python
CompanyDatabase         # Databas-interface
├── get_random_company()      # Dagens företag
├── search_by_name()          # Sök
├── filter_by_type()          # Filtrera typ
├── filter_by_city()          # Filtrera stad
└── filter_greater_stockholm() # Greater Stockholm
```

### Discord-kommandon
```python
@bot.command(name='dagens')    # /dagens
@bot.command(name='sok')       # /sok
@bot.command(name='typ')       # /typ
@bot.command(name='stad')      # /stad
@bot.command(name='stockholm') # /stockholm
@bot.command(name='help')      # /help
```

### Scheduling
```python
@tasks.loop(time=time(hour=8, minute=0))
async def daily_company():
    # Posta kl 08:00 varje dag
```

---

## 🌟 FEATURES

### Implementerat ✅
- [x] Discord-bot med commands
- [x] Databas-integration (SQLite)
- [x] Dagens AI-företag (slumpmässigt)
- [x] Sök efter namn
- [x] Filtrera på typ
- [x] Filtrera på stad
- [x] Greater Stockholm-filtrering
- [x] Daglig automatisk posting
- [x] Snygga Discord embeds
- [x] Error-handling
- [x] Help-command

### Möjliga framtida features 🔮
- [ ] Slash commands (Discord's nya API)
- [ ] Favoriter per användare
- [ ] Notifikationer för nya företag
- [ ] Avancerad filtrering (kombinera flera)
- [ ] Statistik och trender
- [ ] Praktik-status tracking

---

## 🔐 BOT-CREDENTIALS

**Redan konfigurerat:**
```
Application ID: 1423667681940344873
Bot Token: [Hårdkodad i discord_bot.py]
Invite Link: https://discord.com/api/oauth2/authorize?client_id=1423667681940344873&permissions=274877958144&scope=bot
```

**Inget behöver ändras för development!**

---

## 📖 EXEMPEL-ANVÄNDNING

### Terminal
```bash
# 1. Setup
pip install -r requirements.txt

# 2. Testa databas
python test_bot_database.py

# 3. Starta bot
python discord_bot.py
```

### Discord
```
User: /dagens
Bot: [Visar dagens AI-företag med embed]

User: /sok Vision
Bot: [Visar 5 företag med "Vision" i namnet]

User: /typ startup
Bot: [Visar 5 startups]

User: /stad Stockholm
Bot: [Visar företag i Stockholm - om location-data finns]

User: /help
Bot: [Visar alla kommandon]
```

---

## 💡 TIPS

### För bästa resultat:
1. **Kör EU-import** för att få location-data
2. **Konfigurera daglig posting** för automatisk inspiration
3. **Bjud in botten** till din klass-server
4. **Testa alla kommandon** för att förstå vad som finns

### För produktion:
1. **Använd .env** istället för hårdkodad token
2. **Sätt upp logging** för att fånga fel
3. **Backup databas** regelbundet
4. **Överväg hosting** (Heroku, Railway, etc.)

---

## 🎉 DU ÄR REDO!

**Allt du behöver göra nu:**

```bash
python discord_bot.py
```

**Sedan i Discord:**
```
/help
```

**Grattis! 🎊 Din Discord-bot är igång!**

---

## 📞 NÄSTA STEG

1. **Testa botten** - Prova alla kommandon
2. **Konfigurera daglig posting** - Sätt CHANNEL_ID
3. **Bjud in till klass-server** - Dela med klassen
4. **Kör EU-import** (valfritt) - För location-data

---

**Skapad:** 2025-10-15  
**För:** ITHS AIM25S  
**Status:** ✅ REDO ATT ANVÄNDA

**Lycka till! 🚀**
