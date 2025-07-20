"""
Markdown Export Service for LeadFinder

This module provides Markdown generation functionality for collaborative workshops
with editable sections for team collaboration and lead analysis.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from utils.logger import get_logger
    logger = get_logger('markdown_service')
except ImportError:
    logger = None

class MarkdownService:
    def __init__(self, export_folder: str = "exports"):
        self.export_folder = export_folder
        self._ensure_export_folder()
    
    def _ensure_export_folder(self):
        """Ensure export folder exists"""
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
            if logger:
                logger.info(f"Created export folder: {self.export_folder}")
    
    def generate_workshop_report(self, project: Dict[str, Any], analyses: List[Dict[str, Any]]) -> str:
        """
        Generate a collaborative Markdown workshop report
        
        Args:
            project: Project information
            analyses: List of lead analyses
            
        Returns:
            Path to generated Markdown file
        """
        if not analyses:
            raise ValueError("No analyses provided for report generation")
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_project_name = "".join(c for c in project['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"workshop_report_{safe_project_name}_{timestamp}.md"
        filepath = os.path.join(self.export_folder, filename)
        
        # Generate Markdown content
        markdown_content = self._create_workshop_content(project, analyses)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        if logger:
            logger.info(f"Generated Markdown workshop report: {filepath}")
        
        return filepath
    
    def _create_workshop_content(self, project: Dict[str, Any], analyses: List[Dict[str, Any]]) -> str:
        """Create the complete workshop Markdown content"""
        content = []
        
        # Title Section
        content.extend(self._create_title_section(project, analyses))
        
        # Structured Introduction
        content.extend(self._create_introduction_section(project, analyses))
        
        # Lead Analysis Section
        content.extend(self._create_lead_analysis_section(analyses))
        
        # Workshop Notes Section
        content.extend(self._create_workshop_notes_section())
        
        return '\n\n'.join(content)
    
    def _create_title_section(self, project: Dict[str, Any], analyses: List[Dict[str, Any]]) -> List[str]:
        """Create title section"""
        content = []
        
        # Main title
        content.append(f"# Market Report: AI-Powered Lead Discovery for {project['name']}")
        content.append("")
        
        # Subtitle and metadata
        content.append("## Workshop Report")
        content.append("")
        content.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}")
        content.append(f"**Project:** {project['name']}")
        if project.get('description'):
            content.append(f"**Description:** {project['description']}")
        content.append(f"**Total Leads:** {len(analyses)}")
        content.append("")
        content.append("---")
        content.append("")
        
        return content
    
    def _create_introduction_section(self, project: Dict[str, Any], analyses: List[Dict[str, Any]]) -> List[str]:
        """Create structured introduction section"""
        content = []
        
        content.append("## Executive Summary & Introduction")
        content.append("")
        
        # Background and Purpose
        content.append("### Background and Purpose")
        content.append("")
        content.append("This report presents the results of an AI-powered lead discovery analysis conducted using LeadFinder's advanced semantic analysis capabilities. The analysis leverages machine learning algorithms to identify and evaluate potential business opportunities, research collaborations, and market intelligence from diverse data sources including academic publications, industry reports, and web content.")
        content.append("")
        
        # Scope of the Report
        content.append("### Scope of the Report")
        content.append("")
        content.append("- **Data Sources:** Academic publications, industry reports, web content, and research databases")
        content.append("- **Methodology:** AI-based semantic analysis using advanced language models for relevance scoring and content extraction")
        content.append(f"- **Time Frame:** Analysis conducted on {datetime.now().strftime('%B %d, %Y')}")
        content.append(f"- **Sample Size:** {len(analyses)} leads analyzed with comprehensive evaluation")
        content.append("")
        
        # Key Objectives
        content.append("### Key Objectives")
        content.append("")
        content.append("- Identify high-potential leads and business opportunities relevant to the project scope")
        content.append("- Benchmark market activity and identify emerging trends in the target domain")
        content.append("- Extract actionable intelligence including contact information, product details, and collaboration opportunities")
        content.append("- Provide evidence-based recommendations for strategic decision-making")
        content.append("- Establish a foundation for ongoing market monitoring and lead generation")
        content.append("")
        
        # What to Expect
        content.append("### What to Expect from This Report")
        content.append("")
        content.append("This report contains detailed lead analyses including relevance scores (1-5 scale), direct links to source materials, AI-generated summaries, and extracted contact information. Each lead has been evaluated for business potential, technological relevance, and collaboration opportunities. Future versions may include deeper competitive analysis, trend forecasting, and automated follow-up recommendations.")
        content.append("")
        
        # Workshop Instructions
        content.append("### Workshop Instructions")
        content.append("")
        content.append("This collaborative report is designed for team workshops. Each lead analysis includes editable sections where team members can:")
        content.append("- **Add comments and insights**")
        content.append("- **Update relevance scores**")
        content.append("- **Expand contact information**")
        content.append("- **Note follow-up actions**")
        content.append("- **Identify collaboration opportunities**")
        content.append("")
        content.append("Use the sections below to collaborate and enhance the analysis.")
        content.append("")
        content.append("---")
        content.append("")
        
        return content
    
    def _create_lead_analysis_section(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """Create lead analysis section with editable areas"""
        content = []
        
        content.append("## Lead Analysis")
        content.append("")
        
        # Calculate statistics
        scores = [a.get('relevancy_score', 0) for a in analyses if a.get('relevancy_score')]
        if scores:
            avg_score = sum(scores) / len(scores)
            high_priority = len([s for s in scores if s >= 4])
            medium_priority = len([s for s in scores if 2 <= s <= 3])
            low_priority = len([s for s in scores if s <= 1])
            
            content.append("### Analysis Summary")
            content.append("")
            content.append(f"- **Average Relevancy Score:** {avg_score:.1f}/5")
            content.append(f"- **High Priority Leads (4-5):** {high_priority}")
            content.append(f"- **Medium Priority Leads (2-3):** {medium_priority}")
            content.append(f"- **Low Priority Leads (1):** {low_priority}")
            content.append("")
        
        # Individual lead analyses
        for i, analysis in enumerate(analyses, 1):
            content.extend(self._create_single_lead_analysis(analysis, i))
        
        return content
    
    def _create_single_lead_analysis(self, analysis: Dict[str, Any], index: int) -> List[str]:
        """Create content for a single lead analysis with editable sections"""
        content = []
        
        # Lead header
        content.append(f"### Lead {index}: {analysis.get('title', 'Untitled')}")
        content.append("")
        
        # Current AI Analysis
        content.append("#### Current AI Analysis")
        content.append("")
        
        # Relevancy score
        score = analysis.get('relevancy_score', 0)
        score_emoji = self._get_score_emoji(score)
        content.append(f"**Relevancy Score:** {score_emoji} {score}/5")
        content.append("")
        
        # Description
        if analysis.get('description'):
            content.append("**Description:**")
            content.append(f"{analysis['description']}")
            content.append("")
        
        # Source link
        if analysis.get('link'):
            content.append("**Source:**")
            content.append(f"[{analysis['link']}]({analysis['link']})")
            content.append("")
        
        # AI Analysis
        if analysis.get('ai_analysis'):
            content.append("**AI Analysis:**")
            content.append(f"{analysis['ai_analysis']}")
            content.append("")
        
        # Current extracted information
        if analysis.get('key_opinion_leaders'):
            content.append("**Key Opinion Leaders:**")
            content.append(f"{analysis['key_opinion_leaders']}")
            content.append("")
        
        if analysis.get('contact_info'):
            content.append("**Contact Information:**")
            content.append(f"{analysis['contact_info']}")
            content.append("")
        
        # Editable Workshop Sections
        content.append("#### Workshop Collaboration")
        content.append("")
        
        # Team scoring
        content.append("**Team Relevance Score:**")
        content.append("<!-- Update the score below based on team discussion -->")
        content.append(f"Current: {score}/5")
        content.append("Team Score: ___/5")
        content.append("")
        
        # Team comments
        content.append("**Team Comments & Insights:**")
        content.append("<!-- Add team insights, additional context, or concerns -->")
        content.append("")
        content.append("- ")
        content.append("- ")
        content.append("- ")
        content.append("")
        
        # Enhanced contact information
        content.append("**Enhanced Contact Information:**")
        content.append("<!-- Add any additional contact details discovered during research -->")
        content.append("")
        content.append("- **Emails:** ")
        content.append("- **Phone Numbers:** ")
        content.append("- **Social Media:** ")
        content.append("- **Company Website:** ")
        content.append("")
        
        # Follow-up actions
        content.append("**Follow-up Actions:**")
        content.append("<!-- List specific actions to take with this lead -->")
        content.append("")
        content.append("- [ ] ")
        content.append("- [ ] ")
        content.append("- [ ] ")
        content.append("")
        
        # Collaboration opportunities
        content.append("**Collaboration Opportunities:**")
        content.append("<!-- Identify potential collaboration or partnership opportunities -->")
        content.append("")
        content.append("- ")
        content.append("- ")
        content.append("- ")
        content.append("")
        
        # Risk assessment
        content.append("**Risk Assessment:**")
        content.append("<!-- Note any risks, concerns, or red flags -->")
        content.append("")
        content.append("- ")
        content.append("- ")
        content.append("- ")
        content.append("")
        
        content.append("---")
        content.append("")
        
        return content
    
    def _create_workshop_notes_section(self) -> List[str]:
        """Create general workshop notes section"""
        content = []
        
        content.append("## General Workshop Notes")
        content.append("")
        
        content.append("### Overall Assessment")
        content.append("<!-- Provide overall assessment of the leads and market opportunities -->")
        content.append("")
        content.append("")
        
        content.append("### Market Trends Identified")
        content.append("<!-- Note any trends or patterns observed across the leads -->")
        content.append("")
        content.append("- ")
        content.append("- ")
        content.append("- ")
        content.append("")
        
        content.append("### Strategic Recommendations")
        content.append("<!-- Provide strategic recommendations based on the analysis -->")
        content.append("")
        content.append("- ")
        content.append("- ")
        content.append("- ")
        content.append("")
        
        content.append("### Next Steps")
        content.append("<!-- Define next steps and action items -->")
        content.append("")
        content.append("- [ ] ")
        content.append("- [ ] ")
        content.append("- [ ] ")
        content.append("")
        
        content.append("### Team Assignments")
        content.append("<!-- Assign responsibilities for follow-up actions -->")
        content.append("")
        content.append("| Action | Assigned To | Due Date | Status |")
        content.append("|--------|-------------|----------|--------|")
        content.append("| | | | |")
        content.append("| | | | |")
        content.append("| | | | |")
        content.append("")
        
        content.append("### Additional Research Needed")
        content.append("<!-- Note any areas requiring additional research -->")
        content.append("")
        content.append("- ")
        content.append("- ")
        content.append("- ")
        content.append("")
        
        return content
    
    def _get_score_emoji(self, score: int) -> str:
        """Get emoji for relevancy score"""
        if score >= 4:
            return "🟢"  # Green circle for high priority
        elif score == 3:
            return "🟡"  # Yellow circle for medium priority
        else:
            return "🔴"  # Red circle for low priority

# Global Markdown service instance
markdown_service = MarkdownService() 