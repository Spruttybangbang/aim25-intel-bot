#!/usr/bin/env python3
"""
🤖 AIM25 INTEL BOT - Discord Bot för AI-företag praktikprojektet
================================================================
Automatisk "Dagens AI-företag" + Pull-baserad sökning

Kommandon:
- /dagens - Dagens AI-företag
- /sok <namn> - Sök efter företag
- /typ <typ> - Filtrera på företagstyp
- /stad <stad> - Filtrera på stad
- /stockholm - Företag i Greater Stockholm
- /help - Visa hjälp
"""

import discord
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime, time
import sys
import os
from pathlib import Path
import traceback
from typing import Optional, List, Dict

# Ladda environment variables (om .env finns)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv inte installerad, använd hårdkodade värden

# ==================== DATABAS-HANTERING ====================

class CompanyDatabase:
    """Databas-interface för AI-företag"""
    
    def __init__(self, db_path: str = "ai_companies.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Anslut till databasen"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ Kunde inte ansluta till databas: {e}")
            return False
    
    def close(self):
        """Stäng databas-anslutning"""
        if self.conn:
            self.conn.close()
    
    def get_random_company(self, only_praktik_relevant: bool = True) -> Optional[Dict]:
        """
        Hämta ett slumpmässigt företag
        
        Args:
            only_praktik_relevant: Om True, visa bara praktik-relevanta företag
        """
        if not self.conn:
            return None
            
        cursor = self.conn.cursor()
        
        where_clause = ""
        if only_praktik_relevant:
            where_clause = "WHERE type IN ('corporation', 'startup', 'supplier')"
        
        query = f"""
        SELECT id, name, website, type, logo_url, description, 
               location_city, location_greater_stockholm
        FROM companies
        {where_clause}
        ORDER BY RANDOM()
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            company_id = result['id']
            
            # Hämta AI-förmågor
            cursor.execute("""
                SELECT ac.name 
                FROM ai_capabilities ac
                JOIN company_ai_capabilities cac ON ac.id = cac.capability_id
                WHERE cac.company_id = ?
                LIMIT 5
            """, (company_id,))
            ai_capabilities = [row['name'] for row in cursor.fetchall()]
            
            return {
                'id': result['id'],
                'name': result['name'],
                'website': result['website'],
                'type': result['type'],
                'logo_url': result['logo_url'],
                'description': result['description'],
                'location_city': result['location_city'],
                'location_greater_stockholm': result['location_greater_stockholm'],
                'ai_capabilities': ai_capabilities
            }
        
        return None
    
    def search_by_name(self, search_term: str, limit: int = 5) -> List[Dict]:
        """Sök företag efter namn"""
        if not self.conn:
            return []
            
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, name, website, type, location_city
        FROM companies
        WHERE name LIKE ?
        ORDER BY name
        LIMIT ?
        """
        
        cursor.execute(query, (f"%{search_term}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'website': row['website'],
                'type': row['type'],
                'location_city': row['location_city']
            })
        
        return results
    
    def filter_by_type(self, company_type: str, limit: int = 5) -> List[Dict]:
        """Filtrera företag på typ"""
        if not self.conn:
            return []
            
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, name, website, type, location_city
        FROM companies
        WHERE LOWER(type) = LOWER(?)
        ORDER BY name
        LIMIT ?
        """
        
        cursor.execute(query, (company_type, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'website': row['website'],
                'type': row['type'],
                'location_city': row['location_city']
            })
        
        return results
    
    def filter_by_city(self, city: str, limit: int = 10) -> List[Dict]:
        """Filtrera företag på stad (bara praktik-relevanta)"""
        if not self.conn:
            return []
            
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, name, website, type, description, location_city
        FROM companies
        WHERE location_city LIKE ?
        AND type IN ('corporation', 'startup', 'supplier')
        ORDER BY name
        LIMIT ?
        """
        
        cursor.execute(query, (f"%{city}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'website': row['website'],
                'type': row['type'],
                'description': row['description'],
                'location_city': row['location_city']
            })
        
        return results
    
    def filter_greater_stockholm(self, limit: int = 10) -> List[Dict]:
        """Filtrera företag i Greater Stockholm (bara praktik-relevanta)"""
        if not self.conn:
            return []
            
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, name, website, type, description, location_city
        FROM companies
        WHERE location_greater_stockholm = 1
        AND type IN ('corporation', 'startup', 'supplier')
        ORDER BY name
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'name': row['name'],
                'website': row['website'],
                'type': row['type'],
                'description': row['description'],
                'location_city': row['location_city']
            })
        
        return results

