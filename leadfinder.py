import requests
import sqlite3
import os
from serpapi import GoogleSearch

# --- KONFIGURATION ---
SERPAPI_KEY = '3ec483ba975854440e360e49e098a19cb204d80455f39963fe1e2680799d970a'
OLLAMA_URL = 'http://localhost:11434/api/generate'
SEARCH_QUERY = 'epigenetics pre-diabetes company'
DB_PATH = 'leads.db'

# --- STEG 1: Sök på Google via SerpAPI ---
def google_search(query, api_key, num_results=10):
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": num_results,
        "hl": "en"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get('organic_results', [])

# --- STEG 2: Skicka till Ollama för AI-analys ---
def analyze_lead_with_ollama(title, snippet, link):
    prompt = f"""
Här är en webbsida om ett företag:
Titel: {title}
Beskrivning: {snippet}
Länk: {link}
Är detta ett företag som arbetar med 'epigenetics pre-diabetes'? Om ja, ge namn, beskrivning, ev. kontaktinfo, och varför de är relevanta. Svara på svenska.
"""
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json().get('response', '').strip()
    else:
        return None

# --- STEG 3: Spara i SQLite ---
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