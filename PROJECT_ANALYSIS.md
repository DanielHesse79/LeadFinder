# LeadFinder - Komplett Projektanalys

## 📋 Översikt

LeadFinder är en avancerad AI-driven plattform för lead discovery som kombinerar flera sökkällor, AI-analys och forskningsfinansiering. Projektet har genomgått en omfattande refaktorering från en enkel script till en modulär Flask-applikation.

## 🏗️ Mappstruktur och Moduler

### **Root-nivå**
```
leadfinder/
├── app.py                 # Huvudapplikation (Flask entry point)
├── config.py             # Centraliserad konfiguration
├── requirements.txt      # Python-beroenden
├── env.example          # Miljövariabel-mall
├── .gitignore           # Git-ignore regler
├── README.md            # Projekt-dokumentation
├── API_DOCUMENTATION.md # API-dokumentation
├── CHANGELOG.md         # Versionshistorik
├── REFACTORING_SUMMARY.md # Refaktorering-sammanfattning
├── DEPLOYMENT.md        # Deployment-guide
├── leads.db             # SQLite-databas
├── leadfinder.log       # Applikationsloggar
└── exports/             # Export-mapp
```

### **Core-moduler**

#### **📁 routes/** - Flask Blueprint Routes
- **`leads.py`** - Lead-hantering och visning
- **`search.py`** - Sökfunktionalitet
- **`ollama.py`** - AI-modellhantering
- **`research.py`** - Forskningsfinansiering
- **`config.py`** - Konfigurationshantering

#### **📁 services/** - Externa API-integrationer
- **`ollama_service.py`** - AI-integration (Ollama)
- **`serp_service.py`** - Sök-API (SerpAPI)
- **`pubmed_service.py`** - PubMed-integration (placeholder)
- **`orcid_service.py`** - ORCID-integration (placeholder)
- **`research_service.py`** - Forskningsfinansiering APIs
- **`swecris_api.py`** - SweCRIS API
- **`api_base.py`** - Bas-klass för API-integrationer

#### **📁 models/** - Databasmodeller
- **`database.py`** - Databasoperationer och modeller
- **`config.py`** - Konfigurationsmodell

#### **📁 utils/** - Hjälpfunktioner
- **`logger.py`** - Loggningssystem
- **`performance.py`** - Prestandaoptimering

#### **📁 templates/** - HTML-templates
- **`leads.html`** - Huvudtemplate för leads
- **`research.html`** - Forskningsfinansiering
- **`ollama.html`** - AI-modellhantering
- **`config.html`** - Konfigurationshantering
- **`research_results.html`** - Sökresultat
- **`ollama_models.html`** - Modellhantering UI
- **`search_form.html`** - Sökformulär

## 🎯 Funktioner och Ansvar

### **1. Lead Discovery & Management**

#### **Modul: `routes/leads.py`**
**Ansvar:** Lead-hantering och visning
- **`show_leads()`** - Visa alla leads med sökgränssnitt
- **`export_to_excel()`** - Exportera leads till Excel
- **`download_links()`** - Ladda ner innehåll från länkar
- **`delete_lead()`** - Ta bort specifik lead
- **`leads_by_source()`** - Filtrera leads per källa

#### **Modul: `models/database.py`**
**Ansvar:** Databasoperationer
- **`get_all_leads()`** - Hämta alla leads
- **`save_lead()`** - Spara ny lead
- **`delete_lead()`** - Ta bort lead
- **`get_leads_by_source()`** - Filtrera per källa
- **`get_search_history()`** - Sökhistorik

### **2. Sökfunktionalitet**

#### **Modul: `routes/search.py`**
**Ansvar:** Sökkoordinering
- **`perform_search()`** - Utför sökning över valda källor
- **`search_form()`** - Visa sökformulär

#### **Modul: `services/serp_service.py`**
**Ansvar:** Sök-API integration
- **`search()`** - Sök via SerpAPI (Google, Bing, DuckDuckGo)
- **`extract_text()`** - Extrahera text från webbsidor

#### **Modul: `services/pubmed_service.py`**
**Ansvar:** PubMed-integration (placeholder)
- **`search_articles()`** - Sök akademiska artiklar
- **`get_article_details()`** - Hämta artikel-detaljer

#### **Modul: `services/orcid_service.py`**
**Ansvar:** ORCID-integration (placeholder)
- **`search_researchers()`** - Sök forskarprofiler
- **`get_researcher_details()`** - Hämta forskar-detaljer

### **3. AI-integration**

#### **Modul: `routes/ollama.py`**
**Ansvar:** AI-modellhantering
- **`check_ollama()`** - Kontrollera Ollama-status
- **`ollama_status()`** - Hämta status som JSON
- **`ollama_models()`** - Lista tillgängliga modeller
- **`ollama_models_ui()`** - Modellhanteringsgränssnitt
- **`set_model()`** - Sätt prefererad modell

#### **Modul: `services/ollama_service.py`**
**Ansvar:** AI-analys
- **`analyze_relevance()`** - Analysera relevans
- **`check_status()`** - Kontrollera server-status
- **`get_available_models()`** - Hämta tillgängliga modeller
- **`set_preferred_model()`** - Sätt prefererad modell

### **4. Forskningsfinansiering**

#### **Modul: `routes/research.py`**
**Ansvar:** Forskningsfinansiering UI
- **`research_home()`** - Huvudgränssnitt
- **`search_research()`** - Sök forskningsprojekt
- **`api_search()`** - API-endpoint för sökning
- **`project_details()`** - Projekt-detaljer
- **`api_status()`** - API-status
- **`search_with_filters()`** - Avancerad filtrering

