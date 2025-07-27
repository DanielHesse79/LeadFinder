import sqlite3
from typing import List, Tuple, Optional, Dict, Any
from config import DATABASE_PATH

try:
    from utils.logger import get_logger
    logger = get_logger('database')
except ImportError:
    logger = None

# Import the connection pool
try:
    from models.database_pool import get_db_pool
except ImportError:
    get_db_pool = None

class DatabaseConnection:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DATABASE_PATH)
        self.pool = get_db_pool() if get_db_pool else None
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables"""
        if self.pool:
            # Use connection pool
            with self.pool.get_connection() as conn:
                c = conn.cursor()
                self._create_tables_with_cursor(c)
                conn.commit()
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                self._create_tables_with_cursor(c)
                conn.commit()
    
    def _create_tables_with_cursor(self, c):
        """Create all necessary tables using the provided cursor"""
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
        
        # RAG Document Chunks table
        c.execute('''
            CREATE TABLE IF NOT EXISTS rag_document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT UNIQUE NOT NULL,
                doc_id TEXT NOT NULL,
                source TEXT NOT NULL,
                content_chunk TEXT NOT NULL,
                embedding_id TEXT,
                chunk_index INTEGER DEFAULT 0,
                total_chunks INTEGER DEFAULT 1,
                metadata TEXT,  -- JSON string for additional metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RAG Search Sessions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS rag_search_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                query TEXT NOT NULL,
                rag_response TEXT,
                traditional_results_count INTEGER DEFAULT 0,
                rag_results_count INTEGER DEFAULT 0,
                processing_time REAL,
                confidence_score REAL,
                retrieval_method TEXT,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc_id ON rag_document_chunks(doc_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_rag_chunks_source ON rag_document_chunks(source)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_rag_sessions_query ON rag_search_sessions(query)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_rag_sessions_created ON rag_search_sessions(created_at)')
    
    def _get_connection(self):
        """Helper to get a connection with error handling (fallback method)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # Set row_factory for consistent dictionary access
            return conn
        except sqlite3.Error as e:
            if logger:
                logger.error(f"Database connection error: {e}")
            raise
    
    def save_lead(self, title: str, description: str, link: str, ai_summary: str, source: str = 'serp') -> int:
        """Save a new lead to the database"""
        query = '''
            INSERT INTO leads (title, description, link, ai_summary, source)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (title, description, link, ai_summary, source)
        
        if self.pool:
            return self.pool.execute_update(query, params)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.lastrowid
    
    def get_all_leads(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all leads from the database"""
        query = 'SELECT * FROM leads ORDER BY created_at DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        if self.pool:
            return self.pool.execute_query(query)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query)
                results = c.fetchall()
                return [dict(row) for row in results]
    
    def get_leads_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get leads filtered by source"""
        query = 'SELECT * FROM leads WHERE source = ? ORDER BY created_at DESC'
        params = (source,)
        
        if self.pool:
            return self.pool.execute_query(query, params)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                results = c.fetchall()
                return [dict(row) for row in results]
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead by ID"""
        query = 'DELETE FROM leads WHERE id = ?'
        params = (lead_id,)
        
        if self.pool:
            affected_rows = self.pool.execute_update(query, params)
            return affected_rows > 0
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.rowcount > 0
    
    def save_search_history(self, query: str, research_question: str, engines: str, results_count: int) -> bool:
        """Save search history"""
        sql_query = '''
            INSERT INTO search_history (query, research_question, engines, results_count)
            VALUES (?, ?, ?, ?)
        '''
        params = (query, research_question, engines, results_count)
        
        if self.pool:
            affected_rows = self.pool.execute_update(sql_query, params)
            return affected_rows > 0
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(sql_query, params)
                conn.commit()
                return c.rowcount > 0
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get search history"""
        query = 'SELECT * FROM search_history ORDER BY created_at DESC LIMIT ?'
        params = (limit,)
        
        if self.pool:
            return self.pool.execute_query(query, params)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                results = c.fetchall()
                return [dict(row) for row in results]
    
    def get_lead_count(self) -> int:
        """Get total number of leads"""
        query = 'SELECT COUNT(*) as count FROM leads'
        
        if self.pool:
            results = self.pool.execute_query(query)
            return results[0]['count'] if results else 0
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query)
                result = c.fetchone()
                return result[0] if result else 0
    
    def create_project(self, name: str, description: str = "") -> int:
        """Create a new workshop project"""
        query = 'INSERT INTO workshop_projects (name, description) VALUES (?, ?)'
        params = (name, description)
        
        if self.pool:
            return self.pool.execute_update(query, params)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.lastrowid
    
    def get_projects(self) -> list:
        """Get all workshop projects"""
        query = 'SELECT * FROM workshop_projects ORDER BY created_at DESC'
        
        if self.pool:
            return self.pool.execute_query(query)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query)
                results = c.fetchall()
                return [dict(row) for row in results]
    
    def get_project(self, project_id: int) -> dict:
        """Get a specific workshop project"""
        query = 'SELECT * FROM workshop_projects WHERE id = ?'
        params = (project_id,)
        
        if self.pool:
            results = self.pool.execute_query(query, params)
            return results[0] if results else None
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                result = c.fetchone()
                return dict(result) if result else None
    
    def save_lead_analysis(self, project_id: int, lead_id: int, relevancy_score: int, 
                          ai_analysis: str, key_opinion_leaders: str = "", 
                          contact_info: str = "", notes: str = "") -> int:
        """Save lead analysis for a workshop project"""
        query = '''
            INSERT INTO workshop_analysis 
            (project_id, lead_id, relevancy_score, ai_analysis, key_opinion_leaders, contact_info, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (project_id, lead_id, relevancy_score, ai_analysis, 
                 key_opinion_leaders, contact_info, notes)
        
        if self.pool:
            return self.pool.execute_update(query, params)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.lastrowid
    
    def get_project_analyses(self, project_id: int, sort_by: str = 'relevancy_score', sort_order: str = 'DESC') -> list:
        """Get all analyses for a workshop project"""
        # Validate sort parameters
        valid_sort_fields = ['relevancy_score', 'created_at', 'updated_at']
        valid_sort_orders = ['ASC', 'DESC']
        
        if sort_by not in valid_sort_fields:
            sort_by = 'relevancy_score'
        if sort_order not in valid_sort_orders:
            sort_order = 'DESC'
        
        query = f'''
            SELECT wa.*, l.title, l.description, l.link, l.source
            FROM workshop_analysis wa
            JOIN leads l ON wa.lead_id = l.id
            WHERE wa.project_id = ?
            ORDER BY wa.{sort_by} {sort_order}
        '''
        params = (project_id,)
        
        if self.pool:
            return self.pool.execute_query(query, params)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                results = c.fetchall()
                return [dict(row) for row in results]
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete a lead analysis"""
        query = 'DELETE FROM workshop_analysis WHERE id = ?'
        params = (analysis_id,)
        
        if self.pool:
            affected_rows = self.pool.execute_update(query, params)
            return affected_rows > 0
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.rowcount > 0
    
    def update_analysis(self, analysis_id: int, relevancy_score: int = None, 
                       ai_analysis: str = None, key_opinion_leaders: str = None,
                       contact_info: str = None, notes: str = None) -> bool:
        """Update a lead analysis"""
        # Build dynamic update query
        update_parts = []
        params = []
        
        if relevancy_score is not None:
            update_parts.append('relevancy_score = ?')
            params.append(relevancy_score)
        
        if ai_analysis is not None:
            update_parts.append('ai_analysis = ?')
            params.append(ai_analysis)
        
        if key_opinion_leaders is not None:
            update_parts.append('key_opinion_leaders = ?')
            params.append(key_opinion_leaders)
        
        if contact_info is not None:
            update_parts.append('contact_info = ?')
            params.append(contact_info)
        
        if notes is not None:
            update_parts.append('notes = ?')
            params.append(notes)
        
        if not update_parts:
            return False
        
        update_parts.append('updated_at = CURRENT_TIMESTAMP')
        params.append(analysis_id)
        
        query = f'UPDATE workshop_analysis SET {", ".join(update_parts)} WHERE id = ?'
        
        if self.pool:
            affected_rows = self.pool.execute_update(query, tuple(params))
            return affected_rows > 0
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.rowcount > 0
    
    def get_lead_by_id(self, lead_id: int) -> dict:
        """Get a specific lead by ID"""
        query = 'SELECT * FROM leads WHERE id = ?'
        params = (lead_id,)
        
        if self.pool:
            results = self.pool.execute_query(query, params)
            return results[0] if results else None
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                result = c.fetchone()
                return dict(result) if result else None
    
    # RAG-related methods
    def save_rag_chunk(self, chunk_id: str, doc_id: str, source: str, content_chunk: str, 
                      embedding_id: str = None, chunk_index: int = 0, total_chunks: int = 1, 
                      metadata: str = None) -> bool:
        """Save a RAG document chunk to the database"""
        query = '''
            INSERT OR REPLACE INTO rag_document_chunks 
            (chunk_id, doc_id, source, content_chunk, embedding_id, chunk_index, total_chunks, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (chunk_id, doc_id, source, content_chunk, embedding_id, chunk_index, total_chunks, metadata)
        
        if self.pool:
            affected_rows = self.pool.execute_update(query, params)
            return affected_rows > 0
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.rowcount > 0
    
    def get_rag_chunks_by_doc_id(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        query = '''
            SELECT * FROM rag_document_chunks 
            WHERE doc_id = ? 
            ORDER BY chunk_index
        '''
        params = (doc_id,)
        
        if self.pool:
            results = self.pool.execute_query(query, params)
            return [dict(row) for row in results]
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                results = c.fetchall()
                return [dict(row) for row in results]
    
    def save_rag_search_session(self, session_id: str, query: str, rag_response: str = None,
                               traditional_results_count: int = 0, rag_results_count: int = 0,
                               processing_time: float = 0.0, confidence_score: float = 0.0,
                               retrieval_method: str = None, model_used: str = None) -> bool:
        """Save a RAG search session to the database"""
        query = '''
            INSERT INTO rag_search_sessions 
            (session_id, query, rag_response, traditional_results_count, rag_results_count, 
             processing_time, confidence_score, retrieval_method, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (session_id, query, rag_response, traditional_results_count, rag_results_count,
                 processing_time, confidence_score, retrieval_method, model_used)
        
        if self.pool:
            affected_rows = self.pool.execute_update(query, params)
            return affected_rows > 0
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                return c.rowcount > 0
    
    def get_rag_search_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent RAG search sessions"""
        query = '''
            SELECT * FROM rag_search_sessions 
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        params = (limit,)
        
        if self.pool:
            results = self.pool.execute_query(query, params)
            return [dict(row) for row in results]
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(query, params)
                results = c.fetchall()
                return [dict(row) for row in results]
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            stats = {}
        
        # Get chunk statistics
        chunk_query = '''
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT doc_id) as total_documents,
                COUNT(DISTINCT source) as total_sources
            FROM rag_document_chunks
        '''
        
        # Get session statistics
        session_query = '''
            SELECT 
                COUNT(*) as total_sessions,
                AVG(processing_time) as avg_processing_time,
                AVG(confidence_score) as avg_confidence_score
            FROM rag_search_sessions
        '''
        
        if self.pool:
            chunk_results = self.pool.execute_query(chunk_query)
            session_results = self.pool.execute_query(session_query)
        else:
            # Fallback to direct connection
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute(chunk_query)
                chunk_results = c.fetchall()
                c.execute(session_query)
                session_results = c.fetchall()
        
        if chunk_results:
            stats.update(dict(chunk_results[0]))
        
        if session_results:
            session_stats = dict(session_results[0])
            # Ensure values are not None before using round()
            avg_processing_time = session_stats.get('avg_processing_time', 0) or 0
            avg_confidence_score = session_stats.get('avg_confidence_score', 0) or 0
            
            stats.update({
                'total_sessions': session_stats.get('total_sessions', 0) or 0,
                'avg_processing_time': round(avg_processing_time, 3),
                'avg_confidence_score': round(avg_confidence_score, 3)
            })
        
        return stats
        
        except Exception as e:
            if logger:
                logger.error(f"Error getting RAG stats: {str(e)}")
            return {
                'total_chunks': 0,
                'total_documents': 0,
                'total_sources': 0,
                'total_sessions': 0,
                'avg_processing_time': 0.0,
                'avg_confidence_score': 0.0
            }

    def get_lead_stats(self) -> Dict[str, Any]:
        """Get lead management statistics"""
        try:
            if self.pool:
                with self.pool.get_connection() as conn:
                    c = conn.cursor()
                    return self._get_lead_stats_with_cursor(c)
            else:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    return self._get_lead_stats_with_cursor(c)
        except Exception as e:
            if logger:
                logger.error(f"Error getting lead stats: {str(e)}")
            return {
                'total_leads': 0,
                'total_searches': 0,
                'ai_analyses': 0,
                'leads_by_source': {},
                'recent_activity': []
            }

    def _get_lead_stats_with_cursor(self, c) -> Dict[str, Any]:
        """Get lead statistics using the provided cursor"""
        # Get total leads
        c.execute('SELECT COUNT(*) FROM leads')
        total_leads = c.fetchone()[0]
        
        # Get total searches
        c.execute('SELECT COUNT(*) FROM search_history')
        total_searches = c.fetchone()[0]
        
        # Get AI analyses (leads with AI summaries)
        c.execute('SELECT COUNT(*) FROM leads WHERE ai_summary IS NOT NULL AND ai_summary != ""')
        ai_analyses = c.fetchone()[0]
        
        # Get leads by source
        c.execute('SELECT source, COUNT(*) FROM leads GROUP BY source')
        leads_by_source = dict(c.fetchall())
        
        # Get recent activity (last 5 leads)
        c.execute('''
            SELECT title, source, created_at 
            FROM leads 
            ORDER BY created_at DESC 
            LIMIT 5
        ''')
        recent_leads = c.fetchall()
        
        recent_activity = []
        for lead in recent_leads:
            recent_activity.append({
                'type': 'lead',
                'title': lead[0],
                'source': lead[1],
                'created_at': lead[2]
            })
        
        return {
            'total_leads': total_leads,
            'total_searches': total_searches,
            'ai_analyses': ai_analyses,
            'leads_by_source': leads_by_source,
            'recent_activity': recent_activity
        }

# Global database instance
db = DatabaseConnection()

# Convenience functions for backward compatibility
def save_lead(title: str, description: str, link: str, ai_summary: str, source: str = 'serp') -> int:
    return db.save_lead(title, description, link, ai_summary, source)

def get_all_leads(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    return db.get_all_leads(limit)

def get_leads_by_source(source: str) -> List[Dict[str, Any]]:
    return db.get_leads_by_source(source)

def delete_lead(lead_id: int) -> bool:
    return db.delete_lead(lead_id)

def save_search_history(query: str, research_question: str, engines: str, results_count: int) -> bool:
    return db.save_search_history(query, research_question, engines, results_count)

def get_search_history(limit: int = 10) -> List[Dict[str, Any]]:
    return db.get_search_history(limit)

def get_lead_count() -> int:
    return db.get_lead_count()

# RAG-related database methods
def save_rag_chunk(chunk_id: str, doc_id: str, source: str, content_chunk: str, 
                  embedding_id: str = None, chunk_index: int = 0, total_chunks: int = 1, 
                  metadata: str = None) -> bool:
    """Save a RAG document chunk to the database"""
    return db.save_rag_chunk(chunk_id, doc_id, source, content_chunk, embedding_id, 
                            chunk_index, total_chunks, metadata)

def get_rag_chunks_by_doc_id(doc_id: str) -> List[Dict[str, Any]]:
    """Get all chunks for a specific document"""
    return db.get_rag_chunks_by_doc_id(doc_id)

def save_rag_search_session(session_id: str, query: str, rag_response: str = None,
                           traditional_results_count: int = 0, rag_results_count: int = 0,
                           processing_time: float = 0.0, confidence_score: float = 0.0,
                           retrieval_method: str = None, model_used: str = None) -> bool:
    """Save a RAG search session to the database"""
    return db.save_rag_search_session(session_id, query, rag_response, traditional_results_count,
                                     rag_results_count, processing_time, confidence_score,
                                     retrieval_method, model_used)

def get_rag_search_sessions(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent RAG search sessions"""
    return db.get_rag_search_sessions(limit)

def get_rag_stats() -> Dict[str, Any]:
    """Get RAG system statistics"""
    return db.get_rag_stats()

def get_lead_stats() -> Dict[str, Any]:
    """Get lead management statistics"""
    return db.get_lead_stats() 