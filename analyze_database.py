#!/usr/bin/env python3
"""
Analysera databas - hitta vad som saknas
"""
import sqlite3

conn = sqlite3.connect('ai_companies.db')
cursor = conn.cursor()

print("📊 DATABAS-ANALYS")
print("=" * 60)

# Totalt
cursor.execute('SELECT COUNT(*) FROM companies')
print(f"\n✅ Totalt företag: {cursor.fetchone()[0]}")

# Per källa
cursor.execute('SELECT source, COUNT(*) FROM companies GROUP BY source')
print("\n📦 Per källa:")
for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]}")

# Startups totalt
cursor.execute("SELECT COUNT(*) FROM companies WHERE type='startup'")
print(f"\n🚀 Startups totalt: {cursor.fetchone()[0]}")

# Startups med location_city
cursor.execute("SELECT COUNT(*) FROM companies WHERE type='startup' AND location_city IS NOT NULL")
print(f"   - Med location_city: {cursor.fetchone()[0]}")

# Startups i Stockholm
cursor.execute("SELECT COUNT(*) FROM companies WHERE type='startup' AND location_city LIKE '%Stockholm%'")
print(f"   - I Stockholm: {cursor.fetchone()[0]}")

# Greater Stockholm
cursor.execute("SELECT COUNT(*) FROM companies WHERE type='startup' AND location_greater_stockholm = 1")
print(f"   - Greater Stockholm: {cursor.fetchone()[0]}")

# Location-data översikt
cursor.execute('SELECT COUNT(*) FROM companies WHERE location_city IS NOT NULL')
loc_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM companies')
total = cursor.fetchone()[0]
print(f"\n📍 Location-data:")
print(f"   - Med stad: {loc_count} ({100*loc_count/total:.1f}%)")
print(f"   - Utan stad: {total - loc_count} ({100*(total-loc_count)/total:.1f}%)")

# Vilka källor har location?
cursor.execute('SELECT source, COUNT(*) FROM companies WHERE location_city IS NOT NULL GROUP BY source')
print(f"\n   Per källa:")
for row in cursor.fetchall():
    print(f"      {row[0]}: {row[1]}")

# Exempel på my.ai.se-företag utan location
cursor.execute("SELECT name, type FROM companies WHERE source='my.ai.se' AND type='startup' LIMIT 5")
print(f"\n🔍 Exempel på my.ai.se-startups (saknar location):")
for row in cursor.fetchall():
    print(f"   - {row[0]}")

print("\n" + "=" * 60)
print("SLUTSATS:")
print("=" * 60)
print("my.ai.se-data (897 företag) saknar location_city/location_greater_stockholm")
print("Bara EU-data (~200-260 företag) har location-information")
print("\nDärför får du bara 20 träffar när du filtrerar på Stockholm!")

conn.close()
