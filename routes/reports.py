from flask import Blueprint, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List
import io
import csv

# Import services with error handling
try:
    from models.database import db, get_lead_stats, get_rag_stats
except ImportError:
    db = None
    get_lead_stats = None
    get_rag_stats = None

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('reports')
except ImportError:
    logger = None

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
def reports_home():
    """Reports dashboard"""
    return render_template('reports_home.html')

@reports_bp.route('/market-analysis')
def market_analysis_report():
    """Generate market analysis report"""
    if not db:
        return "Database not available", 500
    
    # Get report parameters
    period = request.args.get('period', '30')  # days
    report_type = request.args.get('type', 'comprehensive')
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(period))
    
    # Get lead statistics
    lead_stats = get_lead_stats() if get_lead_stats else {}
    rag_stats = get_rag_stats() if get_rag_stats else {}
    
    # Get recent leads for analysis
    recent_leads = db.get_all_leads(limit=100) if db else []
    
    # Calculate market trends
    trends = calculate_market_trends(recent_leads)
    
    # Generate AI insights
    ai_insights = generate_ai_insights(recent_leads, trends)
    
    # Prepare report data
    report_data = {
        'report_date': end_date.strftime('%Y-%m-%d'),
        'report_period': f'Last {period} Days',
        'model_used': 'Mistral-7B',
        'total_leads': lead_stats.get('total_leads', 0),
        'conversion_rate': calculate_conversion_rate(lead_stats),
        'ai_insights': rag_stats.get('total_sessions', 0),
        'high_quality': lead_stats.get('ai_analyses', 0),
        'trends': trends,
        'ai_insights': ai_insights,
        'recommendations': generate_recommendations(trends, ai_insights)
    }
    
    return render_template('market_report.html', **report_data)

@reports_bp.route('/lead-analysis')
def lead_analysis_report():
    """Generate lead analysis report"""
    if not db:
        return "Database not available", 500
    
    # Get all leads
    leads = db.get_all_leads()
    
    # Analyze leads by source
    source_analysis = analyze_leads_by_source(leads)
    
    # Analyze lead quality
    quality_analysis = analyze_lead_quality(leads)
    
    # Get recent activity
    recent_activity = get_recent_activity(leads)
    
    report_data = {
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'report_period': 'All Time',
        'total_leads': len(leads),
        'source_analysis': source_analysis,
        'quality_analysis': quality_analysis,
        'recent_activity': recent_activity,
        'top_leads': get_top_leads(leads, 10)
    }
    
    return render_template('lead_analysis_report.html', **report_data)

@reports_bp.route('/executive-summary')
def executive_summary_report():
    """Generate executive summary report"""
    if not db:
        return "Database not available", 500
    
    # Get comprehensive statistics
    lead_stats = get_lead_stats() if get_lead_stats else {}
    rag_stats = get_rag_stats() if get_rag_stats else {}
    
    # Calculate KPIs
    kpis = calculate_kpis(lead_stats, rag_stats)
    
    # Get recent activity
    recent_leads = db.get_all_leads(limit=20) if db else []
    search_history = db.get_search_history(10) if db else []
    
    report_data = {
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'report_period': 'Current Period',
        'kpis': kpis,
        'recent_leads': recent_leads,
        'search_history': search_history,
        'system_status': get_system_status()
    }
    
    return render_template('executive_summary_report.html', **report_data)

@reports_bp.route('/export/<report_type>')
def export_report(report_type: str):
    """Export report as CSV/Excel"""
    if not db:
        return "Database not available", 500
    
    format_type = request.args.get('format', 'csv')
    
    if report_type == 'leads':
        return export_leads_report(format_type)
    elif report_type == 'activity':
        return export_activity_report(format_type)
    elif report_type == 'analysis':
        return export_analysis_report(format_type)
    else:
        return "Invalid report type", 400

@reports_bp.route('/api/stats')
def get_report_stats():
    """API endpoint for report statistics"""
    if not db:
        return jsonify({"error": "Database not available"}), 500
    
    lead_stats = get_lead_stats() if get_lead_stats else {}
    rag_stats = get_rag_stats() if get_rag_stats else {}
    
    return jsonify({
        'lead_stats': lead_stats,
        'rag_stats': rag_stats,
        'generated_at': datetime.now().isoformat()
    })

