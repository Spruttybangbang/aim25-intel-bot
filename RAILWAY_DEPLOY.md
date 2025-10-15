# Railway.app Deployment Guide för AIM25 Intel Bot

## Förberedelser

### 1. Skapa Git Repository

```bash
# I din projektmapp
git init
git add .
git commit -m "Initial commit - Discord bot"

# Skapa repo på GitHub och pusha
git remote add origin https://github.com/dittanvändarnamn/aim25-intel-bot.git
git push -u origin main
```

### 2. Skapa Railway-konto

1. Gå till https://railway.app
2. Logga in med GitHub
3. Klicka "New Project"
4. Välj "Deploy from GitHub repo"
5. Välj ditt repo

### 3. Konfigurera Environment Variables

I Railway dashboard:
1. Klicka på ditt projekt
2. Gå till "Variables"
3. Lägg till:
   ```
   DISCORD_BOT_TOKEN=din_token_här
   DAILY_CHANNEL_ID=ditt_channel_id_här
   ```

### 4. Railway deployer automatiskt!

Railway kommer:
- Installera dependencies från requirements.txt
- Köra discord_bot.py
- Hålla botten igång 24/7
- Auto-restart vid crash

## Uppdatera databasen

### Från din dator:
```bash
# 1. Uppdatera databas lokalt
python build_database.py

# 2. Commit och push
git add ai_companies.db
git commit -m "Uppdaterad databas"
git push

# 3. Railway deployer automatiskt om nya filer!
```

## Loggar

Se loggar i Railway:
- Klicka på ditt projekt
- Gå till "Deployments"
- Klicka på senaste deployment
- Se live-loggar

## Kostnad

- **Gratis:** 500h/månad (≈ 20 dagar)
- **Hobby plan:** $5/månad för unlimited
- Perfekt för detta projekt!

## Support

Om något går fel:
- Kolla loggar i Railway
- Verifiera environment variables
- Kolla att ai_companies.db finns i repo