# ==================== DISCORD BOT ====================

# Bot setup med intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# Global databas-instans
db = CompanyDatabase()

@bot.event
async def on_ready():
    """Körs när botten är klar"""
    print(f'\n✅ {bot.user} är nu online!')
    print(f'📊 Ansluten till {len(bot.guilds)} server(s)')
    
    # Anslut till databas
    if db.connect():
        print(f'✅ Ansluten till databas: {db.db_path}')
    else:
        print(f'❌ Kunde inte ansluta till databas!')
        print(f'⚠️  Se till att ai_companies.db finns i samma mapp')
    
    # Starta daglig posting (om aktiverad)
    if not daily_company.is_running():
        daily_company.start()
        print('✅ Daglig "Dagens AI-företag" är aktiv')
    
    print(f'\n🤖 Bot är redo att användas!')
    print(f'💡 Använd /help för att se kommandon\n')

@bot.event
async def on_command_error(ctx, error):
    """Hantera fel i kommandon"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Okänt kommando! Använd `/help` för att se tillgängliga kommandon.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Saknar argument: {error.param.name}")
    else:
        await ctx.send(f"❌ Ett fel uppstod: {str(error)}")
        print(f"Fel: {error}")
        traceback.print_exception(type(error), error, error.__traceback__)

# ==================== BOT-KOMMANDON ====================

@bot.command(name='help')
async def help_command(ctx):
    """Visa hjälp-meddelande"""
    embed = discord.Embed(
        title="🤖 AIM25 Intel Bot - Hjälp",
        description="Discord-bot för att hitta AI-företag och praktikplatser",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📋 Kommandon",
        value=(
            "`/dagens` - Dagens AI-företag (slumpmässigt praktik-relevant företag)\n"
            "`/sok <namn>` - Sök efter företag (t.ex. `/sok Vision`)\n"
            "`/typ <typ>` - Filtrera på typ (startup, corporation, supplier)\n"
            "`/stad <stad>` - Hitta företag i specifik stad\n"
            "`/stockholm` - Företag i Greater Stockholm\n"
            "`/help` - Visa denna hjälp"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⏰ Automatisk posting",
        value="Botten postar automatiskt 'Dagens AI-företag' kl 08:00 varje dag",
        inline=False
    )
    
    embed.add_field(
        name="📊 Om datan",
        value="~900+ svenska AI-företag från my.ai.se och EU-källor",
        inline=False
    )
    
    embed.set_footer(text="Projekt av ITHS AIM25S | För praktikjakt 🚀")
    
    await ctx.send(embed=embed)

@bot.command(name='dagens')
async def dagens(ctx):
    """Dagens AI-företag - slumpmässigt praktik-relevant företag"""
    company = db.get_random_company(only_praktik_relevant=True)
    
    if not company:
        await ctx.send("❌ Kunde inte hitta något företag. Kolla att databasen finns!")
        return
    
    # Skapa embed för snygg presentation
    embed = discord.Embed(
        title=f"🏢 {company['name']}",
        url=company['website'] if company['website'] else None,
        description=company['description'][:500] + "..." if company.get('description') and len(company.get('description', '')) > 500 else company.get('description', ''),
        color=discord.Color.green()
    )
    
    # Lägg till fält
    if company.get('website'):
        embed.add_field(name="🌐 Hemsida", value=company['website'], inline=False)
    
    if company.get('location_city'):
        location = company['location_city']
        if company.get('location_greater_stockholm'):
            location += " (Greater Stockholm)"
        embed.add_field(name="📍 Plats", value=location, inline=True)
    
    embed.add_field(name="📊 Typ", value=company['type'].capitalize(), inline=True)
    
    if company.get('ai_capabilities'):
        ai_caps = ', '.join(company['ai_capabilities'][:3])
        embed.add_field(name="🤖 AI-förmågor", value=ai_caps, inline=False)
    
    # Lägg till logotyp om den finns
    if company.get('logo_url'):
        embed.set_thumbnail(url=company['logo_url'])
    
    embed.set_footer(text=f"Dagens AI-företag • {datetime.now().strftime('%Y-%m-%d')}")
    
    await ctx.send(embed=embed)

@bot.command(name='sok')
async def sok(ctx, *, search_term: str):
    """
    Sök efter företag
    
    Usage: /sok Vision
    """
    results = db.search_by_name(search_term)
    
    if not results:
        await ctx.send(f"❌ Hittade inga företag som matchar '{search_term}'")
        return
    
    # Skapa embed
    embed = discord.Embed(
        title=f"🔍 Sökresultat för '{search_term}'",
        description=f"Hittade {len(results)} företag",
        color=discord.Color.blue()
    )
    
    for i, company in enumerate(results, 1):
        location = f" - {company['location_city']}" if company.get('location_city') else ""
        value = f"[{company['website']}]({company['website']}){location}\nTyp: {company['type']}"
        embed.add_field(
            name=f"{i}. {company['name']}",
            value=value,
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='typ')
async def typ(ctx, company_type: str):
    """
    Filtrera företag på typ
    
    Usage: /typ startup
    Typer: startup, corporation, supplier, academia, etc.
    """
    results = db.filter_by_type(company_type)
    
    if not results:
        await ctx.send(f"❌ Hittade inga företag av typ '{company_type}'\n💡 Prova: startup, corporation, supplier")
        return
    
    # Skapa embed
    embed = discord.Embed(
        title=f"🏢 {company_type.capitalize()}",
        description=f"Visar {len(results)} företag",
        color=discord.Color.purple()
    )
    
    for company in results:
        location = f" - {company['location_city']}" if company.get('location_city') else ""
        embed.add_field(
            name=company['name'] + location,
            value=f"[{company['website']}]({company['website']})",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='stad')
async def stad(ctx, *, city: str):
    """
    Hitta företag i specifik stad
    
    Usage: /stad Stockholm
    """
    results = db.filter_by_city(city)
    
    if not results:
        await ctx.send(
            f"❌ Hittade inga praktik-relevanta företag i {city}\n"
            f"⚠️ OBS: Endast ~20% av företagen har location-data (från EU-källa)"
        )
        return
    
    # Skapa embed
    embed = discord.Embed(
        title=f"📍 AI-företag i {city}",
        description=f"Hittade {len(results)} praktik-relevanta företag",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="ℹ️ Info",
        value="Endast EU-företag (~20%) har location-data. my.ai.se-företag (80%) saknar stad.",
        inline=False
    )
    
    for company in results[:5]:  # Visa max 5
        description = company.get('description', '')[:100] + "..." if company.get('description') else ""
        value = f"[{company['website']}]({company['website']})\n{description}\nTyp: {company['type']}"
        embed.add_field(
            name=company['name'],
            value=value,
            inline=False
        )
    
    if len(results) > 5:
        embed.set_footer(text=f"Visar 5 av {len(results)} företag")
    
    await ctx.send(embed=embed)

@bot.command(name='stockholm')
async def stockholm(ctx):
    """Visa företag i Greater Stockholm-området"""
    results = db.filter_greater_stockholm()
    
    if not results:
        await ctx.send("❌ Hittade inga företag i Greater Stockholm")
        return
    
    # Skapa embed
    embed = discord.Embed(
        title="🏙️ AI-företag i Greater Stockholm",
        description=f"Hittade {len(results)} praktik-relevanta företag",
        color=discord.Color.teal()
    )
    
    for company in results[:5]:  # Visa max 5
        city = company.get('location_city', 'Stockholm')
        description = company.get('description', '')[:100] + "..." if company.get('description') else ""
        value = f"📍 {city}\n[{company['website']}]({company['website']})\n{description}"
        embed.add_field(
            name=f"{company['name']} ({company['type']})",
            value=value,
            inline=False
        )
    
    if len(results) > 5:
        embed.set_footer(text=f"Visar 5 av {len(results)} företag")
    
    await ctx.send(embed=embed)

# ==================== AUTOMATISK DAGLIG POSTING ====================

@tasks.loop(time=time(hour=8, minute=0))  # Kör kl 08:00 varje dag
async def daily_company():
    """
    Posta 'Dagens AI-företag' automatiskt varje dag kl 08:00
    
    Konfigurera CHANNEL_ID via environment variable eller i .env-fil
    """
    # Läs channel-ID från environment variable
    CHANNEL_ID = os.getenv('DAILY_CHANNEL_ID')
    
    if not CHANNEL_ID:
        print("⚠️  DAILY_CHANNEL_ID är inte konfigurerat")
        print("💡 Sätt DAILY_CHANNEL_ID i .env eller environment variable")
        return
    
    try:
        CHANNEL_ID = int(CHANNEL_ID)
    except ValueError:
        print(f"❌ DAILY_CHANNEL_ID är inte ett giltigt nummer: {CHANNEL_ID}")
        return
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"❌ Kunde inte hitta kanal med ID: {CHANNEL_ID}")
        return
    
    # Hämta dagens företag
    company = db.get_random_company(only_praktik_relevant=True)
    
    if not company:
        await channel.send("❌ Kunde inte hitta dagens företag")
        return
    
    # Skapa meddelande
    embed = discord.Embed(
        title=f"🌅 Dagens AI-företag: {company['name']}",
        url=company['website'] if company['website'] else None,
        description=company['description'][:500] + "..." if company.get('description') and len(company.get('description', '')) > 500 else company.get('description', ''),
        color=discord.Color.gold()
    )
    
    if company.get('website'):
        embed.add_field(name="🌐 Hemsida", value=company['website'], inline=False)
    
    if company.get('location_city'):
        location = company['location_city']
        if company.get('location_greater_stockholm'):
            location += " (Greater Stockholm)"
        embed.add_field(name="📍 Plats", value=location, inline=True)
    
    embed.add_field(name="📊 Typ", value=company['type'].capitalize(), inline=True)
    
    if company.get('ai_capabilities'):
        ai_caps = ', '.join(company['ai_capabilities'][:3])
        embed.add_field(name="🤖 AI-förmågor", value=ai_caps, inline=False)
    
    if company.get('logo_url'):
        embed.set_thumbnail(url=company['logo_url'])
    
    embed.set_footer(text=f"Dagens AI-företag • {datetime.now().strftime('%Y-%m-%d')} • Använd /help för fler kommandon")
    
    await channel.send(embed=embed)
    print(f"✅ Postade dagens företag: {company['name']}")

@daily_company.before_loop
async def before_daily_company():
    """Vänta tills botten är redo innan schemat startar"""
    await bot.wait_until_ready()

# ==================== STARTA BOT ====================

def main():
    """Huvudfunktion - starta botten"""
    
    # Läs bot token från environment variable eller använd hårdkodad
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        
    if not TOKEN:
        print("❌ Bot token saknas!")
        print("💡 Sätt DISCORD_BOT_TOKEN i .env eller environment variable")
        sys.exit(1)
    
    # Läs databas-path från environment variable
    db_path = os.getenv('DATABASE_PATH', 'ai_companies.db')
    
    # Uppdatera global databas-instans
    global db
    db = CompanyDatabase(db_path)
    
    # Kolla att databas finns
    if not Path(db_path).exists():
        print(f"⚠️  VARNING: {db_path} hittades inte!")
        print("💡 Kör 'python build_database.py' först för att skapa databasen")
        print("⏳ Botten startar ändå, men kommandon kommer inte fungera...\n")
    
    try:
        print("🚀 Startar AIM25 Intel Bot...")
        print(f"📁 Databas: {db_path}")
        if os.getenv('DISCORD_BOT_TOKEN'):
            print("🔑 Använder token från environment variable")
        print("⏳ Ansluter till Discord...\n")
        bot.run(TOKEN)
    except Exception as e:
        print(f"\n❌ Kunde inte starta botten: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
