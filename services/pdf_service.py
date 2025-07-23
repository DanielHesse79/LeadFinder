"""
PDF Export Service for LeadFinder

This module provides PDF generation functionality for Lead Workshop projects
with clickable links and AI-generated descriptions.
"""

import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

try:
    from utils.logger import get_logger
    logger = get_logger('pdf_service')
except ImportError:
    logger = None

class PDFService:
    def __init__(self, export_folder: str = "exports"):
        self.export_folder = export_folder
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self._ensure_export_folder()
    
    def _setup_styles(self):
        """Setup custom styles for the PDF"""
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        ))
        
        # Custom heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#34495e')
        ))
        
        # Custom body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Link style
        self.styles.add(ParagraphStyle(
            name='LinkStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=HexColor('#3498db'),
            underline=True
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=HexColor('#e74c3c'),
            alignment=TA_CENTER
        ))
    
    def _ensure_export_folder(self):
        """Ensure export folder exists"""
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
            if logger:
                logger.info(f"Created export folder: {self.export_folder}")
    
    def generate_project_report(self, project: Dict[str, Any], analyses: List[Dict[str, Any]]) -> str:
        """
        Generate a PDF report for a Lead Workshop project
        
        Args:
            project: Project information
            analyses: List of lead analyses
            
        Returns:
            Path to generated PDF file
        """
        if not analyses:
            raise ValueError("No analyses provided for report generation")
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_project_name = "".join(c for c in project['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"leadfinder_report_{safe_project_name}_{timestamp}.pdf"
        filepath = os.path.join(self.export_folder, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        
        # Add title page
        story.extend(self._create_title_page(project))
        story.append(PageBreak())
        
        # Add introduction section
        story.extend(self._create_introduction_section(project, analyses))
        story.append(PageBreak())
        
        # Add project overview
        story.extend(self._create_project_overview(project, analyses))
        story.append(PageBreak())
        
        # Add lead analyses
        story.extend(self._create_lead_analyses(analyses))
        
        # Add company footer with beta version info
        story.extend(self._create_company_footer("4Front 2 Market AB", "This is a beta-version. Data might be unreliable."))
        
        # Build PDF
        doc.build(story)
        
        if logger:
            logger.info(f"Generated PDF report: {filepath}")
        
        return filepath
    
    def generate_custom_project_report(self, project: Dict[str, Any], analyses: List[Dict[str, Any]], 
                                      custom_content: Dict[str, Any], company_name: str = "4Front 2 Market AB",
                                      disclaimer: str = "This is a beta-version. Data might be unreliable.") -> str:
        """
        Generate a custom PDF report with company branding and user-editable content
        
        Args:
            project: Project information
            analyses: List of lead analyses
            custom_content: User-edited content
            company_name: Company name for branding
            disclaimer: Disclaimer text
            
        Returns:
            Path to generated PDF file
        """
        if not analyses:
            raise ValueError("No analyses provided for report generation")
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_project_name = "".join(c for c in project['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{company_name.replace(' ', '_')}_report_{safe_project_name}_{timestamp}.pdf"
        filepath = os.path.join(self.export_folder, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        
        # Add custom title page with company branding
        story.extend(self._create_custom_title_page(project, company_name, disclaimer))
        story.append(PageBreak())
        
        # Add custom introduction section
        story.extend(self._create_custom_introduction_section(project, analyses, custom_content, company_name))
        story.append(PageBreak())
        
        # Add project overview
        story.extend(self._create_project_overview(project, analyses))
        story.append(PageBreak())
        
        # Add lead analyses
        story.extend(self._create_lead_analyses(analyses))
        
        # Add company footer
        story.extend(self._create_company_footer(company_name, disclaimer))
        
        # Build PDF
        doc.build(story)
        
        if logger:
            logger.info(f"Generated custom PDF report: {filepath}")
        
        return filepath
    
    def _create_title_page(self, project: Dict[str, Any]) -> List:
        """Create title page content with beta version info"""
        story = []
        
        # Try to add company logo
        logo_path = "static/images/4front2market_logo.png"
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 20))
            except Exception as e:
                if logger:
                    logger.warning(f"Could not add logo: {e}")
        
        # Company branding
        company_title = Paragraph("4Front 2 Market AB", self.styles['CustomTitle'])
        story.append(company_title)
        story.append(Spacer(1, 15))
        
        # Beta version notice
        beta_notice = Paragraph("Beta Version Report", self.styles['CustomHeading'])
        story.append(beta_notice)
        story.append(Spacer(1, 15))
        
        # Title
        title = Paragraph(f"LeadFinder Project Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 30))
        
        # Project name
        project_title = Paragraph(f"Project: {project['name']}", self.styles['CustomHeading'])
        story.append(project_title)
        story.append(Spacer(1, 20))
        
        # Project description
        if project.get('description'):
            desc = Paragraph(f"Description: {project['description']}", self.styles['CustomBody'])
            story.append(desc)
            story.append(Spacer(1, 20))
        
        # Generated date
        date_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        date_para = Paragraph(date_text, self.styles['CustomBody'])
        story.append(date_para)
        story.append(Spacer(1, 20))
        
        # Contact information
        contact_info = f"Contact: daniel.hesse@4front2market.se"
        contact_para = Paragraph(contact_info, self.styles['CustomBody'])
        story.append(contact_para)
        story.append(Spacer(1, 30))
        
        # Beta disclaimer
        beta_disclaimer = f"<b>BETA VERSION DISCLAIMER:</b><br/><i>This is a beta-version. Data might be unreliable.</i>"
        disclaimer_para = Paragraph(beta_disclaimer, self.styles['CustomBody'])
        story.append(disclaimer_para)
        story.append(Spacer(1, 30))
        
        # Summary stats
        story.extend(self._create_summary_stats(project))
        
        return story
    
    def _create_introduction_section(self, project: Dict[str, Any], analyses: List[Dict[str, Any]]) -> List:
        """Create professional introduction section"""
        story = []
        
        # Introduction Title
        intro_title = Paragraph("Executive Summary & Introduction", self.styles['CustomHeading'])
        story.append(intro_title)
        story.append(Spacer(1, 20))
        
        # Report Title
        report_title = f"Market Report: AI-Powered Lead Discovery for {project['name']}"
        title_para = Paragraph(f"<b>{report_title}</b>", self.styles['CustomBody'])
        story.append(title_para)
        story.append(Spacer(1, 15))
        
        # Background and Purpose
        background_text = """
        <b>Background and Purpose:</b><br/>
        This report presents the results of an AI-powered lead discovery analysis conducted using LeadFinder's advanced semantic analysis capabilities. 
        The analysis leverages machine learning algorithms to identify and evaluate potential business opportunities, research collaborations, and market intelligence from diverse data sources including academic publications, industry reports, and web content.
        """
        background_para = Paragraph(background_text, self.styles['CustomBody'])
        story.append(background_para)
        story.append(Spacer(1, 15))
        
        # Scope of the Report
        scope_text = f"""
        <b>Scope of the Report:</b><br/>
        • <b>Data Sources:</b> Academic publications, industry reports, web content, and research databases<br/>
        • <b>Methodology:</b> AI-based semantic analysis using advanced language models for relevance scoring and content extraction<br/>
        • <b>Time Frame:</b> Analysis conducted on {datetime.now().strftime('%B %d, %Y')}<br/>
        • <b>Sample Size:</b> {len(analyses)} leads analyzed with comprehensive evaluation
        """
        scope_para = Paragraph(scope_text, self.styles['CustomBody'])
        story.append(scope_para)
        story.append(Spacer(1, 15))
        
        # Key Objectives
        objectives_text = """
        <b>Key Objectives:</b><br/>
        • Identify high-potential leads and business opportunities relevant to the project scope<br/>
        • Benchmark market activity and identify emerging trends in the target domain<br/>
        • Extract actionable intelligence including contact information, product details, and collaboration opportunities<br/>
        • Provide evidence-based recommendations for strategic decision-making<br/>
        • Establish a foundation for ongoing market monitoring and lead generation
        """
        objectives_para = Paragraph(objectives_text, self.styles['CustomBody'])
        story.append(objectives_para)
        story.append(Spacer(1, 15))
        
        # What to Expect
        expect_text = """
        <b>What to Expect from This Report:</b><br/>
        This report contains detailed lead analyses including relevance scores (1-5 scale), direct links to source materials, 
        AI-generated summaries, and extracted contact information. Each lead has been evaluated for business potential, 
        technological relevance, and collaboration opportunities. Future versions may include deeper competitive analysis, 
        trend forecasting, and automated follow-up recommendations.
        """
        expect_para = Paragraph(expect_text, self.styles['CustomBody'])
        story.append(expect_para)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_summary_stats(self, project: Dict[str, Any]) -> List:
        """Create summary statistics"""
        story = []
        
        # This will be populated with actual stats when we have the analyses
        # For now, create a placeholder
        stats_data = [
            ['Metric', 'Value'],
            ['Total Leads', 'To be calculated'],
            ['Average Score', 'To be calculated'],
            ['High Priority (4-5)', 'To be calculated'],
            ['Medium Priority (2-3)', 'To be calculated'],
            ['Low Priority (1)', 'To be calculated']
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Add report metadata
        metadata_text = f"""
        <b>Report Metadata:</b><br/>
        • <b>Generated by:</b> 4Front 2 Market AB - LeadFinder AI Platform<br/>
        • <b>Analysis Engine:</b> Advanced Language Model (Mistral)<br/>
        • <b>Report Type:</b> Comprehensive Lead Analysis<br/>
        • <b>Software Version:</b> Beta Version<br/>
        • <b>Data Processing:</b> AI-powered semantic analysis with 30-minute per-lead evaluation<br/>
        • <b>Quality Assurance:</b> Automated relevance scoring with manual review capabilities<br/>
        • <b>Contact:</b> daniel.hesse@4front2market.se
        """
        metadata_para = Paragraph(metadata_text, self.styles['CustomBody'])
        story.append(metadata_para)
        
        return story
    
    def _create_project_overview(self, project: Dict[str, Any], analyses: List[Dict[str, Any]]) -> List:
        """Create project overview section"""
        story = []
        
        # Section title
        title = Paragraph("Project Overview", self.styles['CustomHeading'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Project details
        project_info = f"""
        <b>Project Name:</b> {project['name']}<br/>
        <b>Created:</b> {project.get('created_at', 'Unknown')}<br/>
        <b>Total Leads Analyzed:</b> {len(analyses)}<br/>
        """
        
        if project.get('description'):
            project_info += f"<b>Description:</b> {project['description']}<br/>"
        
        project_para = Paragraph(project_info, self.styles['CustomBody'])
        story.append(project_para)
        story.append(Spacer(1, 20))
        
        # Calculate statistics
        scores = [a.get('relevancy_score', 0) for a in analyses if a.get('relevancy_score')]
        if scores:
            avg_score = sum(scores) / len(scores)
            high_priority = len([s for s in scores if s >= 4])
            medium_priority = len([s for s in scores if 2 <= s <= 3])
            low_priority = len([s for s in scores if s <= 1])
            
            stats_info = f"""
            <b>Analysis Summary:</b><br/>
            • Average Relevancy Score: {avg_score:.1f}/5<br/>
            • High Priority Leads (4-5): {high_priority}<br/>
            • Medium Priority Leads (2-3): {medium_priority}<br/>
            • Low Priority Leads (1): {low_priority}<br/>
            """
            
            stats_para = Paragraph(stats_info, self.styles['CustomBody'])
            story.append(stats_para)
        
        return story
    
    def _create_lead_analyses(self, analyses: List[Dict[str, Any]]) -> List:
        """Create lead analyses section"""
        story = []
        
        # Section title
        title = Paragraph("Lead Analyses", self.styles['CustomHeading'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        for i, analysis in enumerate(analyses, 1):
            story.extend(self._create_single_analysis(analysis, i))
            
            # Add page break every 3 analyses to avoid overcrowding
            if i % 3 == 0 and i < len(analyses):
                story.append(PageBreak())
            else:
                story.append(Spacer(1, 20))
        
        return story
    
    def _create_single_analysis(self, analysis: Dict[str, Any], index: int) -> List:
        """Create content for a single lead analysis"""
        story = []
        
        # Lead title and number
        lead_title = f"Lead {index}: {analysis.get('title', 'Untitled')}"
        title_para = Paragraph(lead_title, self.styles['CustomHeading'])
        story.append(title_para)
        story.append(Spacer(1, 8))
        
        # Relevancy score with color coding
        score = analysis.get('relevancy_score', 0)
        score_text = f"<b>Relevancy Score:</b> {score}/5"
        score_para = Paragraph(score_text, self.styles['ScoreStyle'])
        story.append(score_para)
        story.append(Spacer(1, 8))
        
        # Description
        if analysis.get('description'):
            desc_text = f"<b>Description:</b> {analysis['description'][:300]}"
            if len(analysis['description']) > 300:
                desc_text += "..."
            desc_para = Paragraph(desc_text, self.styles['CustomBody'])
            story.append(desc_para)
            story.append(Spacer(1, 8))
        
        # Link (clickable)
        if analysis.get('link'):
            link_text = f"<b>Source:</b> <link href='{analysis['link']}'>{analysis['link']}</link>"
            link_para = Paragraph(link_text, self.styles['LinkStyle'])
            story.append(link_para)
            story.append(Spacer(1, 8))
        
        # AI Analysis with better formatting
        if analysis.get('ai_analysis'):
            ai_text = f"<b>AI Analysis:</b><br/>{analysis['ai_analysis']}"
            ai_para = Paragraph(ai_text, self.styles['CustomBody'])
            story.append(ai_para)
            story.append(Spacer(1, 8))
        
        # Key Opinion Leaders
        if analysis.get('key_opinion_leaders'):
            kol_text = f"<b>Key Opinion Leaders:</b> {analysis['key_opinion_leaders']}"
            kol_para = Paragraph(kol_text, self.styles['CustomBody'])
            story.append(kol_para)
            story.append(Spacer(1, 8))
        
        # Contact Information
        if analysis.get('contact_info'):
            contact_text = f"<b>Contact Information:</b> {analysis['contact_info']}"
            contact_para = Paragraph(contact_text, self.styles['CustomBody'])
            story.append(contact_para)
            story.append(Spacer(1, 8))
        
        # Notes
        if analysis.get('notes'):
            notes_text = f"<b>Notes:</b> {analysis['notes']}"
            notes_para = Paragraph(notes_text, self.styles['CustomBody'])
            story.append(notes_para)
        
        # Add separator
        story.append(Spacer(1, 15))
        
        return story
    
    def _create_custom_title_page(self, project: Dict[str, Any], company_name: str, disclaimer: str) -> List:
        """Create custom title page with company branding and logo"""
        story = []
        
        # Try to add company logo
        logo_path = "static/images/4front2market_logo.png"
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 20))
            except Exception as e:
                if logger:
                    logger.warning(f"Could not add logo: {e}")
        
        # Company branding
        company_title = Paragraph(f"{company_name}", self.styles['CustomTitle'])
        story.append(company_title)
        story.append(Spacer(1, 20))
        
        # Beta version notice
        beta_notice = Paragraph("Beta Version Report", self.styles['CustomHeading'])
        story.append(beta_notice)
        story.append(Spacer(1, 15))
        
        # Report title
        title = Paragraph(f"Lead Discovery Project Report", self.styles['CustomHeading'])
        story.append(title)
        story.append(Spacer(1, 30))
        
        # Project name
        project_title = Paragraph(f"Project: {project['name']}", self.styles['CustomHeading'])
        story.append(project_title)
        story.append(Spacer(1, 20))
        
        # Project description
        if project.get('description'):
            desc = Paragraph(f"Description: {project['description']}", self.styles['CustomBody'])
            story.append(desc)
            story.append(Spacer(1, 20))
        
        # Generated date
        date_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        date_para = Paragraph(date_text, self.styles['CustomBody'])
        story.append(date_para)
        story.append(Spacer(1, 20))
        
        # Contact information
        contact_info = f"Contact: daniel.hesse@4front2market.se"
        contact_para = Paragraph(contact_info, self.styles['CustomBody'])
        story.append(contact_para)
        story.append(Spacer(1, 30))
        
        # Beta disclaimer
        beta_disclaimer = f"<b>BETA VERSION DISCLAIMER:</b><br/><i>{disclaimer}</i>"
        disclaimer_para = Paragraph(beta_disclaimer, self.styles['CustomBody'])
        story.append(disclaimer_para)
        story.append(Spacer(1, 30))
        
        # Summary stats
        story.extend(self._create_summary_stats(project))
        
        return story
    
    def _create_custom_introduction_section(self, project: Dict[str, Any], analyses: List[Dict[str, Any]], 
                                           custom_content: Dict[str, Any], company_name: str) -> List:
        """Create custom introduction section with user-edited content"""
        story = []
        
        # Introduction Title
        intro_title = Paragraph("Executive Summary & Introduction", self.styles['CustomHeading'])
        story.append(intro_title)
        story.append(Spacer(1, 20))
        
        # Custom background (use user content if provided)
        background_text = custom_content.get('background', f"""
        <b>Background and Purpose:</b><br/>
        This report presents the results of an AI-powered lead discovery analysis conducted using {company_name}'s advanced semantic analysis capabilities. 
        The analysis leverages machine learning algorithms to identify and evaluate potential business opportunities, research collaborations, and market intelligence from diverse data sources including academic publications, industry reports, and web content.
        """)
        background_para = Paragraph(background_text, self.styles['CustomBody'])
        story.append(background_para)
        story.append(Spacer(1, 15))
        
        # Custom methodology
        methodology_text = custom_content.get('methodology', f"""
        <b>Methodology:</b><br/>
        The analysis was conducted using {company_name}'s proprietary AI algorithms and data processing techniques. 
        Each lead was evaluated based on multiple criteria including relevance to the project scope, business potential, and collaboration opportunities.
        """)
        methodology_para = Paragraph(methodology_text, self.styles['CustomBody'])
        story.append(methodology_para)
        story.append(Spacer(1, 15))
        
        # Custom objectives
        objectives_text = custom_content.get('objectives', f"""
        <b>Key Objectives:</b><br/>
        • Identify high-potential leads and business opportunities relevant to the project scope<br/>
        • Benchmark market activity and identify emerging trends in the target domain<br/>
        • Extract actionable intelligence including contact information, product details, and collaboration opportunities<br/>
        • Provide evidence-based recommendations for strategic decision-making<br/>
        • Establish a foundation for ongoing market monitoring and lead generation
        """)
        objectives_para = Paragraph(objectives_text, self.styles['CustomBody'])
        story.append(objectives_para)
        
        return story
    
    def _create_company_footer(self, company_name: str, disclaimer: str) -> List:
        """Create company footer with branding and disclaimer"""
        story = []
        
        story.append(PageBreak())
        
        # Footer title
        footer_title = Paragraph("Report Information", self.styles['CustomHeading'])
        story.append(footer_title)
        story.append(Spacer(1, 20))
        
        # Company information
        company_info = f"""
        <b>Report Generated By:</b><br/>
        {company_name}<br/>
        AI-Powered Lead Discovery Platform<br/>
        <br/>
        <b>Contact Information:</b><br/>
        daniel.hesse@4front2market.se<br/>
        <br/>
        <b>Software Version:</b><br/>
        LeadFinder Beta Version<br/>
        <br/>
        <b>Beta Version Disclaimer:</b><br/>
        {disclaimer}<br/>
        <br/>
        <b>Report Generation Date:</b><br/>
        {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>
        <br/>
        <b>Confidentiality:</b><br/>
        This report contains proprietary information and should be treated as confidential.<br/>
        <br/>
        <b>Ownership:</b><br/>
        This report and the underlying analysis technology are proprietary to {company_name}.
        """
        
        footer_para = Paragraph(company_info, self.styles['CustomBody'])
        story.append(footer_para)
        
        return story


# Global PDF service instance
pdf_service = PDFService() 