# 🕷️ WebScraper Integration för Vetenskaplig Information

## Översikt

WebScraper-integrationen ger LeadFinder möjlighet att skrapa vetenskapligt innehåll från webbplatser och analysera det med AI. Den kombinerar Playwright för browser-automation, BeautifulSoup för innehållsextraktion och LangChain + LLM för intelligent analys.

## 🚀 Funktioner

### **WebScraper Service**
- **Playwright Integration**: Automatisk browser-kontroll för dynamiska webbplatser
- **BeautifulSoup**: Intelligent innehållsextraktion från HTML
- **Asynkron Bearbetning**: Samtidig skrapning av flera URLs
- **Innehållstyper**: Stöd för vetenskapliga artiklar, forskarprofiler och institutioner
- **Metadata-extraktion**: Automatisk identifiering av författare, DOI, nyckelord, etc.

### **LangChain Analyzer**
- **Strukturerad Data**: Extraktion av vetenskaplig information i strukturerad format
- **Relevansbedömning**: AI-driven bedömning av innehållets relevans
- **Insikter**: Automatisk generering av insikter och sammanfattningar
- **Flera Modeller**: Stöd för både Ollama (lokal) och RunPod (molnet)

## 📋 Installation

### 1. Installera Beroenden

```bash
# Installera Python-paket
pip install playwright langchain langchain-community pydantic

# Installera Playwright browsers
playwright install chromium
```

### 2. Konfiguration

Lägg till följande i din miljöfil (`env.development`):

```bash
# WebScraper Configuration
WEBSCRAPER_TIMEOUT=30000
WEBSCRAPER_MAX_CONTENT_LENGTH=50000
WEBSCRAPER_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# LangChain Configuration
LANGCHAIN_MODEL=mistral:latest
LANGCHAIN_CHUNK_SIZE=1000
LANGCHAIN_CHUNK_OVERLAP=200
```

## 🎯 Användning

### **Via Web Interface**

1. **Navigera till WebScraper**: Gå till `/webscraper`
2. **Ange URLs**: Lägg till URLs till vetenskapliga artiklar, forskarprofiler eller institutioner
3. **Välj Innehållstyp**: Välj mellan:
   - **Vetenskaplig artikel**: För research papers och publikationer
   - **Forskarprofil**: För forskarprofiler och CV:n
   - **Institution**: För universitet och forskningsinstitut
   - **Allmänt innehåll**: För generell webbinnehåll
4. **Konfigurera AI-analys**: Aktivera LangChain-analys för strukturerad data
5. **Starta Skrapning**: Klicka på "Starta Skrapning"

### **Via API**

#### Skrapa Enskilda URLs
```bash
curl -X POST "http://localhost:5051/webscraper/scrape" \
  -F "urls=https://example.com/paper1" \
  -F "content_type=scientific_paper" \
  -F "research_context=epigenetics research" \
  -F "use_ai_analysis=on"
```

#### Batch-skrapning
```bash
curl -X POST "http://localhost:5051/webscraper/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com/paper1", "https://example.com/paper2"],
    "content_types": ["scientific_paper", "research_profile"],
    "research_context": "epigenetics research",
    "use_ai_analysis": true
  }'
```

#### Analysera Skrapat Innehåll
```bash
curl -X POST "http://localhost:5051/webscraper/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Skrapat innehåll här...",
    "url": "https://example.com/paper1",
    "content_type": "scientific_paper",
    "research_context": "epigenetics research"
  }'
```

## 🔧 Teknisk Arkitektur

### **WebScraper Service**

```python
from services.webscraper_service import webscraper_service

# Skrapa enskild URL
result = await webscraper_service.scrape_url(
    url="https://example.com/paper",
    content_type="scientific_paper"
)

# Skrapa flera URLs samtidigt
results = await webscraper_service.scrape_multiple_urls(
    urls=["url1", "url2", "url3"],
    content_types=["scientific_paper", "research_profile", "institution"]
)
```

### **LangChain Analyzer**

```python
from services.langchain_analyzer import langchain_analyzer

# Analysera vetenskaplig artikel
analysis = langchain_analyzer.analyze_scientific_paper(
    content="Artikelinnehåll...",
    url="https://example.com/paper",
    research_context="epigenetics research"
)

# Analysera forskarprofil
analysis = langchain_analyzer.analyze_research_profile(
    content="Profilinnehåll...",
    url="https://example.com/profile",
    research_context="epigenetics research"
)
```

