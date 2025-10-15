# Cloud-databas för AIM25 Intel Bot

**Professionell lösning för att dela databas mellan din dator och cloud/RasPi**

---

## 🎯 Problemet vi löser

- ✅ Uppdatera databas från vilken dator som helst
- ✅ Botten använder alltid senaste data
- ✅ Ingen manuell synkning via Git eller SCP
- ✅ Flera användare kan uppdatera samtidigt

---

## 🌐 Rekommenderade Cloud-databaser (Gratis)

### 1. **Supabase (PostgreSQL)** ⭐ REKOMMENDERAD

**Varför Supabase?**
- ✅ Gratis tier: 500 MB data
- ✅ PostgreSQL (kraftfull SQL-databas)
- ✅ Enkelt API
- ✅ Web-interface för att se data
- ✅ Auto-backups

**Setup:**
1. Gå till https://supabase.com
2. Skapa konto (gratis)
3. Skapa nytt projekt
4. Få connection string

### 2. **PlanetScale (MySQL)**

- ✅ Gratis tier: 5 GB data
- ✅ MySQL-kompatibel
- ✅ Bra prestanda
- ✅ Auto-scaling

### 3. **MongoDB Atlas**

- ✅ Gratis tier: 512 MB
- ✅ NoSQL (flexibel)
- ✅ Lättare att komma igång
- ⚠️ Annorlunda än SQLite

---

## 🔄 Varför INTE bara Git?

**Git-metoden fungerar, men:**
- ⚠️ Manuell push/pull krävs
- ⚠️ Merge-konflikter om flera uppdaterar
- ⚠️ SQLite-filer kan bli korrupta vid merge
- ⚠️ Ingen real-time sync

**Cloud-databas:**
- ✅ Automatisk synkning
- ✅ Flera användare samtidigt
- ✅ Alltid uppdaterad
- ✅ Professionell lösning

---

## 📝 Implementation med Supabase

### Steg 1: Skapa Supabase-projekt

```bash
# 1. Gå till https://supabase.com och skapa konto
# 2. Skapa nytt projekt
# 3. Vänta ~2 minuter medan projektet sätts upp
# 4. Gå till Settings → Database
# 5. Kopiera Connection String (URI)
```

### Steg 2: Installera PostgreSQL-adapter

```bash
pip install psycopg2-binary
```

### Steg 3: Migrera SQLite till PostgreSQL

**Skapa migration-script:**

```python
#!/usr/bin/env python3
"""
Migrera SQLite till PostgreSQL (Supabase)
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Din Supabase connection string
POSTGRES_URL = "postgresql://user:pass@db.xxx.supabase.co:5432/postgres"

def migrate():
    # Anslut till SQLite
    sqlite_conn = sqlite3.connect('ai_companies.db')
    sqlite_conn.row_factory = sqlite3.Row
    
    # Anslut till PostgreSQL
    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_cursor = pg_conn.cursor()
    
    # Skapa tabeller (kör build_database-logik på PostgreSQL)
    # ... (se fullständig implementation nedan)
    
    # Kopiera data
    # ... 
    
    print("✅ Migration klar!")

if __name__ == "__main__":
    migrate()
```

### Steg 4: Uppdatera discord_bot.py

```python
# Lägg till i början av filen
import psycopg2
from psycopg2.extras import RealDictCursor

class CompanyDatabase:
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.conn = None
        self.is_postgres = 'postgresql' in (self.db_url or '')
    
    def connect(self):
        try:
            if self.is_postgres:
                # PostgreSQL
                self.conn = psycopg2.connect(
                    self.db_url,
                    cursor_factory=RealDictCursor
                )
            else:
                # SQLite (fallback)
                self.conn = sqlite3.connect(self.db_url or 'ai_companies.db')
                self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ Databasfel: {e}")
            return False
```

---

## 🎯 Enklare alternativ: Fortsätt med SQLite + Git

**Om cloud-databas känns för komplext just nu:**

### Automatisera Git-synkning

**På din dator** - `update_and_push.sh`:
```bash
#!/bin/bash
# Uppdatera och pusha automatiskt

echo "🔄 Bygger databas..."
python build_database.py

echo "📤 Pushar till GitHub..."
git add ai_companies.db
git commit -m "Auto-update: $(date)"
git push

echo "✅ Klart! Railway/RasPi hämtar automatiskt"
```

**På Railway/RasPi** - Auto-pull:
```bash
# Railway: Enable auto-deploy från GitHub (redan aktivt!)

# RasPi: Cron-jobb
*/5 * * * * cd ~/aim25-intel-bot && git pull
```

---

## 📊 Jämförelse: Alla metoder

| Metod | Komplexitet | Kostnad | Real-time | Multi-user |
|-------|-------------|---------|-----------|------------|
| **SQLite + Git** | 🟢 Låg | Gratis | ❌ Nej | ⚠️ Begränsat |
| **SQLite + SCP** | 🟢 Låg | Gratis | ❌ Nej | ❌ Nej |
| **Cloud-databas** | 🟡 Medel | Gratis | ✅ Ja | ✅ Ja |

---

## 💡 Min rekommendation

### För detta projekt (just nu):
**Använd SQLite + Git**
- ✅ Du är ensam användare
- ✅ Uppdaterar databas sällan
- ✅ Enklare att komma igång
- ✅ Lär dig Git workflow

### För framtiden (om projektet växer):
**Migrera till cloud-databas**
- När flera ska uppdatera
- När du vill ha real-time updates
- När du vill lära dig PostgreSQL

---

## 🚀 Snabbstart: SQLite + Git (Rekommenderat)

### 1. Skapa Git repo

```bash
cd din-projekt-mapp
git init
git add .
git commit -m "Initial commit"

# Skapa på GitHub och pusha
git remote add origin https://github.com/ditt-användarnamn/aim25-intel-bot.git
git push -u origin main
```

### 2. Deploy på Railway

- Gå till https://railway.app
- New Project → Deploy from GitHub
- Välj ditt repo
- Sätt environment variables:
  - `DISCORD_BOT_TOKEN`
  - `DAILY_CHANNEL_ID`

### 3. Uppdatera databas

```bash
# På din dator
python build_database.py
git add ai_companies.db
git commit -m "Uppdaterad databas"
git push

# Railway deployer automatiskt!
```

**Det är allt!** 🎉

---

## 📚 Resurser

- **Railway docs:** https://docs.railway.app
- **Supabase docs:** https://supabase.com/docs
- **Git basics:** https://git-scm.com/book

---

**Skapad:** 2025-10-15  
**För:** ITHS AIM25S  
**Rekommendation:** Börja med Git, migrera till cloud-databas senare om behövs
