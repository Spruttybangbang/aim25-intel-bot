#!/usr/bin/env python3
"""
EXEMPEL PÅ DISCORD-BOT ANVÄNDNING
==================================
Visar hur man använder databasen i en Discord-bot.

Discord-kommandon exempel:
- !dagens - Dagens AI-företag (push)
- !sök <namn> - Sök efter företag
- !typ <typ> - Filtrera på typ
- !stad <stad> - Filtrera på stad (NYTT!)
- !stockholm - Företag i Greater Stockholm (NYTT!)
"""

from query_database import CompanyQuery, PRAKTIK_RELEVANTA_TYPER


def dagens_ai_foretag():
    """
    'Dagens AI-företag' - för daglig Discord-post
    """
    db = CompanyQuery()
    db.connect()
    
    # Hämta ett slumpmässigt praktik-relevant företag
    companies = db.get_random_companies(
        count=1,
        only_praktik_relevant=True  # VIKTIGT: bara praktik-relevanta!
    )
    
    if companies:
        company = db.get_company_details(companies[0]['id'])
        
        # Format för Discord
        message = f"**🏢 Dagens AI-företag: {company['name']}**\n\n"
        
        if company.get('website'):
            message += f"🌐 {company['website']}\n"
        
        if company.get('location_city'):  # NYTT!
            location = company['location_city']
            if company.get('location_greater_stockholm'):
                location += " (Greater Stockholm)"
            message += f"📍 {location}\n"
        
        message += f"📊 Typ: {company['type']}\n\n"
        
        if company.get('description'):
            message += f"📝 **Om företaget:**\n{company['description'][:500]}...\n\n"
        
        if company.get('ai_capabilities'):
            message += f"🤖 **AI-förmågor:** {', '.join(company['ai_capabilities'][:3])}\n"
        
        db.close()
        return message
    
    db.close()
    return "Kunde inte hitta något företag idag 😢"


def sok_foretag(search_term: str):
    """
    Sök företag - för !sök kommando
    """
    db = CompanyQuery()
    db.connect()
    
    results = db.search_by_name(search_term)
    
    if not results:
        db.close()
        return f"Hittade inga företag som matchar '{search_term}'"
    
    # Ta max 5 resultat
    results = results[:5]
    
    message = f"**🔍 Hittade {len(results)} företag:**\n\n"
    
    for i, company in enumerate(results, 1):
        location = f" - {company['location_city']}" if company.get('location_city') else ""
        message += f"{i}. **{company['name']}** ({company['type']}){location}\n"
        message += f"   {company['website']}\n\n"
    
    db.close()
    return message


def filtrera_typ(company_type: str):
    """
    Filtrera på företagstyp - för !typ kommando
    """
    db = CompanyQuery()
    db.connect()
    
    results = db.filter_companies(
        company_type=company_type,
        limit=5
    )
    
    if not results:
        db.close()
        return f"Hittade inga företag av typ '{company_type}'"
    
    message = f"**🏢 {company_type.capitalize()} ({len(results)} visas):**\n\n"
    
    for company in results:
        location = f" - {company['location_city']}" if company.get('location_city') else ""
        message += f"• **{company['name']}**{location}\n"
        message += f"  {company['website']}\n\n"
    
    db.close()
    return message


def filtrera_stad(city: str):
    """
    Filtrera på stad - för !stad kommando (NYTT!)
    """
    db = CompanyQuery()
    db.connect()
    
    results = db.filter_companies(
        location_city=city,
        only_praktik_relevant=True,  # Bara praktik-relevanta
        limit=10
    )
    
    if not results:
        db.close()
        return f"Hittade inga praktik-relevanta företag i {city}\n⚠️ OBS: Endast EU-företag (~20%) har location-data"
    
    message = f"**📍 AI-företag i {city} ({len(results)} av ~216 med location-data):**\n"
    message += "⚠️ _OBS: my.ai.se-företag (80%) saknar location_\n\n"   

    for company in results:
        message += f"• **{company['name']}** ({company['type']})\n"
        message += f"  {company['website']}\n"
        if company.get('description'):
            message += f"  {company['description'][:100]}...\n"
        message += "\n"
    
    db.close()
    return message


def filtrera_greater_stockholm():
    """
    Filtrera på Greater Stockholm - för !stockholm kommando (NYTT!)
    """
    db = CompanyQuery()
    db.connect()
    
    results = db.filter_companies(
        location_greater_stockholm=True,
        only_praktik_relevant=True,
        limit=10
    )
    
    if not results:
        db.close()
        return "Hittade inga praktik-relevanta företag i Greater Stockholm"
    
    message = f"**🏙️ AI-företag i Greater Stockholm ({len(results)} praktik-relevanta):**\n\n"
    
    for company in results:
        city = company.get('location_city', 'Stockholm')
        message += f"• **{company['name']}** ({company['type']}) - {city}\n"
        message += f"  {company['website']}\n"
        if company.get('description'):
            message += f"  {company['description'][:100]}...\n"
        message += "\n"
    
    db.close()
    return message


# Exempel på Discord-bot integration (pseudo-kod)
"""
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.command(name='dagens')
async def dagens(ctx):
    message = dagens_ai_foretag()
    await ctx.send(message)

@bot.command(name='sök')
async def sok(ctx, *, search_term: str):
    message = sok_foretag(search_term)
    await ctx.send(message)

@bot.command(name='typ')
async def typ(ctx, company_type: str):
    message = filtrera_typ(company_type)
    await ctx.send(message)

@bot.command(name='stad')
async def stad(ctx, city: str):
    message = filtrera_stad(city)
    await ctx.send(message)

@bot.command(name='stockholm')
async def stockholm(ctx):
    message = filtrera_greater_stockholm()
    await ctx.send(message)

bot.run('YOUR_BOT_TOKEN')
"""


if __name__ == "__main__":
    print("🤖 DISCORD-BOT EXEMPEL\n")
    print("=" * 60)
    
    print("\n1. DAGENS AI-FÖRETAG:")
    print("-" * 60)
    print(dagens_ai_foretag())
    
    print("\n2. SÖK EFTER 'Vision':")
    print("-" * 60)
    print(sok_foretag("Vision"))
    
    print("\n3. FILTRERA PÅ TYP 'startup':")
    print("-" * 60)
    print(filtrera_typ("startup"))
    
    print("\n4. FÖRETAG I STOCKHOLM (NYTT!):")
    print("-" * 60)
    print(filtrera_stad("Stockholm"))
    
    print("\n5. GREATER STOCKHOLM (NYTT!):")
    print("-" * 60)
    print(filtrera_greater_stockholm())
