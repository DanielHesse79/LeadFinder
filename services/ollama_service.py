import requests
import subprocess
import threading
import time
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, MAX_TEXT_LENGTH, REQUEST_TIMEOUT
from utils.logger import get_logger
from utils.performance import get_session

logger = get_logger('ollama_service')

class OllamaService:
    def __init__(self, url: str = OLLAMA_URL, preferred_model: str = OLLAMA_MODEL):
        self.url = url
        self.preferred_model = preferred_model
        self.available_models = []
        self.selected_model = None
        self.status = {"ok": False, "msg": "Ej kontrollerad"}
        self.session = get_session()
        self._load_models()
    
    def _load_models(self):
        """Load available models from Ollama API"""
        try:
            response = self.session.get(f"{self.url.replace('/api/generate', '')}/api/tags", timeout=3)
            if response.status_code == 200:
                tags = response.json().get("models", [])
                self.available_models = [tag["name"] for tag in tags]
                self._select_model()
                logger.info(f"Available models: {self.available_models}")
                logger.info(f"Selected model: {self.selected_model}")
                
                # Update status based on model selection
                if self.selected_model:
                    self.status = {"ok": True, "msg": f"Ollama och modell '{self.selected_model}' är redo."}
                else:
                    self.status = {"ok": False, "msg": "Ingen modell tillgänglig."}
            else:
                logger.warning(f"Could not fetch models: Status {response.status_code}")
                self.status = {"ok": False, "msg": f"Ollama svarar inte korrekt (Status {response.status_code})."}
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            self.status = {"ok": False, "msg": f"Ollama verkar inte vara igång: {str(e)}"}
    
    def _select_model(self):
        """Select the best available model based on preference"""
        if not self.available_models:
            self.selected_model = None
            return
        
        # First, try exact match
        for model in self.available_models:
            if model == self.preferred_model:
                self.selected_model = model
                return
        
        # Then, try partial match (e.g., "mistral" matches "mistral:latest")
        for model in self.available_models:
            if self.preferred_model in model:
                self.selected_model = model
                return
        
        # If no match, use first available model
        self.selected_model = self.available_models[0]
        logger.warning(f"Preferred model '{self.preferred_model}' not found, using '{self.selected_model}'")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.available_models.copy()
    
    def get_selected_model(self) -> Optional[str]:
        """Get currently selected model"""
        return self.selected_model
    
    def set_preferred_model(self, model_name: str):
        """Set preferred model and reload"""
        self.preferred_model = model_name
        self._load_models()
    
    def check_status(self) -> Dict[str, Any]:
        """
        Check if Ollama server and model are available
        
        Returns:
            Status dictionary with ok (bool) and msg (str)
        """
        # If we already have a valid status and models, return it
        if self.status.get("ok") and self.selected_model:
            return self.status
        
        try:
            response = self.session.get(f"{self.url.replace('/api/generate', '')}/api/tags", timeout=3)
            if response.status_code != 200:
                self.status = {"ok": False, "msg": "Ollama svarar inte korrekt."}
                return self.status
        except requests.exceptions.RequestException:
            self.status = {"ok": False, "msg": "Ollama verkar inte vara igång."}
            return self.status
        
        # Reload models and check if preferred model is available
        self._load_models()
        
        # Return current status (updated by _load_models)
        return self.status
    
    def fetch_full_text(self, url: str) -> str:
        """
        Fetch and extract text content from a URL
        
        Args:
            url: URL to fetch text from
            
        Returns:
            Extracted text content
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            full_text = ' '.join(p.get_text() for p in paragraphs)
            logger.info(f"Fetched {len(full_text)} characters from page")
            return full_text.strip().replace('\n', ' ')[:MAX_TEXT_LENGTH]
        except Exception as e:
            logger.error(f"Could not fetch text from page: {e}")
            return ""
    
    def analyze_relevance(self, title: str, snippet: str, link: str, research_question: str) -> Optional[str]:
        """
        Analyze if a lead is relevant using Ollama
        
        Args:
            title: Page title
            snippet: Page snippet
            link: Page URL
            research_question: Research question to check against
            
        Returns:
            AI summary if relevant, None if not relevant
        """
        if not self.selected_model:
            logger.warning("No model available for analysis")
            return None
        
        logger.info(f"Analyzing lead: {title} ({link})")
        page_text = self.fetch_full_text(link)
        
        if not page_text:
            logger.warning("No text extracted, skipping AI analysis")
            return None
        
        # Step 1: Quick relevance check
        relevance_prompt = f"""
Jag har hämtat följande text från en webbsida:
Titel: {title}
Länk: {link}
Text: {page_text}

Analysera detta. Handlar det om {research_question}?
Svara endast med "JA" om det är relevant, eller "NEJ" om det inte är relevant.
"""
        
        relevance_response = self._call_ollama(relevance_prompt)
        if not relevance_response:
            return None
        
        ai_response = relevance_response.strip().upper()
        logger.info(f"AI response: {ai_response}")
        
        if "JA" in ai_response:
            # Step 2: Detailed analysis if relevant
            detailed_prompt = f"""
Jag har hämtat följande text från en webbsida:
Titel: {title}
Länk: {link}
Text: {page_text}

Detta är relevant för {research_question}. Ge ett kort svar på svenska med: företagsnamn, varför det är relevant, samt ev. kontaktinfo.
"""
            detailed_response = self._call_ollama(detailed_prompt)
            return detailed_response.strip() if detailed_response else None
        
        return None  # Not relevant
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Make a call to Ollama API
        
        Args:
            prompt: Prompt to send to Ollama
            
        Returns:
            Response text or None if failed
        """
        payload = {
            "model": self.selected_model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = self.session.post(self.url, json=payload, timeout=OLLAMA_TIMEOUT)
            logger.debug(f"Ollama status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    return data["response"]
                else:
                    logger.warning("Response key missing from Ollama response")
                    return None
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def start_status_check(self):
        """Start status check in background thread"""
        def check_thread():
            self.check_status()
        
        t = threading.Thread(target=check_thread, daemon=True)
        t.start()

# Global service instance
ollama_service = OllamaService() 