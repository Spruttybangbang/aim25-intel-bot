#!/usr/bin/env python3
"""
TEST-SCRIPT FÖR DISCORD-BOT DATABAS-INTERFACE
==============================================
Testar att CompanyDatabase-klassen fungerar korrekt
"""

from discord_bot import CompanyDatabase
from pathlib import Path

def test_database():
    """Testa databas-anslutning och queries"""
    
    print("🧪 TESTAR DISCORD-BOT DATABAS-INTERFACE\n")
    print("=" * 60)
    
    # Kolla att databas finns
    if not Path("ai_companies.db").exists():
        print("❌ ai_companies.db hittades inte!")
        print("💡 Kör 'python build_database.py' först")
        return False
    
    print("✅ Databas-fil hittad")
    
    # Initiera databas
    db = CompanyDatabase()
    
    # Test 1: Anslutning
    print("\n📋 TEST 1: Databas-anslutning")
    print("-" * 60)
    if db.connect():
        print("✅ Anslutning lyckades")
    else:
        print("❌ Anslutning misslyckades")
        return False
    
    # Test 2: Slumpmässigt företag
    print("\n📋 TEST 2: Hämta slumpmässigt företag")
    print("-" * 60)
    company = db.get_random_company(only_praktik_relevant=True)
    if company:
        print(f"✅ Hittade företag: {company['name']}")
        print(f"   Website: {company.get('website', 'N/A')}")
        print(f"   Typ: {company.get('type', 'N/A')}")
        print(f"   Stad: {company.get('location_city', 'N/A')}")
        if company.get('ai_capabilities'):
            print(f"   AI-förmågor: {', '.join(company['ai_capabilities'][:3])}")
    else:
        print("❌ Kunde inte hitta något företag")
        return False
    
    # Test 3: Sök efter namn
    print("\n📋 TEST 3: Sök efter namn")
    print("-" * 60)
    results = db.search_by_name("AI")
    if results:
        print(f"✅ Hittade {len(results)} företag med 'AI' i namnet")
        for i, comp in enumerate(results[:3], 1):
            print(f"   {i}. {comp['name']}")
    else:
        print("⚠️  Inga resultat för 'AI'")
    
    # Test 4: Filtrera på typ
    print("\n📋 TEST 4: Filtrera på typ (startup)")
    print("-" * 60)
    startups = db.filter_by_type("startup", limit=5)
    if startups:
        print(f"✅ Hittade {len(startups)} startups")
        for i, comp in enumerate(startups[:3], 1):
            print(f"   {i}. {comp['name']}")
    else:
        print("⚠️  Inga startups hittades")
    
    # Test 5: Filtrera på stad
    print("\n📋 TEST 5: Filtrera på stad (Stockholm)")
    print("-" * 60)
    stockholm = db.filter_by_city("Stockholm", limit=5)
    if stockholm:
        print(f"✅ Hittade {len(stockholm)} företag i Stockholm")
        for i, comp in enumerate(stockholm[:3], 1):
            city = comp.get('location_city', 'N/A')
            print(f"   {i}. {comp['name']} ({city})")
    else:
        print("⚠️  Inga företag i Stockholm (normalt om endast my.ai.se-data)")
        print("💡 EU-import krävs för location-data")
    
    # Test 6: Greater Stockholm
    print("\n📋 TEST 6: Greater Stockholm")
    print("-" * 60)
    greater_sthlm = db.filter_greater_stockholm(limit=5)
    if greater_sthlm:
        print(f"✅ Hittade {len(greater_sthlm)} företag i Greater Stockholm")
        for i, comp in enumerate(greater_sthlm[:3], 1):
            city = comp.get('location_city', 'N/A')
            print(f"   {i}. {comp['name']} ({city})")
    else:
        print("⚠️  Inga företag i Greater Stockholm (normalt om endast my.ai.se-data)")
        print("💡 EU-import krävs för location-data")
    
    # Stäng anslutning
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ ALLA TESTER KLARA!")
    print("\n💡 Nästa steg: Kör 'python discord_bot.py' för att starta botten")
    
    return True

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"\n❌ Test misslyckades: {e}")
        import traceback
        traceback.print_exc()
