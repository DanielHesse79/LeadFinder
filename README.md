# LeadFinder – AI-Powered Lead Discovery Platform

LeadFinder är en avancerad webbapplikation som automatiskt hittar och analyserar leads inom valda områden med hjälp av AI. Appen kombinerar flera sökkällor (Google, Bing, DuckDuckGo), använder lokal AI (Ollama) för analys, och erbjuder en komplett hantering av leads med export och nedladdning.

## 🚀 Funktioner

### **Sök & Analys**
- **Multi-source sökning** via SerpAPI (Google, Bing, DuckDuckGo)
- **AI-driven analys** med Ollama (Mistral, DeepSeek, etc.)
- **Intelligent filtrering** baserat på forskningsfrågor
- **Automatisk textextraktion** från webbsidor

### **Lead Management**
- **SQLite-databas** för persistent lagring
- **Excel-export** med klickbara länkar
- **Bulk-nedladdning** av länkars innehåll
- **Sökhistorik** och filtrering

### **AI Integration**
- **Dynamisk modellhantering** - automatiskt upptäcker tillgängliga modeller
- **Real-time status** för Ollama-server och modeller
- **Modellval via UI** - byt mellan olika AI-modeller
- **Intelligent fallback** - använder bästa tillgängliga modell

### **Webbgränssnitt**
- **Responsiv design** med Bootstrap
- **Real-time statusindikatorer**
- **Snygg modellhantering** med kortvy
- **Export-funktioner** med progress tracking

## 🛠 Installation

### **1. Klona och installera**
```bash
git clone <repository-url>
cd leadfinder
pip install -r requirements.txt
```

### **2. Konfigurera miljövariabler**
```bash
# Kopiera exempel-filen
cp env.example .env

# Redigera .env-filen med dina värden
nano .env
```

**Obligatoriska inställningar:**
```bash
# SerpAPI-nyckel (krävs)
SERPAPI_KEY=your_serpapi_key_here

# Ollama-inställningar
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Flask-inställningar
FLASK_SECRET_KEY=your-secret-key-here
```

### **3. Starta Ollama**
```bash
# Installera Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Ladda modeller
ollama pull mistral:latest
ollama pull deepseek-coder:latest

# Starta Ollama-server
ollama serve
```

### **4. Starta applikationen**
```bash
python app.py
```

Appen kommer att köra på `http://localhost:5050`

## 📁 Projektstruktur

```
leadfinder/
├── app.py                 # Huvudapplikation
├── config.py             # Konfiguration och konstanter
├── models/
│   ├── __init__.py
│   └── database.py       # Databasmodeller och funktioner
├── routes/
│   ├── __init__.py
│   ├── leads.py          # Lead-hantering routes
│   ├── search.py         # Sökfunktionalitet
│   └── ollama.py         # AI-modellhantering
├── services/
│   ├── __init__.py
│   ├── ollama_service.py # AI-integration
│   ├── serp_service.py   # Sök-API integration
│   ├── pubmed_service.py # PubMed integration (placeholder)
│   └── orcid_service.py  # ORCID integration (placeholder)
├── templates/
│   ├── leads.html        # Huvudtemplate
│   └── ollama_models.html # Modellhantering UI
└── requirements.txt      # Python-beroenden
```

## 🔧 Konfiguration

### **Sökparametrar**
- `DEFAULT_RESEARCH_QUESTION` - Standard forskningsfråga
- `SERP_ENGINES` - Tillgängliga sökmotorer
- `MAX_RESULTS` - Max antal resultat per sökning

### **AI-inställningar**
- `OLLAMA_URL` - Ollama API endpoint
- `OLLAMA_MODEL` - Prefererad modell (automatisk upptäckt)
- `OLLAMA_TIMEOUT` - Timeout för AI-anrop

### **Export-inställningar**
- `EXPORT_FOLDER` - Mapp för nedladdade filer
- `SCIHUB_FOLDER` - Mapp för PDF-nedladdningar

## 🎯 Användning

### **1. Huvudgränssnitt**
- Öppna `http://localhost:5050`
- Se status för Ollama och vald modell
- Bläddra bland befintliga leads

### **2. Sökning**
- Ange sökfråga (t.ex. "epigenetik pre-diabetes")
- Välj forskningsfråga för AI-analys
- Välj sökmotorer (Google, Bing, DuckDuckGo)
- Klicka "Sök" för att starta analys

### **3. Modellhantering**
- Klicka "Hantera Ollama Modeller"
- Se tillgängliga modeller
- Välj prefererad modell
- Kontrollera serverstatus

### **4. Export**
- **Excel-export**: Ladda ner alla leads med klickbara länkar
- **Bulk-nedladdning**: Ladda ner innehåll från alla länkar
- **PDF-nedladdning**: Ladda ner PDFs från DOIs via Sci-Hub

## 🔍 AI-analys

### **Relevansbedömning**
1. **Textextraktion** från webbsida
2. **Snabb relevanskontroll** ("JA"/"NEJ")
3. **Detaljerad analys** för relevanta leads
4. **Sammanfattning** med företagsnamn och kontaktinfo

### **Modellval**
- **Automatisk upptäckt** av tillgängliga modeller
- **Intelligent matchning** (exakt → partial → fallback)
- **Real-time status** för server och modeller
- **UI för modellhantering** med snygg design

## 📊 Databas

### **Tabeller**
- `leads` - Lead-information (titel, beskrivning, länk, AI-sammanfattning)
- `search_history` - Sökhistorik med resultat

### **Funktioner**
- CRUD-operationer för leads
- Sökhistorik och statistik
- Filtrering per källa
- Bulk-operationer

## 🚀 Framtida funktioner

### **Planerade tillägg**
- **PubMed-integration** för akademiska artiklar
- **ORCID-integration** för forskarprofiler
- **Google Trends** för trendanalys
- **Avancerad filtrering** och sortering
- **API-endpoints** för externa integrationer
- **Batch-processing** för stora datasets

### **Förbättringar**
- **Caching** för snabbare sökningar
- **Rate limiting** för API-anrop
- **Logging** och monitoring
- **Docker** containerisering
- **CI/CD** pipeline

## 🐛 Felsökning

### **Vanliga problem**

**Ollama inte tillgängligt:**
```bash
# Kontrollera att Ollama körs
curl http://localhost:11434/api/tags

# Starta Ollama om nödvändigt
ollama serve
```

**Modeller inte hittade:**
```bash
# Lista tillgängliga modeller
ollama list

# Ladda modell om den saknas
ollama pull mistral:latest
```

**SerpAPI-fel:**
- Kontrollera API-nyckel i miljövariabler
- Verifiera kvot och betalning på SerpAPI

## 📝 Licens

Detta projekt är utvecklat för intern användning och research.

## 🤝 Bidrag

För förslag och buggrapporter, skapa en issue eller pull request.

---

**LeadFinder** - AI-powered lead discovery made simple! 🎯 