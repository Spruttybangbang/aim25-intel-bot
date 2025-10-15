#!/usr/bin/env python3
"""
AI-FÖRETAG DATABAS - Query Tool
================================
Script för att söka, filtrera och utforska företagsdatabasen.

Användning:
    python query_database.py
"""

import sqlite3
import random
from typing import List, Dict, Optional
import sys


# Definiera praktik-relevanta typer
PRAKTIK_RELEVANTA_TYPER = ['corporation', 'startup', 'supplier']


class CompanyQuery:
    """Verktyg för att söka i företagsdatabasen"""
    
    def __init__(self, db_path: str = "ai_companies.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Anslut till databas"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"❌ Kunde inte ansluta till databas: {e}")
            return False
    
    def close(self):
        """Stäng databas"""
        if self.conn:
            self.conn.close()
    
    def search_by_name(self, search_term: str) -> List[Dict]:
        """Sök företag efter namn"""
        self.cursor.execute('''
        SELECT * FROM companies 
        WHERE name LIKE ? 
        ORDER BY data_quality_score DESC
        ''', (f'%{search_term}%',))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def filter_companies(
        self,
        company_type: Optional[str] = None,
        sector: Optional[str] = None,
        domain: Optional[str] = None,
        ai_capability: Optional[str] = None,
        location_city: Optional[str] = None,  # NYTT!
        location_greater_stockholm: Optional[bool] = None,  # NYTT!
        min_quality: int = 0,
        limit: int = 100,
        only_praktik_relevant: bool = False  # NYTT!
    ) -> List[Dict]:
        """
        Filtrera företag baserat på olika kriterier
        
        Args:
            company_type: Typ av företag
            sector: Sektor
            domain: Domän
            ai_capability: AI-förmåga
            location_city: Stad (NYTT!)
            location_greater_stockholm: Greater Stockholm boolean (NYTT!)
            min_quality: Minimum datakvalitetspoäng
            limit: Max antal resultat
            only_praktik_relevant: Filtrera endast praktik-relevanta typer
        """
        query = 'SELECT DISTINCT c.* FROM companies c'
        conditions = []
        params = []
        
        # Join tables om vi filtrerar på dem
        if sector:
            query += '''
            JOIN company_sectors cs ON c.id = cs.company_id
            JOIN sectors s ON cs.sector_id = s.id
            '''
            conditions.append('s.name LIKE ?')
            params.append(f'%{sector}%')
        
        if domain:
            query += '''
            JOIN company_domains cd ON c.id = cd.company_id
            JOIN domains d ON cd.domain_id = d.id
            '''
            conditions.append('d.name LIKE ?')
            params.append(f'%{domain}%')
        
        if ai_capability:
            query += '''
            JOIN company_ai_capabilities cac ON c.id = cac.company_id
            JOIN ai_capabilities ac ON cac.capability_id = ac.id
            '''
            conditions.append('ac.name LIKE ?')
            params.append(f'%{ai_capability}%')
        
        # WHERE-villkor
        if company_type:
            conditions.append('c.type = ?')
            params.append(company_type)
        
        if min_quality > 0:
            conditions.append('c.data_quality_score >= ?')
            params.append(min_quality)
        
        # LOCATION-FILTER (NYTT!)
        if location_city:
            conditions.append('c.location_city LIKE ?')
            params.append(f'%{location_city}%')
            # OBS: my.ai.se-data (80%) saknar location - bara EU-företag har det
        
        if location_greater_stockholm is not None:
            conditions.append('c.location_greater_stockholm = ?')
            params.append(1 if location_greater_stockholm else 0)
        
        # PRAKTIK-RELEVANT FILTER
        if only_praktik_relevant:
            placeholders = ','.join('?' * len(PRAKTIK_RELEVANTA_TYPER))
            conditions.append(f'c.type IN ({placeholders})')
            params.extend(PRAKTIK_RELEVANTA_TYPER)
        
        # Lägg till WHERE
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY c.data_quality_score DESC LIMIT ?'
        params.append(limit)
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_random_companies(
        self, 
        count: int = 1, 
        company_type: Optional[str] = None,
        only_praktik_relevant: bool = False
    ) -> List[Dict]:
        """Hämta slumpmässiga företag"""
        query = 'SELECT * FROM companies'
        params = []
        conditions = []
        
        if company_type:
            conditions.append('type = ?')
            params.append(company_type)
        
        if only_praktik_relevant:
            placeholders = ','.join('?' * len(PRAKTIK_RELEVANTA_TYPER))
            conditions.append(f'type IN ({placeholders})')
            params.extend(PRAKTIK_RELEVANTA_TYPER)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY RANDOM() LIMIT ?'
        params.append(count)
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_company_details(self, company_id: int) -> Optional[Dict]:
        """Hämta fullständig information om ett företag"""
        # Grundinfo
        self.cursor.execute('SELECT * FROM companies WHERE id = ?', (company_id,))
        company = self.cursor.fetchone()
        
        if not company:
            return None
        
        result = dict(company)
        
        # Sektorer
        self.cursor.execute('''
        SELECT s.name FROM sectors s
        JOIN company_sectors cs ON s.id = cs.sector_id
        WHERE cs.company_id = ?
        ''', (company_id,))
        result['sectors'] = [row[0] for row in self.cursor.fetchall()]
        
        # Domäner
        self.cursor.execute('''
        SELECT d.name FROM domains d
        JOIN company_domains cd ON d.id = cd.domain_id
        WHERE cd.company_id = ?
        ''', (company_id,))
        result['domains'] = [row[0] for row in self.cursor.fetchall()]
        
        # AI-förmågor
        self.cursor.execute('''
        SELECT ac.name FROM ai_capabilities ac
        JOIN company_ai_capabilities cac ON ac.id = cac.capability_id
        WHERE cac.company_id = ?
        ''', (company_id,))
        result['ai_capabilities'] = [row[0] for row in self.cursor.fetchall()]
        
        # Dimensioner
        self.cursor.execute('''
        SELECT d.name FROM dimensions d
        JOIN company_dimensions cd ON d.id = cd.dimension_id
        WHERE cd.company_id = ?
        ''', (company_id,))
        result['dimensions'] = [row[0] for row in self.cursor.fetchall()]
        
        return result
    
    def list_all_values(self, table: str) -> List[str]:
        """Lista alla unika värden från en tabell"""
        valid_tables = ['types', 'sectors', 'domains', 'ai_capabilities', 'dimensions']
        
        if table == 'types':
            self.cursor.execute('SELECT DISTINCT type FROM companies WHERE type IS NOT NULL ORDER BY type')
            return [row[0] for row in self.cursor.fetchall()]
        
        if table in valid_tables and table != 'types':
            self.cursor.execute(f'SELECT name FROM {table} ORDER BY name')
            return [row[0] for row in self.cursor.fetchall()]
        
        return []
    
    def list_cities(self) -> List[tuple]:
        """Lista alla städer med antal företag"""
        self.cursor.execute('''
        SELECT location_city, COUNT(*) as count
        FROM companies
        WHERE location_city IS NOT NULL
        GROUP BY location_city
        ORDER BY count DESC
        ''')
        return self.cursor.fetchall()
    
    def print_company(self, company: Dict, detailed: bool = False):
        """Skriv ut företagsinformation"""
        print("\n" + "=" * 70)
        print(f"🏢 {company['name']}")
        print("=" * 70)
        
        if company.get('website'):
            print(f"🌐 {company['website']}")
        
        if company.get('location_city'):
            location = company['location_city']
            if company.get('location_greater_stockholm'):
                location += " (Greater Stockholm)"
            print(f"📍 {location}")
        
        print(f"📊 Typ: {company.get('type', 'okänt')}")
        print(f"📈 Datakvalitet: {company.get('data_quality_score', 0)}/100")
        print(f"🔗 Källa: {company.get('source', 'okänt')}")
        
        if detailed:
            if company.get('description'):
                print(f"\n📝 Beskrivning:\n{company['description']}")
            
            if company.get('sectors'):
                print(f"\n🏭 Sektorer: {', '.join(company['sectors'])}")
            
            if company.get('domains'):
                print(f"🎯 Domäner: {', '.join(company['domains'])}")
            
            if company.get('ai_capabilities'):
                print(f"🤖 AI-förmågor: {', '.join(company['ai_capabilities'])}")
            
            if company.get('maturity'):
                print(f"📊 Mognadsgrad: {company['maturity']}")
        
        print()


