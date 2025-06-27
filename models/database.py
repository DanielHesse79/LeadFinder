import sqlite3
from typing import List, Tuple, Optional
from config import DB_PATH

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create leads table
        c.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            snippet TEXT,
            link TEXT,
            ai_summary TEXT,
            source TEXT DEFAULT 'serp',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create search_history table
        c.execute('''CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            research_question TEXT,
            engines TEXT,
            results_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
    
    def save_lead(self, title: str, snippet: str, link: str, ai_summary: str, source: str = 'serp') -> bool:
        """Save a lead to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO leads (title, snippet, link, ai_summary, source) 
                        VALUES (?, ?, ?, ?, ?)''',
                     (title, snippet, link, ai_summary, source))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[LOG] Database error saving lead: {e}")
            return False
    
    def get_all_leads(self, limit: Optional[int] = None) -> List[Tuple]:
        """Get all leads from database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if limit:
            c.execute('SELECT * FROM leads ORDER BY id DESC LIMIT ?', (limit,))
        else:
            c.execute('SELECT * FROM leads ORDER BY id DESC')
        
        leads = c.fetchall()
        conn.close()
        return leads
    
    def get_leads_by_source(self, source: str) -> List[Tuple]:
        """Get leads by source (serp, pubmed, orcid, etc.)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM leads WHERE source = ? ORDER BY id DESC', (source,))
        leads = c.fetchall()
        conn.close()
        return leads
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[LOG] Database error deleting lead: {e}")
            return False
    
    def save_search_history(self, query: str, research_question: str, engines: str, results_count: int) -> bool:
        """Save search history"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO search_history (query, research_question, engines, results_count) 
                        VALUES (?, ?, ?, ?)''',
                     (query, research_question, engines, results_count))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[LOG] Database error saving search history: {e}")
            return False
    
    def get_search_history(self, limit: int = 10) -> List[Tuple]:
        """Get recent search history"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM search_history ORDER BY created_at DESC LIMIT ?', (limit,))
        history = c.fetchall()
        conn.close()
        return history
    
    def get_lead_count(self) -> int:
        """Get total number of leads"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM leads')
        count = c.fetchone()[0]
        conn.close()
        return count

# Global database instance
db = DatabaseManager() 