# Leadfinder – Hitta företag med AI

Detta proof-of-concept söker företag inom ett valt område (t.ex. "epigenetics pre-diabetes") via Google, analyserar resultaten med en lokal LLM (Ollama), och sparar leads i en SQLite-databas.

## Steg för steg

1. **Installera beroenden**
   ```bash
   pip install -r requirements.txt
   ```

2. **Skaffa SerpAPI-nyckel**
   - Registrera dig på https://serpapi.com/ och kopiera din API-nyckel.
   - Sätt miljövariabeln `SERPAPI_KEY` eller skriv in nyckeln direkt i scriptet.

3. **Starta Ollama**
   - Installera Ollama: https://ollama.com/
   - Ladda ner t.ex. Mistral-modellen:
     ```bash
     ollama run mistral
     ```
   - Se till att Ollama kör på `localhost:11434` (standard).

4. **Kör scriptet**
   ```bash
   python leadfinder.py
   ```

5. **Resultat**
   - Leads sparas i `leads.db` (SQLite).
   - Varje lead innehåller titel, beskrivning, länk och AI-genererad sammanfattning.

## Anpassning
- Ändra sökordet i `leadfinder.py` (variabeln `SEARCH_QUERY`) för att hitta andra typer av företag eller leads.

## Notering
- SerpAPI har gratis testkvot, men kan kräva betalning vid större volymer.
- Ollama och LLM-modellen måste vara igång för att AI-analysen ska fungera. 