#### **Modul: `services/research_service.py`**
**Ansvar:** Forskningsfinansiering APIs
- **`get_all_projects()`** - Hämta projekt från alla APIs
- **`get_available_apis()`** - Lista tillgängliga APIs
- **`get_api_status()`** - Kontrollera API-status
- **`get_project_details()`** - Hämta projekt-detaljer

#### **Modul: `services/swecris_api.py`**
**Ansvar:** SweCRIS API
- **`search_projects()`** - Sök svenska forskningsprojekt
- **`get_project()`** - Hämta specifikt projekt
- **`check_health()`** - Kontrollera API-hälsa

### **5. Konfigurationshantering**

#### **Modul: `routes/config.py`**
**Ansvar:** Konfigurationsgränssnitt
- **`config_home()`** - Visa konfigurationsgränssnitt
- **`update_config()`** - Uppdatera konfiguration
- **`bulk_update_config()`** - Bulk-uppdatering
- **`test_config()`** - Testa API-nycklar
- **`config_status()`** - Konfigurationsstatus

#### **Modul: `models/config.py`**
**Ansvar:** Konfigurationsmodell
- **`ConfigManager`** - Hantera konfigurationer
- **`get_config()`** - Hämta konfiguration
- **`set_config()`** - Sätt konfiguration
- **`delete_config()`** - Ta bort konfiguration

### **6. Hjälpfunktioner**

#### **Modul: `utils/logger.py`**
**Ansvar:** Loggningssystem
- **`get_logger()`** - Skapa logger-instans
- **`setup_logging()`** - Konfigurera loggning

#### **Modul: `utils/performance.py`**
**Ansvar:** Prestandaoptimering
- **`get_session()`** - Optimerad HTTP-session
- **`DatabaseConnection`** - Databas-connection manager
- **`OptimizedSession`** - Connection pooling

## 🔧 Konfiguration och Miljövariabler

### **Obligatoriska miljövariabler:**
```bash
SERPAPI_KEY=your_serpapi_key_here
FLASK_SECRET_KEY=your-secret-key-here
```

### **Valfria miljövariabler:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TIMEOUT=30
MAX_TEXT_LENGTH=1000
REQUEST_TIMEOUT=10
EXPORT_FOLDER=exports
SCIHUB_FOLDER=scihub
```

## 📊 Databasstruktur

### **Tabeller:**
- **`leads`** - Lead-information (id, title, description, link, ai_summary, source, created_at)
- **`search_history`** - Sökhistorik (id, query, research_question, engines, results_count, created_at)
- **`config`** - Konfigurationer (key, value, description, is_secret)

## 🚀 Deployment och Drift

### **Krav:**
- Python 3.8+
- Ollama-server (lokalt)
- SerpAPI-nyckel
- SQLite-databas

### **Start:**
```bash
# Installera beroenden
pip install -r requirements.txt

# Konfigurera miljövariabler
cp env.example .env
# Redigera .env med dina API-nycklar

# Starta Ollama
ollama serve

# Starta applikationen
python app.py
```

## 🔍 Status och Problem

### **Fungerande funktioner:**
✅ Lead-hantering och visning  
✅ Excel-export  
✅ AI-integration (Ollama)  
✅ Konfigurationshantering  
✅ Forskningsfinansiering (SweCRIS)  
✅ Sökfunktionalitet (SerpAPI)  
✅ Loggningssystem  
✅ Prestandaoptimering  

### **Problem som behöver åtgärdas:**
❌ **SerpAPI-nyckel saknas** - Sökningar returnerar 0 resultat  
❌ **Ollama timeout** - AI-analys tar för lång tid  
❌ **Template-fel** - Null-värden i templates  
❌ **PubMed/ORCID** - Placeholder-implementationer  
❌ **Nätverksproblem** - SweCRIS API når inte servern  

### **Förbättringar som behövs:**
🔄 **Timeout-optimering** - Minska AI-analystid  
🔄 **Felhantering** - Bättre error handling  
🔄 **Caching** - Implementera caching  
🔄 **Rate limiting** - API-rate limiting  
🔄 **Monitoring** - Prestandaövervakning  

## 📈 Framtida Utveckling

### **Planerade funktioner:**
- **PubMed-integration** - Akademiska artiklar
- **ORCID-integration** - Forskareprofiler
- **Google Trends** - Trendanalys
- **Avancerad filtrering** - Mer sofistikerad sökning
- **API-endpoints** - RESTful API
- **Batch-processing** - Stora datasets

### **Tekniska förbättringar:**
- **Async/await** - Bättre prestanda
- **Redis caching** - Snabbare sökningar
- **Docker** - Containerisering
- **CI/CD** - Automatiserad deployment
- **Monitoring** - Prestandaövervakning

## 🎯 Sammanfattning

LeadFinder är en omfattande plattform med modulär arkitektur som kombinerar:

1. **Lead Discovery** - Automatisk lead-upptäckt via flera sökkällor
2. **AI-analys** - Intelligent relevansbedömning med Ollama
3. **Forskningsfinansiering** - Sökning i forskningsfinansiering-databaser
4. **Lead Management** - Komplett hantering av leads med export
5. **Konfigurationshantering** - Flexibel konfiguration av API-nycklar

Projektet har genomgått en omfattande refaktorering och är nu redo för produktion, men kräver konfiguration av API-nycklar och optimering av timeout-inställningar för optimal prestanda. 