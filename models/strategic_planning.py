"""
Strategic Planning Database Models

This module provides database models for strategic planning including
company profiles, market research, and strategic plan generation.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from utils.logger import get_logger
    logger = get_logger('strategic_planning')
except ImportError:
    logger = None

class StrategicPlanningDB:
    """Database manager for strategic planning system"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "leadfinder.db")
        
        self.db_path = db_path
        self._init_strategic_planning_tables()
    
    def _init_strategic_planning_tables(self):
        """Initialize strategic planning tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Company Profiles Table
            c.execute('''CREATE TABLE IF NOT EXISTS company_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                product_description TEXT,
                target_market TEXT,
                usps TEXT,
                service_portfolio TEXT,
                industry TEXT,
                business_model TEXT,
                revenue_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Market Research Table
            c.execute('''CREATE TABLE IF NOT EXISTS market_research (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                market_size_data TEXT,
                competitive_analysis TEXT,
                industry_trends TEXT,
                customer_insights TEXT,
                market_segments TEXT,
                growth_projections TEXT,
                research_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company_profiles (id)
            )''')
            
            # Strategic Plans Table
            c.execute('''CREATE TABLE IF NOT EXISTS strategic_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                plan_type TEXT NOT NULL, -- 'market_plan', 'business_plan', 'gtm_strategy'
                plan_content TEXT,
                status TEXT DEFAULT 'draft',
                version TEXT DEFAULT '1.0',
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company_profiles (id)
            )''')
            
            # SWOT Analysis Table
            c.execute('''CREATE TABLE IF NOT EXISTS swot_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                strengths TEXT,
                weaknesses TEXT,
                opportunities TEXT,
                threats TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company_profiles (id)
            )''')
            
            # Competitive Analysis Table
            c.execute('''CREATE TABLE IF NOT EXISTS competitive_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                competitor_name TEXT,
                competitor_analysis TEXT,
                market_position TEXT,
                competitive_advantages TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company_profiles (id)
            )''')
            
            # Financial Projections Table
            c.execute('''CREATE TABLE IF NOT EXISTS financial_projections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                revenue_projections TEXT,
                cost_structure TEXT,
                profit_margins TEXT,
                funding_requirements TEXT,
                break_even_analysis TEXT,
                projection_period TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company_profiles (id)
            )''')
            
            conn.commit()
            conn.close()
            
            if logger:
                logger.info("Strategic planning tables initialized")
                
        except Exception as e:
            if logger:
                logger.error(f"Failed to initialize strategic planning tables: {e}")
            raise
    
    def create_company_profile(self, company_data: Dict[str, Any]) -> int:
        """Create a new company profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO company_profiles 
                        (company_name, product_description, target_market, usps, 
                         service_portfolio, industry, business_model, revenue_model) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (company_data.get('company_name'),
                      company_data.get('product_description'),
                      company_data.get('target_market'),
                      company_data.get('usps'),
                      company_data.get('service_portfolio'),
                      company_data.get('industry'),
                      company_data.get('business_model'),
                      company_data.get('revenue_model')))
            
            company_id = c.lastrowid
            conn.commit()
            conn.close()
            
            if logger:
                logger.info(f"Created company profile: {company_data.get('company_name')}")
            
            return company_id
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to create company profile: {e}")
            raise
    
    def get_company_profile(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get company profile by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''SELECT * FROM company_profiles WHERE id = ?''', (company_id,))
            result = c.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in c.description]
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to get company profile {company_id}: {e}")
            return None
    
    def update_company_profile(self, company_id: int, company_data: Dict[str, Any]) -> bool:
        """Update company profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            updates = []
            params = []
            
            for key, value in company_data.items():
                if key in ['company_name', 'product_description', 'target_market', 'usps', 
                          'service_portfolio', 'industry', 'business_model', 'revenue_model']:
                    updates.append(f"{key} = ?")
                    params.append(value)
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(company_id)
                
                query = f"UPDATE company_profiles SET {', '.join(updates)} WHERE id = ?"
                c.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to update company profile {company_id}: {e}")
            return False
    
    def get_all_company_profiles(self) -> List[Dict[str, Any]]:
        """Get all company profiles"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''SELECT * FROM company_profiles ORDER BY created_at DESC''')
            results = c.fetchall()
            conn.close()
            
            if results:
                columns = [description[0] for description in c.description]
                return [dict(zip(columns, row)) for row in results]
            
            return []
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to get company profiles: {e}")
            return []
    
    def save_market_research(self, company_id: int, research_data: Dict[str, Any]) -> int:
        """Save market research data"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO market_research 
                        (company_id, market_size_data, competitive_analysis, 
                         industry_trends, customer_insights, market_segments, growth_projections) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (company_id,
                      json.dumps(research_data.get('market_size_data', {})),
                      json.dumps(research_data.get('competitive_analysis', {})),
                      json.dumps(research_data.get('industry_trends', {})),
                      json.dumps(research_data.get('customer_insights', {})),
                      json.dumps(research_data.get('market_segments', {})),
                      json.dumps(research_data.get('growth_projections', {}))))
            
            research_id = c.lastrowid
            conn.commit()
            conn.close()
            
            if logger:
                logger.info(f"Saved market research for company {company_id}")
            
            return research_id
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to save market research: {e}")
            raise
    
    def get_market_research(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get market research for a company"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''SELECT * FROM market_research 
                        WHERE company_id = ? ORDER BY research_date DESC LIMIT 1''', (company_id,))
            result = c.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in c.description]
                data = dict(zip(columns, result))
                
                # Parse JSON fields
                for field in ['market_size_data', 'competitive_analysis', 'industry_trends', 
                             'customer_insights', 'market_segments', 'growth_projections']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except:
                            data[field] = {}
                
                return data
            
            return None
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to get market research for company {company_id}: {e}")
            return None
    
    def save_swot_analysis(self, company_id: int, swot_data: Dict[str, Any]) -> int:
        """Save SWOT analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO swot_analysis 
                        (company_id, strengths, weaknesses, opportunities, threats) 
                        VALUES (?, ?, ?, ?, ?)''',
                     (company_id,
                      json.dumps(swot_data.get('strengths', [])),
                      json.dumps(swot_data.get('weaknesses', [])),
                      json.dumps(swot_data.get('opportunities', [])),
                      json.dumps(swot_data.get('threats', []))))
            
            swot_id = c.lastrowid
            conn.commit()
            conn.close()
            
            if logger:
                logger.info(f"Saved SWOT analysis for company {company_id}")
            
            return swot_id
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to save SWOT analysis: {e}")
            raise
    
    def get_swot_analysis(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get SWOT analysis for a company"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''SELECT * FROM swot_analysis 
                        WHERE company_id = ? ORDER BY analysis_date DESC LIMIT 1''', (company_id,))
            result = c.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in c.description]
                data = dict(zip(columns, result))
                
                # Parse JSON fields
                for field in ['strengths', 'weaknesses', 'opportunities', 'threats']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except:
                            data[field] = []
                
                return data
            
            return None
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to get SWOT analysis for company {company_id}: {e}")
            return None
    
    def save_strategic_plan(self, company_id: int, plan_type: str, plan_content: str) -> int:
        """Save strategic plan"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO strategic_plans 
                        (company_id, plan_type, plan_content) 
                        VALUES (?, ?, ?)''',
                     (company_id, plan_type, plan_content))
            
            plan_id = c.lastrowid
            conn.commit()
            conn.close()
            
            if logger:
                logger.info(f"Saved {plan_type} for company {company_id}")
            
            return plan_id
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to save strategic plan: {e}")
            raise
    
    def get_strategic_plans(self, company_id: int, plan_type: str = None) -> List[Dict[str, Any]]:
        """Get strategic plans for a company"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if plan_type:
                c.execute('''SELECT * FROM strategic_plans 
                            WHERE company_id = ? AND plan_type = ? 
                            ORDER BY generated_at DESC''', (company_id, plan_type))
            else:
                c.execute('''SELECT * FROM strategic_plans 
                            WHERE company_id = ? ORDER BY generated_at DESC''', (company_id,))
            
            results = c.fetchall()
            conn.close()
            
            if results:
                columns = [description[0] for description in c.description]
                return [dict(zip(columns, row)) for row in results]
            
            return []
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to get strategic plans for company {company_id}: {e}")
            return []
    
    def save_financial_projections(self, company_id: int, financial_data: Dict[str, Any]) -> int:
        """Save financial projections"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO financial_projections 
                        (company_id, revenue_projections, cost_structure, profit_margins, 
                         funding_requirements, break_even_analysis, projection_period) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (company_id,
                      json.dumps(financial_data.get('revenue_projections', {})),
                      json.dumps(financial_data.get('cost_structure', {})),
                      json.dumps(financial_data.get('profit_margins', {})),
                      json.dumps(financial_data.get('funding_requirements', {})),
                      json.dumps(financial_data.get('break_even_analysis', {})),
                      financial_data.get('projection_period', '3 years')))
            
            projection_id = c.lastrowid
            conn.commit()
            conn.close()
            
            if logger:
                logger.info(f"Saved financial projections for company {company_id}")
            
            return projection_id
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to save financial projections: {e}")
            raise
    
    def get_financial_projections(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get financial projections for a company"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''SELECT * FROM financial_projections 
                        WHERE company_id = ? ORDER BY created_at DESC LIMIT 1''', (company_id,))
            result = c.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in c.description]
                data = dict(zip(columns, result))
                
                # Parse JSON fields
                for field in ['revenue_projections', 'cost_structure', 'profit_margins', 
                             'funding_requirements', 'break_even_analysis']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except:
                            data[field] = {}
                
                return data
            
            return None
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to get financial projections for company {company_id}: {e}")
            return None

# Global strategic planning database instance
_strategic_db = None

def get_strategic_db() -> StrategicPlanningDB:
    """Get the global strategic planning database instance"""
    global _strategic_db
    if _strategic_db is None:
        _strategic_db = StrategicPlanningDB()
    return _strategic_db