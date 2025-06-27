from flask import Blueprint, render_template, request, send_file, redirect, url_for
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
from pathlib import Path
import os
from typing import List, Tuple

# Import services with error handling
try:
    from models.database import db
except ImportError:
    db = None

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from services.serp_service import serp_service
except ImportError:
    serp_service = None

try:
    from config import EXPORT_FOLDER, SCIHUB_FOLDER, SERP_ENGINES, DEFAULT_RESEARCH_QUESTION
except ImportError:
    EXPORT_FOLDER = "exports"
    SCIHUB_FOLDER = "scihub"
    SERP_ENGINES = ["google"]
    DEFAULT_RESEARCH_QUESTION = "epigenetik och pre-diabetes"

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/')
def show_leads():
    """Display all leads"""
    if db:
        leads = db.get_all_leads()
        lead_count = db.get_lead_count()
        search_history = db.get_search_history(5)
    else:
        leads = []
        lead_count = 0
        search_history = []
    
    # Ensure ollama status is checked
    if ollama_service:
        ollama_status = ollama_service.check_status()
    else:
        ollama_status = {"ok": False, "msg": "Ollama service not available"}
    
    return render_template('leads.html', 
                         leads=leads, 
                         lead_count=lead_count,
                         search_history=search_history,
                         ollama_status=ollama_status,
                         engines=SERP_ENGINES,
                         selected_engines=["google"],
                         research_question=DEFAULT_RESEARCH_QUESTION)

@leads_bp.route('/export')
def export_to_excel():
    """Export leads to Excel file"""
    if not db:
        return "Database not available", 500
    
    leads = db.get_all_leads()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"
    headers = ["ID", "Titel", "Beskrivning", "Länk", "AI-sammanfattning", "Källa", "Skapad"]
    ws.append(headers)
    
    for lead in leads:
        row = list(lead)
        ws.append(row)
        # Make link clickable
        link_cell = ws.cell(row=ws.max_row, column=4)
        link_cell.hyperlink = row[3]
        link_cell.font = Font(color="0000FF", underline="single")
    
    # Set column width
    for i, col in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(i)].width = 30
    
    filename = "leads_export.xlsx"
    wb.save(filename)
    return send_file(filename, as_attachment=True)

@leads_bp.route('/download_links')
def download_links():
    """Download content from all links in Excel file"""
    logs = []
    excel_path = 'leads_export.xlsx'
    
    try:
        os.makedirs(EXPORT_FOLDER, exist_ok=True)
        logs.append(f"Mapp OK: {EXPORT_FOLDER}")
    except Exception as e:
        logs.append(f"<span style='color:red'>Kunde inte skapa mapp: {EXPORT_FOLDER} - {e}</span>")
        return "<br>".join(logs)
    
    try:
        df = pd.read_excel(excel_path)
        logs.append(f"Excel OK: {excel_path}")
        logs.append(f"Kolumner: {list(df.columns)}")
        logs.append(f"Antal rader: {len(df)}")
    except Exception as e:
        logs.append(f"<span style='color:red'>Kunde inte läsa Excel: {e}</span>")
        return "<br>".join(logs)
    
    if 'Länk' not in df.columns:
        logs.append('<b>Ingen kolumn "Länk" hittades i Excel-filen.</b>')
        return "<br>".join(logs)
    
    n_links = 0
    for _, row in df.iterrows():
        url = str(row['Länk'])
        if isinstance(url, str) and url.startswith("http"):
            n_links += 1
            filename = url.split("/")[-1].split("?")[0] or f"lead_{row['ID']}.html"
            try:
                import requests
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                with open(Path(EXPORT_FOLDER) / filename, "wb") as f:
                    f.write(r.content)
                logs.append(f"<span style='color:green'>Nedladdad:</span> {filename}")
            except Exception as e:
                logs.append(f"<span style='color:red'>Misslyckades:</span> {url} - {e}")
    
    if n_links == 0:
        logs.append('<b>Inga giltiga länkar hittades i kolumnen "Länk".</b>')
    
    return "<br>".join(logs)

@leads_bp.route('/delete/<int:lead_id>', methods=['POST'])
def delete_lead(lead_id: int):
    """Delete a specific lead"""
    if not db:
        return "Database not available", 500
    
    if db.delete_lead(lead_id):
        return redirect(url_for('leads.show_leads'))
    else:
        return "Error deleting lead", 400

@leads_bp.route('/leads_by_source/<source>')
def leads_by_source(source: str):
    """Show leads filtered by source"""
    if not db:
        leads = []
    else:
        leads = db.get_leads_by_source(source)
    
    # Ensure ollama status is checked
    if ollama_service:
        ollama_status = ollama_service.check_status()
    else:
        ollama_status = {"ok": False, "msg": "Ollama service not available"}
    
    return render_template('leads.html', 
                         leads=leads, 
                         lead_count=len(leads),
                         current_source=source,
                         ollama_status=ollama_status,
                         engines=SERP_ENGINES,
                         selected_engines=["google"],
                         research_question=DEFAULT_RESEARCH_QUESTION) 