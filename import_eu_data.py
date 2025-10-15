#!/usr/bin/env python3
"""
EU-DATA IMPORT - Plan A (Konservativ)
=====================================
Importerar EU-företag till SQLite-databasen.
Endast unika företag (dubblettfiltrering).

Användning:
    python import_eu_data.py companies_from_eu_site_no_name_headers.csv

Plan A: Bara unika, ingen merge
"""

import sqlite3
import csv
import re
from typing import Dict, List, Set
from pathlib import Path
import sys


class EUImporter:
    """Hanterar import av EU-data"""
    
    def __init__(self, db_path: str = "ai_companies.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Anslut till databas"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        print(f"✅ Ansluten till: {self.db_path}")
    
    def close(self):
        """Stäng databas"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def normalize_name(self, name: str) -> str:
        """
        Normalisera företagsnamn för dubblettjämförelse
        
        Exempel:
        "AI Sweden AB" → "ai sweden"
        "Kognic Technologies Aktiebolag" → "kognic technologies"
        """
        if not name:
            return ""
        
        name = name.lower().strip()
        
        # Ta bort företagsformer
        suffixes = [
            ' ab', ' aktiebolag', ' ltd', ' limited', 
            ' inc', ' gmbh', ' technology', ' technologies'
        ]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        # Ta bort extra mellanslag
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def get_existing_normalized_names(self) -> Set[str]:
        """Hämta normaliserade namn från befintliga företag"""
        self.cursor.execute('SELECT name FROM companies')
        names = set()
        
        for row in self.cursor.fetchall():
            norm_name = self.normalize_name(row[0])
            if norm_name:
                names.add(norm_name)
        
        print(f"   Hittade {len(names)} befintliga företag för dubblettcheck")
        return names
    
    def extract_city(self, location: str) -> str:
        """
        Extrahera stad från Location-fältet
        
        Exempel:
        "Stockholm, Sweden" → "Stockholm"
        "Bromma, Stockholm" → "Bromma"
        """
        if not location:
            return None
        
        # Ta första delen före komma
        city = location.split(',')[0].strip()
        return city if city else None
    
    def parse_greater_stockholm(self, value: str) -> bool:
        """
        Parsa Greater Stockholm Y/N-fältet
        
        Hanterar: "Yes", "No", "yes", "no", "Nej", "nej"
        """
        if not value:
            return False
        
        value = value.lower().strip()
        return value in ['yes', 'y']
    
    def parse_types(self, type_string: str) -> List[str]:
        """
        Parsa type-fältet till lista
        
        Exempel:
        "artificial intelligence, saas" → ["artificial intelligence", "saas"]
        """
        if not type_string:
            return []
        
        return [t.strip() for t in type_string.split(',') if t.strip()]
    
    def calculate_quality_score(self, company: Dict) -> int:
        """Beräkna datakvalitetspoäng för EU-företag"""
        score = 0
        
        # Grundläggande (40 poäng)
        if company.get('name'): score += 15
        if company.get('website'): score += 15
        if company.get('type'): score += 10
        
        # Beskrivning (30 poäng - EU har ofta bra beskrivningar!)
        desc = company.get('description', '')
        if len(desc) > 50: score += 10
        if len(desc) > 200: score += 10
        if len(desc) > 500: score += 10
        
        # Extra information (30 poäng)
        if company.get('logo_url'): score += 10
        if company.get('location_city'): score += 10
        if company.get('metadata_source_url'): score += 5
        if company.get('types'): score += 5
        
        return min(score, 100)
    
    def get_next_id(self) -> int:
        """Hämta nästa lediga ID"""
        self.cursor.execute('SELECT MAX(id) FROM companies')
        max_id = self.cursor.fetchone()[0]
        return (max_id or 0) + 1
    
    def get_or_create_capability_id(self, capability: str) -> int:
        """Hämta eller skapa AI-capability ID"""
        if not capability:
            return None
        
        # Kolla om finns
        self.cursor.execute(
            'SELECT id FROM ai_capabilities WHERE name = ?', 
            (capability,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # Skapa ny
        self.cursor.execute(
            'INSERT INTO ai_capabilities (name) VALUES (?)', 
            (capability,)
        )
        return self.cursor.lastrowid
    
    def import_csv(self, csv_path: str, only_unique: bool = True):
        """
        Huvudfunktion för EU-import
        
        Args:
            csv_path: Sökväg till EU CSV
            only_unique: Om True, skippa dubbletter (Plan A)
        """
        print(f"\n📥 IMPORTERAR EU-DATA")
        print(f"   Fil: {csv_path}")
        print(f"   Strategi: Plan A (endast unika)")
        print("=" * 60)
        
        # Hämta befintliga namn
        existing_names = self.get_existing_normalized_names()
        
        # Statistik
        imported = 0
        skipped_duplicates = 0
        skipped_errors = 0
        
        # Öppna CSV (VIKTIGT: semikolon-separerad!)
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                try:
                    # Normalisera namn för dubblettcheck
                    norm_name = self.normalize_name(row['name'])
                    
                    # Kolla om dublett
                    if only_unique and norm_name in existing_names:
                        skipped_duplicates += 1
                        continue
                    
                    # Nästa ID
                    next_id = self.get_next_id()
                    
                    # Extrahera stad
                    city = self.extract_city(row['Location'])
                    
                    # Parsa Greater Stockholm
                    greater_stockholm = self.parse_greater_stockholm(
                        row['Greater Stockholm Y/N']
                    )
                    
                    # Parsa types
                    types = self.parse_types(row['type'])
                    
                    # Bygg company-dict
                    company = {
                        'name': row['name'].strip(),
                        'description': row['description'].strip(),
                        'website': row['website'].strip(),
                        'logo_url': row['image_url'].strip(),
                        'location_city': city,
                        'location_country': 'Sweden',
                        'location_greater_stockholm': greater_stockholm,
                        'metadata_source_url': row['source_page'].strip(),
                        'types': types,
                        'type': 'startup',  # Default för EU-företag
                        'source': 'eu-site',
                        'is_swedish': True
                    }
                    
                    # Beräkna kvalitet
                    quality = self.calculate_quality_score(company)
                    
                    # Infoga i databas
                    self.cursor.execute('''
                    INSERT INTO companies 
                    (id, name, website, type, logo_url, description,
                     location_city, location_country, location_greater_stockholm,
                     metadata_source_url, source, is_swedish, data_quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        next_id,
                        company['name'],
                        company['website'],
                        company['type'],
                        company['logo_url'],
                        company['description'],
                        company['location_city'],
                        company['location_country'],
                        company['location_greater_stockholm'],
                        company['metadata_source_url'],
                        company['source'],
                        company['is_swedish'],
                        quality
                    ))
                    
                    # Lägg till AI-capabilities
                    for capability in types:
                        cap_id = self.get_or_create_capability_id(capability)
                        if cap_id:
                            self.cursor.execute('''
                            INSERT OR IGNORE INTO company_ai_capabilities 
                            VALUES (?, ?)
                            ''', (next_id, cap_id))
                    
                    # Lägg till i existing_names för nästa iteration
                    existing_names.add(norm_name)
                    
                    imported += 1
                    
                    # Progress
                    if imported % 50 == 0:
                        print(f"   Importerade {imported}...")
                
                except Exception as e:
                    print(f"   ⚠️  Fel på {row.get('name', 'okänt')}: {e}")
                    skipped_errors += 1
                    continue
        
        self.conn.commit()
        
        # Resultat
        print("\n" + "=" * 60)
        print("✅ EU-IMPORT KLAR!")
        print("=" * 60)
        print(f"✅ Importerade: {imported} nya företag")
        print(f"⚠️  Skippade (dubbletter): {skipped_duplicates}")
        if skipped_errors > 0:
            print(f"❌ Fel: {skipped_errors}")
        print()


def main():
    """Huvudfunktion"""
    if len(sys.argv) < 2:
        print("Användning: python import_eu_data.py <csv_file>")
        print("Exempel: python import_eu_data.py companies_from_eu_site_no_name_headers.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Kolla att CSV finns
    if not Path(csv_file).exists():
        print(f"❌ Kunde inte hitta: {csv_file}")
        sys.exit(1)
    
    # Kolla att databas finns
    db_path = "ai_companies.db"
    if not Path(db_path).exists():
        print(f"❌ Databas saknas: {db_path}")
        print("   Kör först: python build_database.py")
        sys.exit(1)
    
    # Importera
    importer = EUImporter(db_path)
    
    try:
        importer.connect()
        importer.import_csv(csv_file, only_unique=True)
        
        print("🎉 Klart! Testa med: python query_database.py")
        
    except Exception as e:
        print(f"\n❌ FEL: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        importer.close()


if __name__ == "__main__":
    main()
