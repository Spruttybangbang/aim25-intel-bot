#!/usr/bin/env python3
"""
AI-FÖRETAG DATABAS - SQLite Setup
=================================
Detta script skapar och populerar SQLite-databasen med AI-företagsdata.

Användning:
    python build_database.py

Databas: ai_companies.db
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
import re

class CompanyDatabase:
    """Hanterar AI-företagsdatabasen"""
    
    def __init__(self, db_path: str = "ai_companies.db"):
        """
        Initialisera databas-anslutning
        
        Args:
            db_path: Sökväg till SQLite-databasen
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Öppna databas-anslutning"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        print(f"✅ Ansluten till databas: {self.db_path}")
        
    def close(self):
        """Stäng databas-anslutning"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print("✅ Databas-anslutning stängd")
    
    def create_schema(self):
        """
        Skapa databas-schema (tabeller)
        """
        
        print("\n🗄️  Skapar databas-schema...")
        
        # Huvudtabell för företag - NU MED LOCATION-KOLUMNER!
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            website TEXT,
            type TEXT,
            logo_url TEXT,
            description TEXT,
            owner TEXT,
            maturity TEXT,
            
            -- LOCATION-DATA (NYTT!)
            location_city TEXT,
            location_country TEXT DEFAULT 'Sweden',
            location_greater_stockholm BOOLEAN,
            
            -- METADATA
            metadata_source_url TEXT,
            source TEXT DEFAULT 'my.ai.se',
            is_swedish BOOLEAN DEFAULT 1,
            accepts_interns BOOLEAN,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_quality_score INTEGER DEFAULT 0
        )
        ''')
        
        # Tabell för sektorer
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Koppling företag <-> sektorer
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_sectors (
            company_id INTEGER,
            sector_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (sector_id) REFERENCES sectors(id),
            PRIMARY KEY (company_id, sector_id)
        )
        ''')
        
        # Tabell för domäner
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Koppling företag <-> domäner
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_domains (
            company_id INTEGER,
            domain_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (domain_id) REFERENCES domains(id),
            PRIMARY KEY (company_id, domain_id)
        )
        ''')
        
        # Tabell för AI-förmågor
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_capabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Koppling företag <-> AI-förmågor
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_ai_capabilities (
            company_id INTEGER,
            capability_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (capability_id) REFERENCES ai_capabilities(id),
            PRIMARY KEY (company_id, capability_id)
        )
        ''')
        
        # Tabell för dimensioner
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dimensions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Koppling företag <-> dimensioner
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_dimensions (
            company_id INTEGER,
            dimension_id INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (dimension_id) REFERENCES dimensions(id),
            PRIMARY KEY (company_id, dimension_id)
        )
        ''')
        
        # Index för snabbare sökningar
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_company_name ON companies(name)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_company_type ON companies(type)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_company_swedish ON companies(is_swedish)')
        
        # NYA INDEX FÖR LOCATION!
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_location_city ON companies(location_city)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_location_stockholm ON companies(location_greater_stockholm)')
        
        self.conn.commit()
        print("✅ Schema skapat (med location-kolumner)!")
    
    def get_or_create_id(self, table: str, value: str) -> int:
        """Hämta eller skapa ID för värde i lookup-tabell"""
        if not value:
            return None
            
        # Kolla om finns
        self.cursor.execute(f'SELECT id FROM {table} WHERE name = ?', (value,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # Skapa ny
        self.cursor.execute(f'INSERT INTO {table} (name) VALUES (?)', (value,))
        return self.cursor.lastrowid
    
    def parse_list_field(self, value: Any) -> List[str]:
        """Parsa list-fält från JSON"""
        if not value:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if v]
        return [str(value).strip()]
    
    def calculate_quality_score(self, company: Dict) -> int:
        """Beräkna data-kvalitetspoäng (0-100)"""
        score = 0
        
        # Grundläggande fält (40 poäng)
        if company.get('företagsnamn'): score += 15
        if company.get('hemsida'): score += 15
        if company.get('typ'): score += 10
        
        # Beskrivning (30 poäng baserat på längd)
        desc = company.get('beskrivning', '')
        if len(desc) > 50: score += 10
        if len(desc) > 200: score += 10
        if len(desc) > 500: score += 10
        
        # Extra information (30 poäng)
        if company.get('logotyp'): score += 5
        if company.get('ägare'): score += 5
        if company.get('mognadsgrad'): score += 5
        if company.get('sektor'): score += 5
        if company.get('domän'): score += 5
        if company.get('ai_förmågor'): score += 5
        
        return min(score, 100)
    
    def import_myai_data(self, json_path: str):
        """
        Importera data från my.ai.se JSON
        """
        print(f"\n📥 Importerar data från: {json_path}")
        
        # Läs JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        companies = data if isinstance(data, list) else data.get('companies', [])
        print(f"   Hittade {len(companies)} organisationer")
        
        imported = 0
        skipped = 0
        
        for company in companies:
            try:
                # Grunddata
                company_id = int(company.get('id'))
                name = company.get('företagsnamn', '').strip()
                
                if not name:
                    skipped += 1
                    continue
                
                # Beräkna kvalitet
                quality = self.calculate_quality_score(company)
                
                # Infoga företag
                self.cursor.execute('''
                INSERT OR REPLACE INTO companies 
                (id, name, website, type, logo_url, description, owner, maturity, 
                 source, is_swedish, data_quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    company_id,
                    name,
                    company.get('hemsida'),
                    company.get('typ'),
                    company.get('logotyp'),
                    company.get('beskrivning'),
                    company.get('ägare'),
                    company.get('mognadsgrad'),
                    'my.ai.se',
                    True,
                    quality
                ))
                
                # Lägg till sektorer
                sectors = self.parse_list_field(company.get('sektor'))
                for sector in sectors:
                    sector_id = self.get_or_create_id('sectors', sector)
                    if sector_id:
                        self.cursor.execute(
                            'INSERT OR IGNORE INTO company_sectors VALUES (?, ?)',
                            (company_id, sector_id)
                        )
                
                # Lägg till domäner
                domains = self.parse_list_field(company.get('domän'))
                for domain in domains:
                    domain_id = self.get_or_create_id('domains', domain)
                    if domain_id:
                        self.cursor.execute(
                            'INSERT OR IGNORE INTO company_domains VALUES (?, ?)',
                            (company_id, domain_id)
                        )
                
                # Lägg till AI-förmågor
                capabilities = self.parse_list_field(company.get('ai_förmågor'))
                for capability in capabilities:
                    cap_id = self.get_or_create_id('ai_capabilities', capability)
                    if cap_id:
                        self.cursor.execute(
                            'INSERT OR IGNORE INTO company_ai_capabilities VALUES (?, ?)',
                            (company_id, cap_id)
                        )
                
                # Lägg till dimensioner
                dims = self.parse_list_field(company.get('dimension'))
                for dimension in dims:
                    dim_id = self.get_or_create_id('dimensions', dimension)
                    if dim_id:
                        self.cursor.execute(
                            'INSERT OR IGNORE INTO company_dimensions VALUES (?, ?)',
                            (company_id, dim_id)
                        )
                
                imported += 1
                
                if imported % 100 == 0:
                    print(f"   Importerat {imported}/{len(companies)}...")
                    
            except Exception as e:
                print(f"   ⚠️  Kunde inte importera {company.get('företagsnamn', 'okänt')}: {e}")
                skipped += 1
                continue
        
        self.conn.commit()
        print(f"\n✅ Import klar!")
        print(f"   Importerade: {imported}")
        print(f"   Skippade: {skipped}")
    
    def print_stats(self):
        """Visa statistik om databasen"""
        print("\n📊 DATABAS-STATISTIK")
        print("=" * 50)
        
        # Totalt antal företag
        self.cursor.execute('SELECT COUNT(*) FROM companies')
        total = self.cursor.fetchone()[0]
        print(f"Totalt företag: {total}")
        
        # Per typ
        self.cursor.execute('''
        SELECT type, COUNT(*) as count 
        FROM companies 
        WHERE type IS NOT NULL 
        GROUP BY type 
        ORDER BY count DESC
        ''')
        print("\nPer typ:")
        for row in self.cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Datakvalitet
        self.cursor.execute('''
        SELECT 
            AVG(data_quality_score) as avg_score,
            MIN(data_quality_score) as min_score,
            MAX(data_quality_score) as max_score
        FROM companies
        ''')
        stats = self.cursor.fetchone()
        print(f"\nDatakvalitet:")
        print(f"  Genomsnitt: {stats[0]:.1f}")
        print(f"  Min: {stats[1]}")
        print(f"  Max: {stats[2]}")
        
        # Antal sektorer/domäner/capabilities
        for table in ['sectors', 'domains', 'ai_capabilities']:
            self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = self.cursor.fetchone()[0]
            name = table.replace('_', ' ').title()
            print(f"\n{name}: {count}")


def main():
    """Huvudfunktion"""
    json_file = "organizations_data_v3_2.json"
    
    # Kolla att JSON finns
    if not Path(json_file).exists():
        print(f"❌ Kunde inte hitta: {json_file}")
        print("   Kontrollera att filen finns i samma mapp")
        return
    
    # Skapa databas
    db = CompanyDatabase()
    
    try:
        db.connect()
        db.create_schema()
        db.import_myai_data(json_file)
        db.print_stats()
        
        print("\n✅ DATABAS KLAR ATT ANVÄNDA!")
        print(f"   📁 Fil: {db.db_path}")
        print(f"   🔍 Testa den med: python query_database.py")
        
    except Exception as e:
        print(f"\n❌ FEL: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
