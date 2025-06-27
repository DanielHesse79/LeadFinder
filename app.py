"""
LeadFinder Main Application

This is the main Flask application entry point for LeadFinder.
It provides a web interface for lead discovery and management.
"""

from flask import Flask, render_template_string, request, redirect, url_for, send_file, jsonify
import sqlite3
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
import threading
import time
import subprocess
import pandas as pd
from pathlib import Path
import os
from typing import List, Dict, Any, Optional

# Import configuration and utilities
from config import (
    SERPAPI_KEY, OLLAMA_BASE_URL, OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT,
    DB_PATH, SERP_ENGINES, EXPORT_FOLDER, SCIHUB_FOLDER, FLASK_SECRET_KEY,
    DEFAULT_RESEARCH_QUESTION, MAX_TEXT_LENGTH, REQUEST_TIMEOUT
)
from utils.logger import get_logger

# Initialize logger
logger = get_logger('app')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Global state
ollama_status = {"ok": False, "msg": "Ej kontrollerad"}

def check_ollama_and_model():
    """Check if Ollama server and model are available"""
    global ollama_status
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        if response.status_code != 200:
            ollama_status = {"ok": False, "msg": "Ollama svarar inte korrekt."}
            logger.warning("Ollama server not responding correctly")
            return False
    except requests.exceptions.RequestException as e:
        ollama_status = {"ok": False, "msg": "Ollama verkar inte vara igång."}
        logger.error(f"Ollama server not available: {e}")
        return False
    
    tags = response.json().get("models", [])
    available_models = [tag["name"] for tag in tags]
    logger.info(f"Available models: {available_models}")
    
    if OLLAMA_MODEL not in available_models:
        try:
            logger.info(f"Model {OLLAMA_MODEL} not found, attempting to pull...")
            subprocess.run(["ollama", "pull", OLLAMA_MODEL], check=True)
            ollama_status = {"ok": True, "msg": f"Modellen '{OLLAMA_MODEL}' laddades."}
            logger.info(f"Successfully pulled model {OLLAMA_MODEL}")
            return True
        except Exception as e:
            ollama_status = {"ok": False, "msg": f"Kunde inte ladda ner modellen '{OLLAMA_MODEL}'."}
            logger.error(f"Failed to pull model {OLLAMA_MODEL}: {e}")
            return False
    
    ollama_status = {"ok": True, "msg": "Ollama och modellen är redo."}
    logger.info("Ollama and model are ready")
    return True

def ollama_check_thread():
    """Background thread for Ollama status check"""
    check_ollama_and_model()

# Start background check
t = threading.Thread(target=ollama_check_thread, daemon=True)
t.start()