## 📊 Datastrukturer

### **ScrapedContent**
```python
@dataclass
class ScrapedContent:
    url: str                    # Käll-URL
    title: str                  # Sidtitel
    content: str                # Extraherat innehåll
    metadata: Dict[str, Any]    # Extraherad metadata
    html: str                   # Rå HTML
    timestamp: float            # Skrapningstidpunkt
    source_type: str            # Innehållstyp
```

### **ScientificPaper (LangChain)**
```python
class ScientificPaper(BaseModel):
    title: str                          # Artikeltitel
    authors: List[str]                  # Författare
    abstract: str                       # Abstract
    doi: Optional[str]                  # DOI
    publication_date: Optional[str]     # Publiceringsdatum
    keywords: List[str]                 # Nyckelord
    institution: Optional[str]          # Institution
    funding: Optional[str]              # Finansiering
    methodology: Optional[str]          # Metodologi
    results: Optional[str]              # Resultat
    conclusions: Optional[str]          # Slutsatser
    relevance_score: int                # Relevans (1-5)
    research_areas: List[str]           # Forskningsområden
    potential_collaborations: List[str] # Samarbetsmöjligheter
```

### **ResearchProfile (LangChain)**
```python
class ResearchProfile(BaseModel):
    name: str                           # Forskarnamn
    title: str                          # Professionell titel
    institution: str                    # Institution
    department: Optional[str]           # Avdelning
    research_interests: List[str]       # Forskningsintressen
    expertise: List[str]                # Expertisområden
    publications: List[str]             # Publikationer
    contact_info: Optional[str]         # Kontaktinformation
    collaboration_potential: str        # Samarbetspotential
    relevance_score: int                # Relevans (1-5)
```

## 🔄 Integration med Lead Workshop

WebScraper kan integreras med Lead Workshop för förbättrad analys:

1. **Skrapa Innehåll**: Använd WebScraper för att hämta detaljerad information
2. **AI-analys**: Använd LangChain för strukturerad analys
3. **Lead Workshop**: Importera resultaten för vidare bearbetning

### **Exempel Integration**
```python
# I Lead Workshop
from services.webscraper_service import webscraper_service
from services.langchain_analyzer import langchain_analyzer

# Skrapa lead-innehåll
scraping_result = await webscraper_service.scrape_url(lead_url, "scientific_paper")

if scraping_result.success:
    # Analysera med LangChain
    analysis = langchain_analyzer.analyze_scientific_paper(
        scraping_result.content.content,
        scraping_result.content.url,
        project_context
    )
    
    # Använd i Lead Workshop
    lead_data = {
        'title': analysis.structured_data.title,
        'authors': analysis.structured_data.authors,
        'relevance_score': analysis.structured_data.relevance_score,
        'insights': analysis.insights,
        'summary': analysis.summary
    }
```

## 🛠️ Konfiguration

### **WebScraper Inställningar**

```python
# I config.py
WEBSCRAPER_CONFIG = {
    'timeout': 30000,              # 30 sekunder timeout
    'max_content_length': 50000,   # 50KB max innehåll
    'user_agent': 'Mozilla/5.0...', # Browser user agent
    'retry_attempts': 3,           # Antal försök
    'retry_delay': 2               # Fördröjning mellan försök
}
```

### **LangChain Inställningar**

```python
# I config.py
LANGCHAIN_CONFIG = {
    'model': 'mistral:latest',     # LLM-modell
    'chunk_size': 1000,            # Text-chunk storlek
    'chunk_overlap': 200,          # Överlapp mellan chunks
    'temperature': 0.3,            # Kreativitet (0-1)
    'max_tokens': 2000             # Max tokens per svar
}
```

## 🔍 Felsökning

### **Vanliga Problem**

#### 1. "Playwright not available"
**Lösning**: Installera Playwright och browsers
```bash
pip install playwright
playwright install chromium
```

#### 2. "LangChain not available"
**Lösning**: Installera LangChain-paket
```bash
pip install langchain langchain-community pydantic
```

