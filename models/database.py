import sqlite3
from typing import List, Tuple, Optional, Dict, Any
from config import DATABASE_PATH

try:
    from utils.logger import get_logger
    logger = get_logger('database')
except ImportError:
    logger = None

class DatabaseConnection:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DATABASE_PATH)
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables"""
        with self._get_connection() as conn:
            c = conn.cursor()
            
            # Leads table
            c.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    link TEXT,
                    ai_summary TEXT,
                    source TEXT DEFAULT 'unknown',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Search history table
            c.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    research_question TEXT,
                    engines TEXT,
                    results_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Lead Workshop Projects table
            c.execute('''
                CREATE TABLE IF NOT EXISTS workshop_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Lead Workshop Analysis table
            c.execute('''
                CREATE TABLE IF NOT EXISTS workshop_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    lead_id INTEGER,
                    relevancy_score INTEGER CHECK (relevancy_score >= 1 AND relevancy_score <= 5),
                    ai_analysis TEXT,
                    key_opinion_leaders TEXT,
                    contact_info TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES workshop_projects (id),
                    FOREIGN KEY (lead_id) REFERENCES leads (id)
                )
            ''')
            
            # Contact Information table
            c.execute('''
                CREATE TABLE IF NOT EXISTS contact_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER,
                    name TEXT,
                    title TEXT,
                    email TEXT,
                    phone TEXT,
                    website TEXT,
                    organization TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES workshop_analysis (id)
                )
            ''')
            
            conn.commit()
    
    def _get_connection(self):
        """Helper to get a connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # Set row_factory for consistent dictionary access
            return conn
        except sqlite3.Error as e:
            if logger:
                logger.error(f"Database connection error: {e}")
            raise
    
    def save_lead(self, title: str, description: str, link: str, ai_summary: str, source: str = 'serp') -> int:
        """Save a lead to database and return the lead ID"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO leads (title, description, link, ai_summary, source) 
                            VALUES (?, ?, ?, ?, ?)''',
                         (title, description, link, ai_summary, source))
                lead_id = c.lastrowid
                conn.commit()
            if logger:
                logger.info(f"Saved lead: {title[:50]}...")
            return lead_id
        except Exception as e:
            if logger:
                logger.error(f"Database error saving lead: {e}")
            return None
    
    def get_all_leads(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all leads from database as dictionaries"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                
                if limit:
                    c.execute('SELECT * FROM leads ORDER BY id DESC LIMIT ?', (limit,))
                else:
                    c.execute('SELECT * FROM leads ORDER BY id DESC')
                
                leads = [dict(row) for row in c.fetchall()]
            if logger:
                logger.debug(f"Retrieved {len(leads)} leads from database")
            return leads
        except Exception as e:
            if logger:
                logger.error(f"Database error getting leads: {e}")
            return []
    
    def get_leads_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get leads by source (serp, pubmed, orcid, etc.) as dictionaries"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM leads WHERE source = ? ORDER BY id DESC', (source,))
                leads = [dict(row) for row in c.fetchall()]
            if logger:
                logger.debug(f"Retrieved {len(leads)} leads from source: {source}")
            return leads
        except Exception as e:
            if logger:
                logger.error(f"Database error getting leads by source: {e}")
            return []
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead by ID"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
                deleted = c.rowcount > 0
                conn.commit()
            if logger:
                if deleted:
                    logger.info(f"Deleted lead with ID: {lead_id}")
                else:
                    logger.warning(f"Lead with ID {lead_id} not found")
            return deleted
        except Exception as e:
            if logger:
                logger.error(f"Database error deleting lead: {e}")
            return False
    
    def save_search_history(self, query: str, research_question: str, engines: str, results_count: int) -> bool:
        """Save search history"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO search_history (query, research_question, engines, results_count) 
                            VALUES (?, ?, ?, ?)''',
                         (query, research_question, engines, results_count))
                conn.commit()
            if logger:
                logger.info(f"Saved search history: {query[:50]}...")
            return True
        except Exception as e:
            if logger:
                logger.error(f"Database error saving search history: {e}")
            return False
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history as dictionaries"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM search_history ORDER BY created_at DESC LIMIT ?', (limit,))
                history = [dict(row) for row in c.fetchall()]
            if logger:
                logger.debug(f"Retrieved {len(history)} search history entries")
            return history
        except Exception as e:
            if logger:
                logger.error(f"Database error getting search history: {e}")
            return []
    
    def get_lead_count(self) -> int:
        """Get total number of leads"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT COUNT(*) FROM leads')
                return c.fetchone()[0]
        except Exception as e:
            if logger:
                logger.error(f"Error getting lead count: {e}")
            return 0
    
    # Lead Workshop Methods
    def create_project(self, name: str, description: str = "") -> int:
        """Create a new workshop project and return project ID"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO workshop_projects (name, description) 
                             VALUES (?, ?)''', (name, description))
                conn.commit()
                return c.lastrowid
        except Exception as e:
            if logger:
                logger.error(f"Error creating project: {e}")
            return None
    
    def get_projects(self) -> list:
        """Get all workshop projects"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM workshop_projects ORDER BY created_at DESC')
                return [dict(row) for row in c.fetchall()]
        except Exception as e:
            if logger:
                logger.error(f"Error getting projects: {e}")
            return []
    
    def get_project(self, project_id: int) -> dict:
        """Get a specific project by ID"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM workshop_projects WHERE id = ?', (project_id,))
                row = c.fetchone()
                return dict(row) if row else None
        except Exception as e:
            if logger:
                logger.error(f"Error getting project: {e}")
            return None
    
    def save_lead_analysis(self, project_id: int, lead_id: int, relevancy_score: int, 
                          ai_analysis: str, key_opinion_leaders: str = "", 
                          contact_info: str = "", notes: str = "") -> int:
        """Save lead analysis to workshop"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO workshop_analysis 
                             (project_id, lead_id, relevancy_score, ai_analysis, key_opinion_leaders, contact_info, notes)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                         (project_id, lead_id, relevancy_score, ai_analysis, key_opinion_leaders, contact_info, notes))
                conn.commit()
                return c.lastrowid
        except Exception as e:
            if logger:
                logger.error(f"Error saving lead analysis: {e}")
            return None
    
    def get_project_analyses(self, project_id: int, sort_by: str = 'relevancy_score', sort_order: str = 'DESC') -> list:
        """Get all analyses for a specific project with sorting options"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                
                # Validate sort parameters
                valid_sort_fields = ['relevancy_score', 'created_at', 'title']
                valid_sort_orders = ['ASC', 'DESC']
                
                if sort_by not in valid_sort_fields:
                    sort_by = 'relevancy_score'
                if sort_order not in valid_sort_orders:
                    sort_order = 'DESC'
                
                # Build the ORDER BY clause
                if sort_by == 'title':
                    order_clause = f'l.{sort_by} {sort_order}'
                else:
                    order_clause = f'wa.{sort_by} {sort_order}'
                
                c.execute(f'''SELECT wa.*, l.title, l.description, l.link, l.source, l.ai_summary
                             FROM workshop_analysis wa
                             LEFT JOIN leads l ON wa.lead_id = l.id
                             WHERE wa.project_id = ?
                             ORDER BY {order_clause}''', (project_id,))
                return [dict(row) for row in c.fetchall()]
        except Exception as e:
            if logger:
                logger.error(f"Error getting project analyses: {e}")
            return []
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete a specific analysis by ID"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('DELETE FROM workshop_analysis WHERE id = ?', (analysis_id,))
                deleted = c.rowcount > 0
                conn.commit()
            if logger:
                if deleted:
                    logger.info(f"Deleted analysis with ID: {analysis_id}")
                else:
                    logger.warning(f"Analysis with ID {analysis_id} not found")
            return deleted
        except Exception as e:
            if logger:
                logger.error(f"Database error deleting analysis: {e}")
            return False
    
    def update_analysis(self, analysis_id: int, relevancy_score: int = None, 
                       ai_analysis: str = None, key_opinion_leaders: str = None,
                       contact_info: str = None, notes: str = None) -> bool:
        """Update an existing analysis"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                
                # Build update query dynamically
                updates = []
                params = []
                
                if relevancy_score is not None:
                    updates.append("relevancy_score = ?")
                    params.append(relevancy_score)
                if ai_analysis is not None:
                    updates.append("ai_analysis = ?")
                    params.append(ai_analysis)
                if key_opinion_leaders is not None:
                    updates.append("key_opinion_leaders = ?")
                    params.append(key_opinion_leaders)
                if contact_info is not None:
                    updates.append("contact_info = ?")
                    params.append(contact_info)
                if notes is not None:
                    updates.append("notes = ?")
                    params.append(notes)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(analysis_id)
                    
                    query = f"UPDATE workshop_analysis SET {', '.join(updates)} WHERE id = ?"
                    c.execute(query, params)
                    conn.commit()
                    return True
                    
        except Exception as e:
            if logger:
                logger.error(f"Error updating analysis: {e}")
            return False
    
    def get_lead_by_id(self, lead_id: int) -> dict:
        """Get a specific lead by ID"""
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM leads WHERE id = ?', (lead_id,))
                row = c.fetchone()
                return dict(row) if row else None
        except Exception as e:
            if logger:
                logger.error(f"Error getting lead: {e}")
            return None

# Global database instance
db = DatabaseConnection()

# Convenience functions for backward compatibility
def save_lead(title: str, description: str, link: str, ai_summary: str, source: str = 'serp') -> int:
    """Save a lead and return the lead ID"""
    return db.save_lead(title, description, link, ai_summary, source)

def get_all_leads(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get all leads as dictionaries"""
    return db.get_all_leads(limit)

def get_leads_by_source(source: str) -> List[Dict[str, Any]]:
    """Get leads by source as dictionaries"""
    return db.get_leads_by_source(source)

def delete_lead(lead_id: int) -> bool:
    """Delete a lead by ID"""
    return db.delete_lead(lead_id)

def save_search_history(query: str, research_question: str, engines: str, results_count: int) -> bool:
    """Save search history"""
    return db.save_search_history(query, research_question, engines, results_count)

def get_search_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent search history as dictionaries"""
    return db.get_search_history(limit)

def get_lead_count() -> int:
    """Get total number of leads"""
    return db.get_lead_count() 