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
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime, time
from zoneinfo import ZoneInfo
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
    
    def suggest_types(self, prefix: str = "", limit: int = 25) -> List[str]:
        """Hämta distinkta företagstyper för autocomplete"""
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        if prefix:
            cursor.execute(
                """
                SELECT DISTINCT type FROM companies
                WHERE type IS NOT NULL AND LOWER(type) LIKE LOWER(?)
                ORDER BY type LIMIT ?
                """,
                (f"{prefix}%", limit),
            )
        else:
            cursor.execute(
                """
                SELECT DISTINCT type FROM companies
                WHERE type IS NOT NULL
                ORDER BY type LIMIT ?
                """,
                (limit,),
            )
        return [row[0] for row in cursor.fetchall() if row[0]]

    def suggest_cities(self, prefix: str = "", limit: int = 25) -> List[str]:
        """Hämta distinkta städer för autocomplete"""
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        if prefix:
            cursor.execute(
                """
                SELECT DISTINCT location_city FROM companies
                WHERE location_city IS NOT NULL AND LOWER(location_city) LIKE LOWER(?)
                ORDER BY location_city LIMIT ?
                """,
                (f"{prefix}%", limit),
            )
        else:
            cursor.execute(
                """
                SELECT DISTINCT location_city FROM companies
                WHERE location_city IS NOT NULL
                ORDER BY location_city LIMIT ?
                """,
                (limit,),
            )
        return [row[0] for row in cursor.fetchall() if row[0]]

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

    def get_random_company_strict(self) -> Optional[Dict]:
        """Slumpa ett företag som uppfyller minimikraven för daglig post"""
        if not self.conn:
            return None
        cursor = self.conn.cursor()
        query = """
        SELECT id, name, website, type, logo_url, description, 
               location_city, location_greater_stockholm
        FROM companies
        WHERE type IN ('corporation','startup','supplier')
          AND website IS NOT NULL AND TRIM(website) <> ''
          AND logo_url IS NOT NULL AND TRIM(logo_url) <> ''
          AND description IS NOT NULL AND TRIM(description) <> ''
        ORDER BY RANDOM()
        LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            company_id = result['id']
            cursor.execute(
                """
                SELECT ac.name 
                FROM ai_capabilities ac
                JOIN company_ai_capabilities cac ON ac.id = cac.capability_id
                WHERE cac.company_id = ?
                LIMIT 5
                """,
                (company_id,),
            )
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
        ORDER BY RANDOM()
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

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents, help_command=None)

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
    
    # Synca slash-kommandon (snabbt till en specifik guild om GUILD_ID finns)
    try:
        guild_id = os.getenv('GUILD_ID')
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f'✅ Slash-kommandon synkade till guild {guild_id}: {len(synced)} st')
        else:
            synced = await bot.tree.sync()
            print(f'✅ Globala slash-kommandon synkade: {len(synced)} st (kan ta upp till 1h att dyka upp)')
    except Exception as e:
        print(f'❌ Kunde inte synka slash-kommandon: {e}')
    
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


# ==================== UI HELPERS (PAGINERING) ====================
class PagedResultsView(discord.ui.View):
    def __init__(self, pages: List[List[Dict]], title: str, make_field_line, user_id: int, color: discord.Color = discord.Color.blurple()):
        super().__init__(timeout=120)
        self.pages = pages
        self.index = 0
        self.title = title
        self.make_field_line = make_field_line
        self.user_id = user_id
        self.color = color

    def _embed_for_page(self):
        embed = discord.Embed(title=self.title, description=f"Sida {self.index+1}/{len(self.pages)}", color=self.color)
        for company in self.pages[self.index]:
            name = company['name'] + (f" - {company['location_city']}" if company.get('location_city') else "")
            url = company['website'] or "(saknar hemsida)"
            value = self.make_field_line(company, url)
            embed.add_field(name=name, value=value, inline=False)
        return embed

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self._embed_for_page(), view=self)

    @discord.ui.button(label="◀ Föregående", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Endast den som startade kommandot kan bläddra.", ephemeral=True)
            return
        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Nästa ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Endast den som startade kommandot kan bläddra.", ephemeral=True)
            return
        if self.index < len(self.pages) - 1:
            self.index += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()


def chunk_list(items: List[Dict], size: int) -> List[List[Dict]]:
    return [items[i:i+size] for i in range(0, len(items), size)]


# ==================== AUTOCOMPLETE-CALLBACKS ====================
async def ac_company_type(interaction: discord.Interaction, current: str):
    try:
        suggestions = db.suggest_types(current) if hasattr(db, 'suggest_types') else []
        return [app_commands.Choice(name=t, value=t) for t in suggestions[:25]]
    except Exception:
        return []

async def ac_city(interaction: discord.Interaction, current: str):
    try:
        suggestions = db.suggest_cities(current) if hasattr(db, 'suggest_cities') else []
        return [app_commands.Choice(name=c, value=c) for c in suggestions[:25]]
    except Exception:
        return []

# ==================== BOT-KOMMANDON ====================


@bot.tree.command(name="help", description="Visa hjälp och kommandon")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 AIM25 Intel Bot - Hjälp",
        description="Discord-bot för att hitta AI-företag och praktikplatser",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 Kommandon",
        value=(
            "/dagens – Dagens AI-företag (slumpmässigt praktik-relevant)\n"
            "/sok <namn> – Sök efter företag\n"
            "/typ <typ> – Filtrera på typ (startup, corporation, supplier)\n"
            "/stad <stad> – Hitta företag i specifik stad\n"
            "/stockholm – Företag i Greater Stockholm\n"
            "/help – Visa denna hjälp"
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
    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="dagens", description="Visa ett slumpmässigt praktik-relevant företag")
async def dagens(interaction: discord.Interaction):
    company = db.get_random_company_strict()
    if not company:
        await interaction.response.send_message("❌ Kunde inte hitta något företag. Kolla att databasen finns!", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🏢 {company['name']}",
        url=company['website'] if company['website'] else None,
        description=company['description'][:500] + "..." if company.get('description') and len(company.get('description', '')) > 500 else company.get('description', ''),
        color=discord.Color.green()
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
    embed.set_footer(text=f"Dagens AI-företag • {datetime.now().strftime('%Y-%m-%d')}\nDetta är ett AI-genererat meddelande, dubbelkolla alltid viktig fakta")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="sok", description="Sök efter företag på namn")
@app_commands.describe(search_term="Del av företagsnamn, t.ex. 'Vision'")
async def sok(interaction: discord.Interaction, search_term: str):
    results = db.search_by_name(search_term)
    if not results:
        await interaction.response.send_message(f"❌ Hittade inga företag som matchar '{search_term}'", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🔍 Sökresultat för '{search_term}'",
        description=f"Hittade {len(results)} företag",
        color=discord.Color.blue()
    )
    for i, company in enumerate(results, 1):
        location = f" - {company['location_city']}" if company.get('location_city') else ""
        website = company['website'] if company['website'] else "(saknar hemsida)"
        value = f"{website}{location}\nTyp: {company['type']}"
        embed.add_field(name=f"{i}. {company['name']}", value=value, inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="typ", description="Filtrera företag på typ (startup, corporation, supplier)")
@app_commands.describe(company_type="t.ex. 'startup', 'corporation', 'supplier'")
@app_commands.autocomplete(company_type=ac_company_type)
async def typ(interaction: discord.Interaction, company_type: str):
    # Hämta fler för paginering
    results = db.filter_by_type(company_type, limit=100)
    if not results:
        await interaction.response.send_message(f"❌ Hittade inga företag av typ '{company_type}'\n💡 Prova: startup, corporation, supplier", ephemeral=True)
        return

    pages = chunk_list(results, 5)

    def make_line(c, url):
        return f"{url}\nTyp: {c['type']}"

    view = PagedResultsView(pages, title=f"🏢 {company_type.capitalize()}", make_field_line=make_line, user_id=interaction.user.id, color=discord.Color.purple())
    await interaction.response.send_message(embed=view._embed_for_page(), view=view)


@bot.tree.command(name="stad", description="Hitta praktik-relevanta företag i en stad")
@app_commands.describe(city="t.ex. 'Stockholm'")
@app_commands.autocomplete(city=ac_city)
async def stad(interaction: discord.Interaction, city: str):
    results = db.filter_by_city(city, limit=100)
    if not results:
        await interaction.response.send_message(
            f"❌ Hittade inga praktik-relevanta företag i {city}\n"
            f"⚠️ OBS: Endast ~20% av företagen har location-data (från EU-källa)",
            ephemeral=True
        )
        return

    pages = chunk_list(results, 5)

    def make_line(c, url):
        desc = (c.get('description') or '')
        desc = (desc[:100] + '...') if desc else ''
        return f"{url}\n{desc}\nTyp: {c['type']}"

    title = f"📍 AI-företag i {city}"
    view = PagedResultsView(pages, title=title, make_field_line=make_line, user_id=interaction.user.id, color=discord.Color.orange())
    await interaction.response.send_message(embed=view._embed_for_page(), view=view)


@bot.tree.command(name="stockholm", description="Visa företag i Greater Stockholm")
async def stockholm(interaction: discord.Interaction):
    results = db.filter_greater_stockholm(limit=100)
    if not results:
        await interaction.response.send_message("❌ Hittade inga företag i Greater Stockholm", ephemeral=True)
        return

    pages = chunk_list(results, 5)

    def make_line(c, url):
        city = c.get('location_city', 'Stockholm')
        desc = (c.get('description') or '')
        desc = (desc[:100] + '...') if desc else ''
        return f"📍 {city}\n{url}\n{desc}"

    view = PagedResultsView(pages, title="🏙️ AI-företag i Greater Stockholm", make_field_line=make_line, user_id=interaction.user.id, color=discord.Color.teal())
    await interaction.response.send_message(embed=view._embed_for_page(), view=view)

# ==================== AUTOMATISK DAGLIG POSTING ====================

@tasks.loop(time=time(hour=8, minute=0, tzinfo=ZoneInfo("Europe/Stockholm")))  # Kör kl 08:00 varje dag (Stockholm-tid)
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
    company = db.get_random_company_strict()
    
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
    
    embed.set_footer(text=f"Dagens AI-företag • {datetime.now().strftime('%Y-%m-%d')} • Använd /help för fler kommandon\nDetta är ett AI-genererat meddelande, dubbelkolla alltid viktig fakta")
    
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

# ==================== SLASH-KOMMANDO ERROR HANDLER ====================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    try:
        await interaction.response.send_message(f"❌ Ett fel uppstod: {error}", ephemeral=True)
    except discord.InteractionResponded:
        await interaction.followup.send(f"❌ Ett fel uppstod: {error}", ephemeral=True)