#### 3. "Browser initialization failed"
**Lösning**: Kontrollera system-beroenden
```bash
# Ubuntu/Debian
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1

# CentOS/RHEL
sudo yum install -y nss atk libdrm libxkbcommon libxcomposite libxdamage libxrandr mesa-libgbm libXScrnSaver
```

#### 4. "Content extraction failed"
**Lösning**: Kontrollera URL-tillgänglighet och innehållstyp
- Verifiera att URL:en är tillgänglig
- Kontrollera att innehållstypen matchar sidan
- Öka timeout-värdet om sidan laddar långsamt

### **Debugging**

Aktivera detaljerad loggning:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Kontrollera service-status:
```bash
curl http://localhost:5051/webscraper/status
```

Testa skrapning:
```bash
curl http://localhost:5051/webscraper/test
```

## 📈 Prestanda

### **Optimering**

1. **Samtidig Skrapning**: Använd `scrape_multiple_urls` för batch-bearbetning
2. **Innehållsfiltrering**: Begränsa innehållslängd med `max_content_length`
3. **Caching**: Implementera caching för återanvändning av skrapat innehåll
4. **Rate Limiting**: Lägg till fördröjningar mellan requests

### **Prestanda-mätningar**

- **Skrapning**: 2-10 sekunder per URL (beroende på sidstorlek)
- **AI-analys**: 5-30 sekunder per innehåll (beroende på modell)
- **Samtidig kapacitet**: 5-10 URLs samtidigt (beroende på systemresurser)

## 🔒 Säkerhet

### **Best Practices**

1. **Rate Limiting**: Begränsa antal requests per tidsenhet
2. **User Agent**: Använd realistisk user agent
3. **Respect Robots.txt**: Kontrollera robots.txt innan skrapning
4. **Error Handling**: Hantera fel gracefully
5. **Content Validation**: Validera skrapat innehåll

### **Säkerhetskonfiguration**

```python
WEBSCRAPER_SECURITY = {
    'respect_robots_txt': True,    # Respektera robots.txt
    'rate_limit': 10,              # Max requests per minut
    'user_agent': 'LeadFinder Bot', # Identifierbar user agent
    'timeout': 30000,              # Timeout för requests
    'max_redirects': 5             # Max omdirigeringar
}
```

## 🚀 Framtida Utveckling

### **Planerade Funktioner**

1. **Intelligent Skrapning**: AI-driven identifiering av relevant innehåll
2. **Schema.org Support**: Extraktion av strukturerad data från schema.org
3. **PDF Support**: Skrapning av PDF-dokument
4. **Social Media Integration**: Skrapning från sociala medier
5. **Real-time Monitoring**: Övervakning av webbplatser för nya innehåll
6. **Advanced Caching**: Smart caching med versioning
7. **Distributed Scraping**: Distribuerad skrapning för hög prestanda

### **API-utökningar**

- **Webhook Support**: Notifieringar vid nya innehåll
- **Scheduled Scraping**: Schemalagd skrapning
- **Content Monitoring**: Övervakning av specifika webbplatser
- **Export Formats**: Stöd för fler export-format

## 📚 Exempel

### **Komplett Exempel**

```python
import asyncio
from services.webscraper_service import webscraper_service
from services.langchain_analyzer import langchain_analyzer

async def analyze_scientific_papers():
    # URLs till vetenskapliga artiklar
    urls = [
        "https://example.com/paper1",
        "https://example.com/paper2",
        "https://example.com/paper3"
    ]
    
    # Skrapa innehåll
    scraping_results = await webscraper_service.scrape_multiple_urls(
        urls, 
        ["scientific_paper"] * len(urls)
    )
    
    # Analysera med LangChain
    for result in scraping_results:
        if result.success:
            analysis = langchain_analyzer.analyze_scientific_paper(
                result.content.content,
                result.content.url,
                "epigenetics research"
            )
            
            if analysis.success:
                print(f"Title: {analysis.structured_data.title}")
                print(f"Authors: {analysis.structured_data.authors}")
                print(f"Relevance: {analysis.structured_data.relevance_score}/5")
                print(f"Summary: {analysis.summary}")
                print("---")

# Kör analys
asyncio.run(analyze_scientific_papers())
```

Detta ger dig en komplett lösning för att skrapa och analysera vetenskapligt innehåll med modern AI-teknik! 