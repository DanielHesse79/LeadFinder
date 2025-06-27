from flask import Flask, render_template_string, request, redirect, url_for, send_file
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

SERPAPI_KEY = '3ec483ba975854440e360e49e098a19cb204d80455f39963fe1e2680799d970a'
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_NAME = "mistral"
ollama_status = {"ok": False, "msg": "Ej kontrollerad"}
DB_PATH = 'leads.db'

# Lista över populära SERPAPI-motorer (kan utökas vid behov)
SERP_ENGINES = [
    "google", "bing", "yahoo", "duckduckgo", "google_news", "google_scholar", "google_ai_overview", "google_immersive_product"
]

app = Flask(__name__)

def check_ollama_and_model():
    global ollama_status
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if response.status_code != 200:
            ollama_status = {"ok": False, "msg": "Ollama svarar inte korrekt."}
            return False
    except requests.exceptions.RequestException:
        ollama_status = {"ok": False, "msg": "Ollama verkar inte vara igång."}
        return False
    tags = response.json().get("models", [])
    available_models = [tag["name"] for tag in tags]
    if MODEL_NAME not in available_models:
        try:
            subprocess.run(["ollama", "pull", MODEL_NAME], check=True)
            ollama_status = {"ok": True, "msg": f"Modellen '{MODEL_NAME}' laddades."}
            return True
        except Exception:
            ollama_status = {"ok": False, "msg": f"Kunde inte ladda ner modellen '{MODEL_NAME}'."}
            return False
    ollama_status = {"ok": True, "msg": "Ollama och modellen är redo."}
    return True

def ollama_check_thread():
    check_ollama_and_model()

# Starta kontrollen i bakgrunden vid app-start
t = threading.Thread(target=ollama_check_thread)
t.start()

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

