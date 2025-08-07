"""
Database Indexing System for LeadFinder

This module provides comprehensive database indexing to improve query performance:
- Automatic index creation and management
- Performance monitoring and optimization
- Index health checks and maintenance
- Query optimization recommendations
"""

import sqlite3
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    from utils.logger import get_logger
    logger = get_logger('database_indexes')
except ImportError:
    logger = None

try:
    from models.database_pool import get_db_pool
except ImportError:
    get_db_pool = None

@dataclass
class IndexInfo:
    """Information about a database index"""
    name: str
    table: str
    columns: List[str]
    unique: bool
    created_at: float
    last_used: Optional[float] = None
    usage_count: int = 0

@dataclass
class QueryPerformance:
    """Query performance metrics"""
    query: str
    execution_time: float
    rows_returned: int
    index_used: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class DatabaseIndexManager:
    """
    Comprehensive database indexing system
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.pool = get_db_pool() if get_db_pool else None
        self.indexes = {}
        self.query_performance = []
        self._load_existing_indexes()
    
    def _load_existing_indexes(self):
        """Load existing indexes from database"""
        try:
            if self.pool:
                with self.pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT name, tbl_name, sql 
                        FROM sqlite_master 
                        WHERE type='index' AND name NOT LIKE 'sqlite_%'
                    """)
                    indexes = cursor.fetchall()
                    
                    for name, table, sql in indexes:
                        # Parse index information
                        columns = self._parse_index_columns(sql)
                        unique = 'UNIQUE' in sql.upper()
                        
                        self.indexes[name] = IndexInfo(
                            name=name,
                            table=table,
                            columns=columns,
                            unique=unique,
                            created_at=time.time()
                        )
                        
            if logger:
                logger.info(f"Loaded {len(self.indexes)} existing indexes")
                
        except Exception as e:
            if logger:
                logger.error(f"Error loading existing indexes: {e}")
    
    def _parse_index_columns(self, sql: str) -> List[str]:
        """Parse column names from index SQL"""
        try:
            # Extract column names from index SQL
            start = sql.find('(')
            end = sql.rfind(')')
            if start != -1 and end != -1:
                columns_str = sql[start+1:end]
                return [col.strip() for col in columns_str.split(',')]
            return []
        except Exception:
            return []
    
    def create_index(self, table: str, columns: List[str], 
                    unique: bool = False, name: str = None) -> bool:
        """
        Create a new index
        
        Args:
            table: Table name
            columns: List of column names
            unique: Whether index should be unique
            name: Custom index name (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not name:
                name = f"idx_{table}_{'_'.join(columns)}"
            
            columns_str = ', '.join(columns)
            unique_str = 'UNIQUE' if unique else ''
            
            sql = f"CREATE {unique_str} INDEX IF NOT EXISTS {name} ON {table} ({columns_str})"
            
            if self.pool:
                with self.pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit()
                    
                    # Add to local tracking
                    self.indexes[name] = IndexInfo(
                        name=name,
                        table=table,
                        columns=columns,
                        unique=unique,
                        created_at=time.time()
                    )
                    
                    if logger:
                        logger.info(f"Created index {name} on {table}({columns_str})")
                    return True
            else:
                # Fallback to direct connection
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit()
                    return True
                    
        except Exception as e:
            if logger:
                logger.error(f"Error creating index {name}: {e}")
            return False
    
    def drop_index(self, name: str) -> bool:
        """
        Drop an index
        
        Args:
            name: Index name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sql = f"DROP INDEX IF EXISTS {name}"
            
            if self.pool:
                with self.pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit()
                    
                    # Remove from local tracking
                    if name in self.indexes:
                        del self.indexes[name]
                    
                    if logger:
                        logger.info(f"Dropped index {name}")
                    return True
            else:
                # Fallback to direct connection
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    conn.commit()
                    return True
                    
        except Exception as e:
            if logger:
                logger.error(f"Error dropping index {name}: {e}")
            return False
    
    def get_indexes_for_table(self, table: str) -> List[IndexInfo]:
        """
        Get all indexes for a table
        
        Args:
            table: Table name
            
        Returns:
            List of index information
        """
        return [idx for idx in self.indexes.values() if idx.table == table]
    
    def get_index_usage_stats(self) -> Dict[str, Any]:
        """
        Get index usage statistics
        
        Returns:
            Dictionary with index usage information
        """
        try:
            if self.pool:
                with self.pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA index_list")
                    indexes = cursor.fetchall()
                    
                    usage_stats = {}
                    for index in indexes:
                        index_name = index[1]
                        cursor.execute(f"PRAGMA index_info({index_name})")
                        info = cursor.fetchall()
                        
                        usage_stats[index_name] = {
                            'columns': [row[2] for row in info],
                            'table': index[2],
                            'unique': bool(index[3])
                        }
                    
                    return usage_stats
            else:
                # Fallback to direct connection
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA index_list")
                    indexes = cursor.fetchall()
                    
                    usage_stats = {}
                    for index in indexes:
                        index_name = index[1]
                        cursor.execute(f"PRAGMA index_info({index_name})")
                        info = cursor.fetchall()
                        
                        usage_stats[index_name] = {
                            'columns': [row[2] for row in info],
                            'table': index[2],
                            'unique': bool(index[3])
                        }
                    
                    return usage_stats
                    
        except Exception as e:
            if logger:
                logger.error(f"Error getting index usage stats: {e}")
            return {}
    
    def analyze_query_performance(self, query: str, execution_time: float, 
                                rows_returned: int, index_used: str = None):
        """
        Record query performance metrics
        
        Args:
            query: SQL query
            execution_time: Query execution time
            rows_returned: Number of rows returned
            index_used: Index used (if any)
        """
        performance = QueryPerformance(
            query=query,
            execution_time=execution_time,
            rows_returned=rows_returned,
            index_used=index_used
        )
        
        self.query_performance.append(performance)
        
        # Keep only last 1000 performance records
        if len(self.query_performance) > 1000:
            self.query_performance = self.query_performance[-1000:]
    
    def get_slow_queries(self, threshold: float = 1.0) -> List[QueryPerformance]:
        """
        Get queries that exceed performance threshold
        
        Args:
            threshold: Execution time threshold in seconds
            
        Returns:
            List of slow queries
        """
        return [qp for qp in self.query_performance if qp.execution_time > threshold]
    
    def recommend_indexes(self) -> List[Dict[str, Any]]:
        """
        Recommend indexes based on query performance
        
        Returns:
            List of index recommendations
        """
        recommendations = []
        
        # Analyze slow queries
        slow_queries = self.get_slow_queries(0.5)
        
        for query_perf in slow_queries:
            # Simple heuristic for index recommendations
            query = query_perf.query.upper()
            
            # Check for WHERE clauses
            if 'WHERE' in query:
                # Extract potential column names from WHERE clause
                where_start = query.find('WHERE')
                where_end = query.find('ORDER BY') if 'ORDER BY' in query else len(query)
                where_clause = query[where_start:where_end]
                
                # Look for common patterns
                if 'LEADS.' in where_clause:
                    recommendations.append({
                        'table': 'leads',
                        'columns': ['source', 'created_at'],
                        'reason': f'Slow query: {query_perf.query[:100]}...',
                        'estimated_improvement': 'High'
                    })
                
                if 'WORKSHOP_ANALYSIS.' in where_clause:
                    recommendations.append({
                        'table': 'workshop_analysis',
                        'columns': ['project_id', 'relevancy_score'],
                        'reason': f'Slow query: {query_perf.query[:100]}...',
                        'estimated_improvement': 'High'
                    })
                
                if 'RAG_CHUNKS.' in where_clause:
                    recommendations.append({
                        'table': 'rag_chunks',
                        'columns': ['doc_id', 'source'],
                        'reason': f'Slow query: {query_perf.query[:100]}...',
                        'estimated_improvement': 'Medium'
                    })
        
        return recommendations
    
    def optimize_database(self) -> Dict[str, Any]:
        """
        Perform database optimization
        
        Returns:
            Dictionary with optimization results
        """
        results = {
            'indexes_created': 0,
            'indexes_dropped': 0,
            'recommendations_applied': 0,
            'performance_improvement': 0.0
        }
        
        try:
            # Get recommendations
            recommendations = self.recommend_indexes()
            
            # Apply recommendations
            for rec in recommendations:
                table = rec['table']
                columns = rec['columns']
                
                # Check if index already exists
                existing_indexes = self.get_indexes_for_table(table)
                index_exists = any(
                    set(idx.columns) == set(columns) for idx in existing_indexes
                )
                
                if not index_exists:
                    if self.create_index(table, columns):
                        results['indexes_created'] += 1
                        results['recommendations_applied'] += 1
            
            # Analyze performance improvement
            if self.query_performance:
                recent_queries = self.query_performance[-100:]
                avg_time = sum(qp.execution_time for qp in recent_queries) / len(recent_queries)
                results['performance_improvement'] = avg_time
            
            if logger:
                logger.info(f"Database optimization completed: {results}")
            
            return results
            
        except Exception as e:
            if logger:
                logger.error(f"Error during database optimization: {e}")
            return results
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report
        
        Returns:
            Dictionary with performance information
        """
        return {
            'total_indexes': len(self.indexes),
            'indexes_by_table': {
                table: len(self.get_indexes_for_table(table))
                for table in set(idx.table for idx in self.indexes.values())
            },
            'slow_queries_count': len(self.get_slow_queries()),
            'avg_query_time': (
                sum(qp.execution_time for qp in self.query_performance) / 
                len(self.query_performance) if self.query_performance else 0
            ),
            'recommendations': self.recommend_indexes(),
            'index_usage': self.get_index_usage_stats()
        }

# Global index manager instance
_index_manager = None

def get_index_manager(db_path: str = None) -> DatabaseIndexManager:
    """Get global database index manager instance"""
    global _index_manager
    
    if _index_manager is None:
        _index_manager = DatabaseIndexManager(db_path)
    
    return _index_manager

def create_standard_indexes():
    """Create standard indexes for optimal performance"""
    manager = get_index_manager()
    
    # Standard indexes for common queries
    standard_indexes = [
        # Leads table
        ('leads', ['source', 'created_at']),
        ('leads', ['title']),
        ('leads', ['created_at']),
        
        # Workshop analysis table
        ('workshop_analysis', ['project_id', 'relevancy_score']),
        ('workshop_analysis', ['lead_id']),
        ('workshop_analysis', ['created_at']),
        
        # RAG chunks table
        ('rag_chunks', ['doc_id']),
        ('rag_chunks', ['source']),
        ('rag_chunks', ['chunk_id']),
        
        # Search history table
        ('search_history', ['created_at']),
        ('search_history', ['query']),
        
        # Researchers table
        ('researchers', ['orcid_id']),
        ('researchers', ['name']),
        ('researchers', ['institution']),
        
        # Researcher publications table
        ('researcher_publications', ['researcher_id']),
        ('researcher_publications', ['publication_id']),
        ('researcher_publications', ['year'])
    ]
    
    created_count = 0
    for table, columns in standard_indexes:
        if manager.create_index(table, columns):
            created_count += 1
    
    if logger:
        logger.info(f"Created {created_count} standard indexes")
    
    return created_count

def optimize_database_performance():
    """Optimize database performance"""
    manager = get_index_manager()
    return manager.optimize_database()

def get_database_performance_report():
    """Get database performance report"""
    manager = get_index_manager()
    return manager.get_performance_report() 