# Helper functions
def calculate_market_trends(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate market trends from leads data"""
    trends = {
        'emerging_sectors': [],
        'declining_sectors': [],
        'top_sources': {},
        'quality_distribution': {}
    }
    
    if not leads:
        return trends
    
    # Analyze by source
    sources = {}
    for lead in leads:
        source = lead.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    trends['top_sources'] = dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5])
    
    # Analyze quality distribution
    quality_counts = {'high': 0, 'medium': 0, 'low': 0}
    for lead in leads:
        if lead.get('ai_summary'):
            quality_counts['high'] += 1
        elif lead.get('description'):
            quality_counts['medium'] += 1
        else:
            quality_counts['low'] += 1
    
    trends['quality_distribution'] = quality_counts
    
    return trends

def generate_ai_insights(leads: List[Dict[str, Any]], trends: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate AI-powered insights"""
    insights = []
    
    if not leads:
        return insights
    
    # Analyze top sources
    top_source = max(trends.get('top_sources', {}).items(), key=lambda x: x[1], default=('unknown', 0))
    insights.append({
        'type': 'source_analysis',
        'title': 'Top Lead Source',
        'content': f"{top_source[0].title()} generates {top_source[1]} leads ({top_source[1]/len(leads)*100:.1f}% of total)",
        'recommendation': f'Focus marketing efforts on {top_source[0].title()} to maximize lead generation'
    })
    
    # Analyze quality
    quality_dist = trends.get('quality_distribution', {})
    high_quality_pct = quality_dist.get('high', 0) / len(leads) * 100 if leads else 0
    
    insights.append({
        'type': 'quality_analysis',
        'title': 'Lead Quality',
        'content': f"{high_quality_pct:.1f}% of leads are high quality (have AI analysis)",
        'recommendation': 'Continue AI analysis to improve lead quality and conversion rates'
    })
    
    return insights

def generate_recommendations(trends: Dict[str, Any], insights: List[Dict[str, Any]]) -> List[str]:
    """Generate strategic recommendations"""
    recommendations = []
    
    # Based on source analysis
    top_sources = trends.get('top_sources', {})
    if top_sources:
        top_source = max(top_sources.items(), key=lambda x: x[1])
        recommendations.append(f"Focus on {top_source[0].title()} as it generates {top_source[1]} leads")
    
    # Based on quality analysis
    quality_dist = trends.get('quality_distribution', {})
    if quality_dist.get('high', 0) < quality_dist.get('low', 0):
        recommendations.append("Increase AI analysis to improve lead quality")
    
    # General recommendations
    recommendations.append("Implement lead scoring to prioritize high-value prospects")
    recommendations.append("Set up automated follow-up sequences for new leads")
    
    return recommendations

def analyze_leads_by_source(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze leads by source"""
    source_analysis = {}
    
    for lead in leads:
        source = lead.get('source', 'unknown')
        if source not in source_analysis:
            source_analysis[source] = {
                'count': 0,
                'with_ai': 0,
                'with_description': 0
            }
        
        source_analysis[source]['count'] += 1
        if lead.get('ai_summary'):
            source_analysis[source]['with_ai'] += 1
        if lead.get('description'):
            source_analysis[source]['with_description'] += 1
    
    return source_analysis

def analyze_lead_quality(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze lead quality"""
    quality_analysis = {
        'high': {'count': 0, 'percentage': 0},
        'medium': {'count': 0, 'percentage': 0},
        'low': {'count': 0, 'percentage': 0}
    }
    
    total_leads = len(leads)
    if total_leads == 0:
        return quality_analysis
    
    for lead in leads:
        if lead.get('ai_summary'):
            quality_analysis['high']['count'] += 1
        elif lead.get('description'):
            quality_analysis['medium']['count'] += 1
        else:
            quality_analysis['low']['count'] += 1
    
    # Calculate percentages
    for quality in quality_analysis:
        quality_analysis[quality]['percentage'] = (quality_analysis[quality]['count'] / total_leads) * 100
    
    return quality_analysis

def get_recent_activity(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get recent lead activity"""
    # Sort leads by creation date (most recent first)
    sorted_leads = sorted(leads, key=lambda x: x.get('created_at', ''), reverse=True)
    
    recent_activity = []
    for lead in sorted_leads[:10]:  # Last 10 leads
        recent_activity.append({
            'type': 'lead',
            'title': lead.get('title', 'Unknown'),
            'source': lead.get('source', 'unknown'),
            'created_at': lead.get('created_at', ''),
            'has_ai': bool(lead.get('ai_summary'))
        })
    
    return recent_activity

def get_top_leads(leads: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """Get top leads by quality"""
    # Sort by AI analysis presence and creation date
    sorted_leads = sorted(leads, 
                         key=lambda x: (bool(x.get('ai_summary')), x.get('created_at', '')), 
                         reverse=True)
    
    return sorted_leads[:limit]

def calculate_kpis(lead_stats: Dict[str, Any], rag_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate key performance indicators"""
    kpis = {
        'total_leads': lead_stats.get('total_leads', 0),
        'total_searches': lead_stats.get('total_searches', 0),
        'ai_analyses': lead_stats.get('ai_analyses', 0),
        'rag_queries': rag_stats.get('total_sessions', 0),
        'conversion_rate': 0,
        'avg_response_time': 0,
        'system_uptime': 99.9
    }
    
    # Calculate conversion rate (leads with AI analysis / total leads)
    if kpis['total_leads'] > 0:
        kpis['conversion_rate'] = (kpis['ai_analyses'] / kpis['total_leads']) * 100
    
    # Calculate average response time from RAG stats
    if rag_stats.get('avg_processing_time'):
        kpis['avg_response_time'] = rag_stats['avg_processing_time']
    
    return kpis

def get_system_status() -> Dict[str, Any]:
    """Get system status information"""
    status = {
        'ollama': {'status': 'unknown', 'message': 'Service not available'},
        'database': {'status': 'unknown', 'message': 'Database not available'},
        'rag_system': {'status': 'unknown', 'message': 'RAG system not available'}
    }
    
    # Check Ollama status
    if ollama_service:
        try:
            ollama_status = ollama_service.check_status()
            status['ollama'] = {
                'status': 'online' if ollama_status.get('ok') else 'offline',
                'message': ollama_status.get('msg', 'Unknown status')
            }
        except Exception as e:
            status['ollama'] = {'status': 'error', 'message': str(e)}
    
    # Check database status
    if db:
        try:
            # Try to get lead count as a simple test
            lead_count = db.get_lead_count()
            status['database'] = {
                'status': 'online',
                'message': f'Connected - {lead_count} leads'
            }
        except Exception as e:
            status['database'] = {'status': 'error', 'message': str(e)}
    
    # Check RAG system status
    if get_rag_stats:
        try:
            rag_stats = get_rag_stats()
            status['rag_system'] = {
                'status': 'online',
                'message': f'Active - {rag_stats.get("total_sessions", 0)} sessions'
            }
        except Exception as e:
            status['rag_system'] = {'status': 'error', 'message': str(e)}
    
    return status

def calculate_conversion_rate(lead_stats: Dict[str, Any]) -> float:
    """Calculate conversion rate"""
    total_leads = lead_stats.get('total_leads', 0)
    ai_analyses = lead_stats.get('ai_analyses', 0)
    
    if total_leads > 0:
        return (ai_analyses / total_leads) * 100
    return 0.0

def export_leads_report(format_type: str):
    """Export leads report"""
    if not db:
        return "Database not available", 500
    
    leads = db.get_all_leads()
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Title', 'Description', 'Link', 'AI Summary', 'Source', 'Created At'])
        
        # Write data
        for lead in leads:
            writer.writerow([
                lead.get('id', ''),
                lead.get('title', ''),
                lead.get('description', ''),
                lead.get('link', ''),
                lead.get('ai_summary', ''),
                lead.get('source', ''),
                lead.get('created_at', '')
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'leads_report_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    return "Unsupported format", 400

def export_activity_report(format_type: str):
    """Export activity report"""
    if not db:
        return "Database not available", 500
    
    search_history = db.get_search_history()
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Query', 'Research Question', 'Engines', 'Results Count', 'Created At'])
        
        # Write data
        for search in search_history:
            writer.writerow([
                search.get('id', ''),
                search.get('query', ''),
                search.get('research_question', ''),
                search.get('engines', ''),
                search.get('results_count', ''),
                search.get('created_at', '')
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'activity_report_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    return "Unsupported format", 400

def export_analysis_report(format_type: str):
    """Export analysis report"""
    if not db:
        return "Database not available", 500
    
    # Get comprehensive analysis data
    lead_stats = get_lead_stats() if get_lead_stats else {}
    rag_stats = get_rag_stats() if get_rag_stats else {}
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Value', 'Description'])
        
        # Write data
        analysis_data = [
            ['Total Leads', lead_stats.get('total_leads', 0), 'Total number of leads in database'],
            ['Total Searches', lead_stats.get('total_searches', 0), 'Total number of searches performed'],
            ['AI Analyses', lead_stats.get('ai_analyses', 0), 'Number of leads with AI analysis'],
            ['RAG Sessions', rag_stats.get('total_sessions', 0), 'Total RAG search sessions'],
            ['Conversion Rate', f"{calculate_conversion_rate(lead_stats):.1f}%", 'Percentage of leads with AI analysis'],
            ['Avg Processing Time', f"{rag_stats.get('avg_processing_time', 0):.3f}s", 'Average RAG processing time'],
            ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Report generation timestamp']
        ]
        
        for row in analysis_data:
            writer.writerow(row)
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'analysis_report_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    return "Unsupported format", 400 