def get_trends(query):
    pytrends = TrendReq(hl='en-US', tz=360)
    try:
        pytrends.build_payload([query], cat=0, timeframe='today 12-m')
        data = pytrends.interest_over_time()
        if not data.empty:
            score = int(data[query].mean())
            return {query: score}
        else:
            return {query: 0}
    except Exception as e:
        print(f"[LOG] Google Trends error: {e}")
        return {query: 0}

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        snippet TEXT,
        link TEXT,
        ai_summary TEXT
    )''')
    conn.commit()
    conn.close()

def save_lead(db_path, title, snippet, link, ai_summary):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO leads (title, snippet, link, ai_summary) VALUES (?, ?, ?, ?)',
              (title, snippet, link, ai_summary))
    conn.commit()
    conn.close()

def google_search(query, api_key, engine="google", num_results=10):
    print(f"[LOG] Kör {engine}-sökning med query: '{query}'")
    params = {
        "engine": engine,
        "q": query,
        "api_key": api_key,
        "num": num_results,
        "hl": "en"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic = results.get('organic_results', [])
    print(f"[LOG] {engine} - Antal resultat: {len(organic)}")
    return organic

def fetch_full_text(url, max_chars=4000):
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        full_text = ' '.join(p.get_text() for p in paragraphs)
        print(f"[LOG] Hämtade {len(full_text)} tecken från sidan.")
        return full_text.strip().replace('\n', ' ')[:max_chars]
    except Exception as e:
        print(f"[LOG] Kunde inte hämta text från sidan: {e}")
        return ""

def download_pdf_from_doi(doi, output_folder="scihub_pdfs"):
    url = f"https://sci-hub.se/{doi}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        iframe = soup.find("iframe")
        if not iframe or not iframe.get("src"):
            print(f"Ingen PDF hittad för DOI: {doi}")
            return False

        pdf_url = iframe["src"]
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url

        pdf_response = requests.get(pdf_url, headers=headers)
        pdf_response.raise_for_status()

        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.join(output_folder, f"{doi.replace('/', '_')}.pdf")
        with open(filename, "wb") as f:
            f.write(pdf_response.content)

        print(f"✅ Nedladdad: {filename}")
        return True
    except Exception as e:
        print(f"❌ Misslyckades för {doi}: {e}")
        return False

def analyze_lead_with_ollama(title, snippet, link, research_question="epigenetik och pre-diabetes"):
    print(f"[LOG] Hämtar och analyserar: {title} ({link})")
    page_text = fetch_full_text(link)

    if not page_text:
        print("[LOG] Ingen text hämtad, skippar AI-analys.")
        return None

    prompt = f"""
Jag har hämtat följande text från en webbsida:
Titel: {title}
Länk: {link}
Text: {page_text}

Analysera detta. Handlar det om {research_question}?
Svara endast med "JA" om det är relevant, eller "NEJ" om det inte är relevant.
"""

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        print(f"[LOG] Ollama status: {response.status_code}")
        print(f"[LOG] Ollama raw response: {response.text[:300]}")

        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                ai_response = data["response"].strip().upper()
                print(f"[LOG] AI-svar: {ai_response}")
                
                if "JA" in ai_response:
                    # Om relevant, gör en detaljerad analys
                    detailed_prompt = f"""
Jag har hämtat följande text från en webbsida:
Titel: {title}
Länk: {link}
Text: {page_text}

Detta är relevant för {research_question}. Ge ett kort svar på svenska med: företagsnamn, varför det är relevant, samt ev. kontaktinfo.
"""
                    detailed_payload = {
                        "model": "mistral",
                        "prompt": detailed_prompt,
                        "stream": False
                    }
                    
                    detailed_response = requests.post("http://localhost:11434/api/generate", json=detailed_payload, timeout=120)
                    if detailed_response.status_code == 200:
                        detailed_data = detailed_response.json()
                        if "response" in detailed_data:
                            return detailed_data["response"].strip()
                
                return None  # Inte relevant
            else:
                print("[LOG] Nyckeln 'response' saknas.")
                return None
        else:
            print(f"[LOG] Ollama fel: {response.status_code}")
            return None
    except Exception as e:
        print(f"[LOG] Exception vid AI-anrop: {e}")
        return None

@app.route('/', methods=['GET'])
def show_leads():
    init_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM leads ORDER BY id DESC')
    leads = c.fetchall()
    conn.close()
    print(f"[LOG] Visar {len(leads)} leads på startsidan.")
    return render_template_string(HTML, leads=leads, searching=False, research_question="epigenetik och pre-diabetes", engines=SERP_ENGINES, selected_engines=["google"], trends=None, ollama_status=ollama_status)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    research_question = request.form.get('research_question', "epigenetik och pre-diabetes")
    selected_engines = request.form.getlist('engines')
    if not selected_engines:
        selected_engines = ["google"]
    print(f"[LOG] Sökterm mottagen: {query}")
    print(f"[LOG] Frågeställning: {research_question}")
    print(f"[LOG] Valda motorer: {selected_engines}")
    all_results = []
    for engine in selected_engines:
        results = google_search(query, SERPAPI_KEY, engine=engine)
        all_results.extend(results)
    if not all_results:
        print("[LOG] Inga resultat hittades från någon motor.")
    
    relevant_leads = 0
    for res in all_results:
        title = res.get('title', '')
        snippet = res.get('snippet', '')
        link = res.get('link', '')
        print(f"[LOG] Analyserar lead: {title}")
        ai_summary = analyze_lead_with_ollama(title, snippet, link, research_question)
        
        if ai_summary:  # Endast spara om AI:n tycker det är relevant
            save_lead(DB_PATH, title, snippet, link, ai_summary)
            print(f"[LOG] Relevant lead sparad: {title}")
            relevant_leads += 1
        else:
            print(f"[LOG] Inte relevant, hoppar över: {title}")
    
    print(f"[LOG] Totalt {len(all_results)} leads analyserade, {relevant_leads} relevanta sparade.")
    
    # Visa leads efter sökning
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM leads ORDER BY id DESC')
    leads = c.fetchall()
    conn.close()
    print(f"[LOG] Visar {len(leads)} leads efter sökning.")
    trends = get_trends(query)
    return render_template_string(HTML, leads=leads, searching=False, research_question=research_question, engines=SERP_ENGINES, selected_engines=selected_engines, trends=trends, ollama_status=ollama_status)

@app.route('/export')
def export_to_excel():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, snippet, link, ai_summary FROM leads ORDER BY id DESC')
    leads = c.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"
    headers = ["ID", "Titel", "Beskrivning", "Länk", "AI-sammanfattning"]
    ws.append(headers)

    for lead in leads:
        row = list(lead)
        ws.append(row)
        # Gör länken klickbar
        link_cell = ws.cell(row=ws.max_row, column=4)
        link_cell.hyperlink = row[3]
        link_cell.font = Font(color="0000FF", underline="single")

    # Sätt kolumnbredd
    for i, col in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(i)].width = 30

    filename = "leads_export.xlsx"
    wb.save(filename)
    return send_file(filename, as_attachment=True)

@app.route('/ollama_check', methods=['POST'])
def ollama_check():
    check_ollama_and_model()
    return redirect(url_for('show_leads'))

@app.route('/download_links')
def download_links():
    excel_path = 'leads_export.xlsx'
    output_folder = '/mnt/seagate/leads_downloads'
    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_excel(excel_path)
    downloaded = []

    if 'Länk' not in df.columns:
        return '<b>Ingen kolumn "Länk" hittades i Excel-filen.</b>'

    for _, row in df.iterrows():
        url = str(row['Länk'])
        if isinstance(url, str) and url.startswith("http"):
            filename = url.split("/")[-1].split("?")[0] or f"lead_{row['ID']}.html"
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                with open(Path(output_folder) / filename, "wb") as f:
                    f.write(r.content)
                downloaded.append(f"<span style='color:green'>Nedladdad:</span> {filename}")
            except Exception as e:
                downloaded.append(f"<span style='color:red'>Misslyckades:</span> {url} - {e}")

    return "<br>".join(downloaded)

if __name__ == '__main__':
    app.run(debug=True, port=5050, host='0.0.0.0') 
