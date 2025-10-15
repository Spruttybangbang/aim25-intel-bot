#!/bin/bash
# 🚀 SNABB SETUP FÖR AIM25 INTEL BOT

echo "🤖 AIM25 Intel Bot - Setup"
echo "=========================="
echo ""

# 1. Installera dependencies
echo "📦 Installerar dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Kunde inte installera dependencies"
    exit 1
fi

echo "✅ Dependencies installerade"
echo ""

# 2. Kolla databas
echo "🔍 Kollar efter databas..."
if [ ! -f "ai_companies.db" ]; then
    echo "⚠️  ai_companies.db hittades inte!"
    echo "💡 Kör 'python build_database.py' för att skapa databasen"
    echo ""
    read -p "Vill du skapa databasen nu? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python build_database.py
        if [ $? -ne 0 ]; then
            echo "❌ Kunde inte skapa databas"
            exit 1
        fi
    fi
else
    echo "✅ Databas hittad: ai_companies.db"
fi

echo ""

# 3. Konfigurera (valfritt)
echo "⚙️  Konfiguration (valfritt)"
echo ""
echo "För produktion kan du skapa en .env-fil:"
echo "  cp .env.example .env"
echo "  # Redigera .env och sätt DISCORD_BOT_TOKEN och DAILY_CHANNEL_ID"
echo ""
echo "För development fungerar botten utan .env (token är hårdkodad)"
echo ""

# 4. Information
echo "📋 Nästa steg:"
echo "  1. Starta botten: python discord_bot.py"
echo "  2. Använd /help i Discord för att se kommandon"
echo "  3. (Valfritt) Konfigurera CHANNEL_ID för daglig posting"
echo ""

# 5. Bot invite link
echo "🔗 Invite bot till din server:"
echo "https://discord.com/api/oauth2/authorize?client_id=1423667681940344873&permissions=274877958144&scope=bot"
echo ""

echo "✅ Setup klar! Kör 'python discord_bot.py' för att starta botten"