def interactive_menu():
    """Interaktiv meny för att utforska databasen"""
    db = CompanyQuery()
    
    if not db.connect():
        print("❌ Kunde inte ansluta till databasen")
        return
    
    print("\n🤖 AI-FÖRETAG DATABAS")
    print("=" * 50)
    
    try:
        while True:
            print("\n📋 MENY:")
            print("1. Sök efter företagsnamn")
            print("2. Filtrera företag")
            print("3. Visa slumpmässiga företag")
            print("4. Lista tillgängliga kategorier")
            print("5. Lista städer")  # NYTT!
            print("6. Avsluta")
            
            choice = input("\nVälj alternativ (1-6): ").strip()
            
            if choice == "1":
                search_term = input("Sökord: ").strip()
                results = db.search_by_name(search_term)
                
                if results:
                    print(f"\n✅ Hittade {len(results)} företag:")
                    for i, company in enumerate(results[:10], 1):
                        location = f" - {company['location_city']}" if company.get('location_city') else ""
                        print(f"\n{i}. {company['name']} ({company['type']}){location}")
                        print(f"   {company['website']}")
                    
                    if len(results) > 10:
                        print(f"\n... och {len(results) - 10} till")
                    
                    detail = input("\nVisa detaljer för företag? (nummer eller 'n'): ").strip()
                    if detail.isdigit() and 1 <= int(detail) <= len(results):
                        company_id = results[int(detail)-1]['id']
                        detailed = db.get_company_details(company_id)
                        db.print_company(detailed, detailed=True)
                else:
                    print("\n❌ Inga företag hittades")
            
            elif choice == "2":
                print("\n🔍 FILTER (lämna tomt för att hoppa över):")
                
                types = db.list_all_values('types')
                print(f"\nTillgängliga typer: {', '.join(types)}")
                company_type = input("Företagstyp: ").strip() or None
                
                city = input("Stad (t.ex. Stockholm, Göteborg) ⚠️ Bara EU-företag har location: ").strip() or None

                greater_sthlm = input("Greater Stockholm? (j/n): ").strip().lower()  # NYTT!
                greater_stockholm = True if greater_sthlm == 'j' else None if not greater_sthlm else False
                
                sector = input("Sektor (del av namn): ").strip() or None
                ai_cap = input("AI-förmåga (del av namn): ").strip() or None
                
                praktik = input("Endast praktik-relevanta? (j/n): ").strip().lower()
                only_praktik = praktik == 'j'
                
                results = db.filter_companies(
                    company_type=company_type,
                    location_city=city,
                    location_greater_stockholm=greater_stockholm,
                    sector=sector,
                    ai_capability=ai_cap,
                    only_praktik_relevant=only_praktik,
                    limit=100
                )
                
                if results:
                    print(f"\n✅ Hittade {len(results)} företag:")
                    for i, company in enumerate(results, 1):
                        location = f" - {company['location_city']}" if company.get('location_city') else ""
                        print(f"\n{i}. {company['name']} ({company['type']}){location}")
                        print(f"   {company['website']}")
                        if company.get('description'):
                            desc = company['description'][:100] + "..."
                            print(f"   {desc}")
                else:
                    print("\n❌ Inga företag matchade filtret")
            
            elif choice == "3":
                count = input("Antal företag (1-10): ").strip()
                count = int(count) if count.isdigit() else 1
                count = min(max(count, 1), 10)
                
                praktik = input("Endast praktik-relevanta? (j/n): ").strip().lower()
                only_praktik = praktik == 'j'
                
                results = db.get_random_companies(count, only_praktik_relevant=only_praktik)
                
                for company in results:
                    detailed = db.get_company_details(company['id'])
                    db.print_company(detailed, detailed=True)
            
            elif choice == "4":
                print("\n📊 TILLGÄNGLIGA KATEGORIER:")
                
                print("\n🏢 Företagstyper:")
                types = db.list_all_values('types')
                for t in types:
                    print(f"   • {t}")
                
                print("\n🏭 Sektorer (top 10):")
                sectors = db.list_all_values('sectors')[:10]
                for s in sectors:
                    print(f"   • {s}")
                
                print("\n🎯 Domäner (top 10):")
                domains = db.list_all_values('domains')[:10]
                for d in domains:
                    print(f"   • {d}")
                
                print("\n🤖 AI-förmågor:")
                ai_caps = db.list_all_values('ai_capabilities')
                for a in ai_caps:
                    print(f"   • {a}")
            
            elif choice == "5":  # NYTT!
                print("\n🏙️  STÄDER MED AI-FÖRETAG:")
                cities = db.list_cities()
                for city, count in cities[:20]:
                    print(f"   • {city}: {count} företag")
                if len(cities) > 20:
                    print(f"\n... och {len(cities) - 20} andra städer")
            
            elif choice == "6":
                print("\n👋 Hej då!")
                break
            
            else:
                print("\n❌ Ogiltigt val")
                
    finally:
        db.close()


if __name__ == "__main__":
    interactive_menu()
