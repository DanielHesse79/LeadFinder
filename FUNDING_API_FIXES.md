# Funding API Fixes - Från Mock till Riktig Data

## Problem

När du sökte efter funding så fick du **mock-resultat** istället för riktig data från forskningsfinansierings-API:erna. Detta hände eftersom:

1. **SweCRIS API** använde simulerad data istället för att ansluta till riktig API
2. **Andra API:er** (CORDIS, NIH, NSF) var inte implementerade
3. **Fallback-systemet** visade alltid mock-data när API:erna inte fungerade

## Lösningar Implementerade

### 1. **SweCRIS API - Riktig Anslutning**

**Före:**
```python
# Simulerad data för demonstration
self._mock_projects = self._generate_mock_projects()
```

**Efter:**
```python
# Riktig API-anslutning
response = self.session.get(f"{self.base_url}/projects", params=params, timeout=30)
```

**Fördelar:**
- ✅ Ansluter till riktig SweCRIS API
- ✅ Hämtar verklig forskningsdata
- ✅ Fallback till mock-data endast vid fel
- ✅ Bättre felhantering

### 2. **CORDIS API - EU Forskningsprojekt**

**Ny Implementation:**
- Ansluter till `https://cordis.europa.eu/api`
- Hämtar EU-finansierade forskningsprojekt
- Stöder sökning och projekt-detaljer
- Fallback till mock-data vid fel

### 3. **NIH RePORTER API - US Forskningsprojekt**

**Ny Implementation:**
- Ansluter till `https://api.reporter.nih.gov/v2`
- Hämtar NIH-finansierade projekt
- Stöder sökning och projekt-detaljer
- Fallback till mock-data vid fel

### 4. **NSF API - US National Science Foundation**

**Ny Implementation:**
- Ansluter till `https://api.nsf.gov/v1`
- Hämtar NSF-finansierade projekt
- Stöder sökning och projekt-detaljer
- Fallback till mock-data vid fel

## Konfiguration för Riktig Data

### 1. **API-nycklar Konfigurera**

Gå till `/config` och sätt följande API-nycklar:

```bash
# SweCRIS (Svenska forskningsrådet)
SWECRIS_API_KEY=din_riktiga_api_nyckel

# CORDIS (EU)
CORDIS_API_KEY=din_riktiga_api_nyckel

# NIH RePORTER (US)
NIH_API_KEY=din_riktiga_api_nyckel

# NSF (US)
NSF_API_KEY=din_riktiga_api_nyckel
```

### 2. **Aktivera API:er**

I konfigurationen kan du aktivera/inaktivera API:er:

```bash
SWECRIS_ENABLED=True
CORDIS_ENABLED=True
NIH_ENABLED=True
NSF_ENABLED=True
```

### 3. **Testa Anslutningar**

Varje API har en test-funktion:
- Gå till `/config`
- Klicka på "Testa" för varje API-nyckel
- Verifiera att anslutningen fungerar

## Så Här Fungerar Det Nu

### 1. **Sökning**
```python
# Riktig API-anrop
response = self.session.get(f"{self.base_url}/projects", params=params)

# Om API fungerar - riktig data
if response.status_code == 200:
    return self._parse_api_response(data)

# Om API misslyckas - fallback till mock
else:
    return self._fallback_search(query, max_results)
```

### 2. **Data-parsning**
```python
# Hanterar olika API-format
if 'projects' in data:
    items = data['projects']
elif 'results' in data:
    items = data['results']
elif isinstance(data, list):
    items = data
```

### 3. **Felhantering**
```python
# Graceful degradation
try:
    # Försök riktig API
    return self._real_api_call()
except Exception as e:
    # Fallback till mock med tydlig markering
    return self._fallback_with_warning()
```

## Förbättringar i Mock-Data

Även mock-data har förbättrats:

### **Före:**
```python
# Statisk mock-data
'title': 'Forskning om epigenetik och dess påverkan'
```

### **Efter:**
```python
# Dynamisk mock-data baserad på sökning
'title': f'Forskning om {title_term} - Mock Data'
'description': f'Detta är mock-data för sökningen "{query}". Riktig API-data skulle visas här.'
```

## Så Här Ser Du Skillnaden

### **Riktig Data:**
- ✅ Projekt-ID från riktig API
- ✅ Verkliga forskningsinstitutioner
- ✅ Riktiga belopp och valutor
- ✅ Korrekta datum och status
- ✅ Riktiga länkar till projekt

### **Mock Data:**
- ⚠️ Projekt-ID med "mock" prefix
- ⚠️ Generiska institutioner
- ⚠️ Slumpmässiga belopp
- ⚠️ Tydlig markering "Mock Data"

## Felsökning

### **Om Du Fortfarande Får Mock Data:**

1. **Kontrollera API-nycklar:**
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.swecris.se/v1/health
   ```

2. **Kontrollera nätverksanslutning:**
   ```bash
   ping api.swecris.se
   ```

3. **Kontrollera loggar:**
   ```bash
   tail -f leadfinder.log | grep "API error"
   ```

4. **Testa API-status:**
   - Gå till `/research`
   - Klicka på "API Status"
   - Se vilka API:er som fungerar

### **Vanliga Fel:**

```python
# Nätverksfel
"Cannot connect to SweCRIS API"

# API-nyckel fel
"API returned status 401"

# Timeout
"Request timeout after 30 seconds"
```

## Framtida Förbättringar

### **Planerade Funktioner:**
1. **Caching** - Spara API-resultat lokalt
2. **Rate Limiting** - Hantera API-begränsningar
3. **Batch Processing** - Sök flera API:er samtidigt
4. **Data Export** - Exportera till Excel/CSV
5. **Avancerad Filtrering** - Filtrera på belopp, datum, etc.

### **Fler API:er:**
- **Horizon Europe** - EU:s nya forskningsprogram
- **ERC** - European Research Council
- **Wellcome Trust** - Brittisk forskningsfinansiering
- **DFG** - Tysk forskningsfinansiering

## Sammanfattning

Nu ansluter LeadFinder till riktiga forskningsfinansierings-API:er och hämtar verklig data istället för mock-resultat. Systemet har:

- ✅ **Riktiga API-anslutningar** för alla stora forskningsfinansiärer
- ✅ **Smart fallback** som visar mock-data endast vid fel
- ✅ **Tydlig markering** av mock-data så du vet vad som är riktigt
- ✅ **Konfigurerbar** via webbgränssnittet
- ✅ **Robust felhantering** som aldrig kraschar

För att få riktig data, konfigurera dina API-nycklar i `/config` och testa anslutningarna! 