# HTML template moved to separate file for better organization
HTML = '''
<!doctype html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <title>Leadfinder - Leads</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; }
        th { background: #eee; }
        form { margin-bottom: 2em; }
        input[type=text] { width: 400px; padding: 6px; }
        input[type=submit] { padding: 6px 12px; }
        .status-dot { display: inline-block; width: 16px; height: 16px; border-radius: 8px; margin-right: 8px; }
        .status-green { background: #0c0; }
        .status-red { background: #c00; }
    </style>
</head>
<body>
    <h1>Leads</h1>
    <div>
        <span class="status-dot {% if ollama_status.ok %}status-green{% else %}status-red{% endif %}"></span>
        Ollama/Mistral-status: {{ ollama_status.msg }}
        {% if not ollama_status.ok %}
            <form method="post" action="/ollama_check" style="display:inline;">
                <button type="submit">Försök igen</button>
            </form>
        {% endif %}
    </div>
    <a href="/export"><button>Exportera till Excel</button></a>
    <a href="/download_links"><button>Ladda ner alla länkars innehåll</button></a><br><br>
    <form method="post" action="/search">
        <input type="text" name="query" placeholder="Skriv in sökfråga..." required><br><br>
        <input type="text" name="research_question" placeholder="Vad ska AI:n leta efter?" value="{{ research_question }}"><br><br>
        <label>Välj SERP API-källor:</label><br>
        {% for engine in engines %}
            <input type="checkbox" name="engines" value="{{ engine }}" {% if engine in selected_engines %}checked{% endif %}> {{ engine }}<br>
        {% endfor %}
        <br><input type="submit" value="Sök">
    </form>
    {% if trends %}
        <h2>Google Trends (senaste 12 mån):</h2>
        <ul>
        {% for term, score in trends.items() %}
            <li><strong>{{ term }}</strong>: {{ score }}</li>
        {% endfor %}
        </ul>
    {% endif %}
    {% if searching %}<p>Söker... detta kan ta en stund.</p>{% endif %}
    <table>
        <tr>
            <th>ID</th>
            <th>Titel</th>
            <th>Beskrivning</th>
            <th>Länk</th>
            <th>AI-sammanfattning</th>
        </tr>
        {% for lead in leads %}
        <tr>
            <td>{{ lead[0] }}</td>
            <td>{{ lead[1] }}</td>
            <td>{{ lead[2] }}</td>
            <td><a href="{{ lead[3] }}" target="_blank">Länk</a></td>
            <td>{{ lead[4] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

def get_trends(query: str) -> Dict[str, int]:
    """Get Google Trends data for a query"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([query], cat=0, timeframe='today 12-m')
        data = pytrends.interest_over_time()
        if not data.empty:
            score = int(data[query].mean())
            logger.info(f"Google Trends score for '{query}': {score}")
            return {query: score}
        else:
            logger.warning(f"No Google Trends data for '{query}'")
            return {query: 0}
    except Exception as e:
        logger.error(f"Google Trends error for '{query}': {e}")
        return {query: 0}

def init_db(db_path: str) -> None:
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            snippet TEXT,
            link TEXT,
            ai_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {db_path}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def save_lead(db_path: str, title: str, snippet: str, link: str, ai_summary: str) -> None:
    """Save a lead to the database"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('INSERT INTO leads (title, snippet, link, ai_summary) VALUES (?, ?, ?, ?)',
                  (title, snippet, link, ai_summary))
        conn.commit()
        conn.close()
        logger.info(f"Lead saved: {title[:50]}...")
    except Exception as e:
        logger.error(f"Failed to save lead: {e}")
        raise

def google_search(query: str, api_key: str, engine: str = "google", num_results: int = 10) -> List[Dict[str, Any]]:
    """Perform a Google search using SerpAPI"""
    logger.info(f"Running {engine} search with query: '{query}'")
    params = {
        "engine": engine,
        "q": query,
        "api_key": api_key,
        "num": num_results,
        "hl": "en"
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get('organic_results', [])
        logger.info(f"{engine} - Number of results: {len(organic)}")
        return organic
    except Exception as e:
        logger.error(f"Search failed for {engine}: {e}")
        return []

def fetch_full_text(url: str, max_chars: int = MAX_TEXT_LENGTH) -> str:
    """Fetch and extract text content from a URL"""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        full_text = ' '.join(p.get_text() for p in paragraphs)
        logger.info(f"Fetched {len(full_text)} characters from page")
        return full_text.strip().replace('\n', ' ')[:max_chars]
    except Exception as e:
        logger.error(f"Could not fetch text from page: {e}")
        return ""

def download_pdf_from_doi(doi: str, output_folder: str = SCIHUB_FOLDER) -> Optional[str]:
    """Download PDF from DOI using Sci-Hub"""
    url = f"https://sci-hub.se/{doi}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            filename = f"{doi.replace('/', '_')}.pdf"
            filepath = Path(output_folder) / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"PDF downloaded: {filepath}")
            return str(filepath)
        else:
            logger.warning(f"Failed to download PDF for DOI {doi}: Status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading PDF for DOI {doi}: {e}")
        return None

def analyze_lead_with_ollama(title: str, snippet: str, link: str, research_question: str = DEFAULT_RESEARCH_QUESTION) -> Optional[str]:
    """Analyze a lead using Ollama AI"""
    if not ollama_status["ok"]:
        logger.warning("Ollama not available for analysis")
        return None
    
    logger.info(f"Analyzing lead: {title} ({link})")
    page_text = fetch_full_text(link)
    
    if not page_text:
        logger.warning("No text extracted, skipping AI analysis")
        return None
    
    prompt = f"""
Jag har hämtat följande text från en webbsida:
Titel: {title}
Länk: {link}
Text: {page_text}

Analysera detta. Handlar det om {research_question}?
Svara endast med "JA" om det är relevant, eller "NEJ" om det inte är relevant.
"""
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", "").strip().upper()
            logger.info(f"AI response: {ai_response}")
            
            if "JA" in ai_response:
                detailed_prompt = f"""
Jag har hämtat följande text från en webbsida:
Titel: {title}
Länk: {link}
Text: {page_text}

Detta är relevant för {research_question}. Ge ett kort svar på svenska med: företagsnamn, varför det är relevant, samt ev. kontaktinfo.
"""
                detailed_response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": detailed_prompt,
                        "stream": False
                    },
                    timeout=OLLAMA_TIMEOUT
                )
                
                if detailed_response.status_code == 200:
                    detailed_data = detailed_response.json()
                    return detailed_data.get("response", "").strip()
            
            return None
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return None

@app.route('/', methods=['GET'])
def show_leads():
    """Display all leads"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM leads ORDER BY id DESC')
        leads = c.fetchall()
        conn.close()
        
        return render_template_string(HTML, 
                                     leads=leads, 
                                     ollama_status=ollama_status,
                                     engines=SERP_ENGINES,
                                     selected_engines=["google"],
                                     research_question=DEFAULT_RESEARCH_QUESTION,
                                     trends=None,
                                     searching=False)
    except Exception as e:
        logger.error(f"Error showing leads: {e}")
        return f"Error: {e}", 500

@app.route('/search', methods=['POST'])
def search():
    """Perform search and analyze results"""
    try:
        query = request.form.get('query', '')
        research_question = request.form.get('research_question', DEFAULT_RESEARCH_QUESTION)
        engines = request.form.getlist('engines')
        
        if not engines:
            engines = ["google"]
        
        logger.info(f"Search request: {query} with engines: {engines}")
        
        # Get trends
        trends = get_trends(query)
        
        # Perform searches
        all_results = []
        for engine in engines:
            results = google_search(query, SERPAPI_KEY, engine)
            all_results.extend(results)
        
        # Analyze and save leads
        leads_saved = 0
        for result in all_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')
            
            if title and link:
                ai_summary = analyze_lead_with_ollama(title, snippet, link, research_question)
                if ai_summary:
                    save_lead(DB_PATH, title, snippet, link, ai_summary)
                    leads_saved += 1
        
        logger.info(f"Search completed: {leads_saved} leads saved")
        
        return redirect(url_for('show_leads'))
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search error: {e}", 500

@app.route('/export')
def export_to_excel():
    """Export leads to Excel file"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query('SELECT * FROM leads', conn)
        conn.close()
        
        filename = "leads_export.xlsx"
        df.to_excel(filename, index=False)
        
        logger.info(f"Exported {len(df)} leads to {filename}")
        return send_file(filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Export error: {e}")
        return f"Export error: {e}", 500

@app.route('/ollama_check', methods=['POST'])
def ollama_check():
    """Check Ollama status"""
    check_ollama_and_model()
    return redirect(url_for('show_leads'))

@app.route('/download_links')
def download_links():
    """Download content from all lead links"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT link FROM leads')
        links = c.fetchall()
        conn.close()
        
        Path(EXPORT_FOLDER).mkdir(parents=True, exist_ok=True)
        
        downloaded = 0
        for (link,) in links:
            if link and link.startswith('http'):
                try:
                    response = requests.get(link, timeout=REQUEST_TIMEOUT)
                    filename = link.split('/')[-1].split('?')[0] or f"lead_{downloaded}.html"
                    filepath = Path(EXPORT_FOLDER) / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded += 1
                    logger.info(f"Downloaded: {filename}")
                except Exception as e:
                    logger.error(f"Failed to download {link}: {e}")
        
        logger.info(f"Download completed: {downloaded} files")
        return f"Downloaded {downloaded} files to {EXPORT_FOLDER}"
    except Exception as e:
        logger.error(f"Download error: {e}")
        return f"Download error: {e}", 500

if __name__ == '__main__':
    # Initialize database
    init_db(DB_PATH)
    
    # Start Flask app
    from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
    logger.info(f"Starting LeadFinder on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG) 
