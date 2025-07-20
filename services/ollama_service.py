import requests
import subprocess
import threading
import time
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, MAX_TEXT_LENGTH, REQUEST_TIMEOUT
from utils.logger import get_logger
from utils.performance import get_session

logger = get_logger('ollama_service')

class OllamaService:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.api_url = f"{self.base_url}/api/generate"
        self.tags_url = f"{self.base_url}/api/tags"
        self.selected_model = None
        self.available_models = []
        self.status = {"ok": False, "msg": "Not checked"}
        self.session = get_session()
        self._model_cache_time = 0
        self._cache_duration = 300  # 5 minutes cache
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available models, preferring smaller/faster ones"""
        # Check cache first
        if time.time() - self._model_cache_time < self._cache_duration and self.available_models:
            logger.debug("Using cached model list")
            return
        
        try:
            response = self.session.get(self.tags_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['name'] for model in data.get('models', [])]
                self._model_cache_time = time.time()
                logger.info(f"Available models: {self.available_models}")
                
                # Prefer mistral for general text analysis
                if 'mistral:latest' in self.available_models:
                    self.selected_model = 'mistral:latest'  # Better for text analysis
                elif 'deepseek-coder:latest' in self.available_models:
                    self.selected_model = 'deepseek-coder:latest'  # 1B model - faster but limited
                else:
                    self.selected_model = self.available_models[0] if self.available_models else None
                
                logger.info(f"Selected model: {self.selected_model}")
                
                # Update status based on model selection
                if self.selected_model:
                    self.status = {"ok": True, "msg": f"Ollama and model '{self.selected_model}' are ready."}
                else:
                    self.status = {"ok": False, "msg": "No model available."}
            else:
                logger.error(f"Failed to get models: {response.status_code}")
                self.status = {"ok": False, "msg": f"Ollama not responding correctly (Status {response.status_code})."}
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            self.status = {"ok": False, "msg": f"Ollama doesn't seem to be running: {str(e)}"}
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.available_models.copy()
    
    def get_selected_model(self) -> Optional[str]:
        """Get currently selected model"""
        return self.selected_model
    
    def set_preferred_model(self, model_name: str) -> bool:
        """
        Set preferred model if available
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            True if model was set successfully, False otherwise
        """
        if model_name in self.available_models:
            self.selected_model = model_name
            self.status = {"ok": True, "msg": f"Ollama and model '{self.selected_model}' are ready."}
            logger.info(f"Model set to: {self.selected_model}")
            return True
        else:
            logger.warning(f"Model '{model_name}' not available. Available: {self.available_models}")
            return False
    
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
            response = self.session.get(self.tags_url, timeout=3)
            if response.status_code != 200:
                self.status = {"ok": False, "msg": "Ollama not responding correctly."}
                return self.status
        except requests.exceptions.RequestException:
            self.status = {"ok": False, "msg": "Ollama doesn't seem to be running."}
            return self.status
        
        # Reload models and check if preferred model is available
        self._initialize_models()
        
        # Return current status (updated by _initialize_models)
        return self.status
    
    def fetch_full_text(self, url: str) -> str:
        """
        Fetch and extract text content from a URL with strict limits
        
        Args:
            url: URL to fetch text from
            
        Returns:
            Extracted text content (max 500 chars)
        """
        try:
            response = self.session.get(url, timeout=5)  # Shorter timeout
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text from paragraphs and headers
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            full_text = ' '.join(elem.get_text().strip() for elem in text_elements if elem.get_text().strip())
            
            # Very strict text length limit to avoid timeout
            max_length = 500  # Much shorter than before
            full_text = full_text[:max_length]
            
            logger.info(f"Fetched {len(full_text)} characters from page")
            return full_text.strip().replace('\n', ' ')
        except Exception as e:
            logger.error(f"Could not fetch text from page: {e}")
            return ""
    
    def analyze_relevance(self, title: str, snippet: str, link: str, research_question: str) -> Optional[str]:
        """
        Analyze if a lead is relevant using Ollama with a minimal, fast prompt
        
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
        
        # Try ultra-fast check first
        fast_result = self._ultra_fast_relevance_check(title, snippet, research_question)
        if fast_result is not None:
            return fast_result
        
        # Fallback to regular analysis if fast check fails
        prompt = f"""Q: {research_question}
T: {title}
S: {snippet}

Analyze this content and provide:
1. Relevance assessment (Yes/No)
2. All person names mentioned (with titles and organizations)
3. Brief summary if relevant

IMPORTANT: Always extract and list all person names mentioned in the text, along with their titles and organizations."""
        
        # Use retry logic for better reliability
        ai_response = self._call_ollama_with_retry(prompt)
        
        if ai_response:
            ai_response = ai_response.strip().lower()
            logger.info(f"AI full response: {ai_response}")
            
            # More robust parsing with multiple fallback strategies
            is_relevant = self._parse_relevance_response(ai_response)
            if is_relevant:
                logger.info(f"Lead relevant and research-based: {title}")
                return f"Relevant for {research_question}"
            else:
                logger.info("Lead not relevant or not research-based")
                return None
        else:
            logger.error("Failed to get AI response after retries")
            return None

    def _ultra_fast_relevance_check(self, title: str, snippet: str, research_question: str) -> Optional[str]:
        """
        Ultra-fast relevance check using minimal prompt
        
        Args:
            title: Page title
            snippet: Page snippet
            research_question: Research question
            
        Returns:
            Quick summary if relevant, None if not relevant or timeout
        """
        # Extract key terms from research question
        key_terms = research_question.lower().split()
        important_terms = [term for term in key_terms if len(term) > 3]
        
        # Check if key terms appear in title or snippet
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        
        # Count matches
        title_matches = sum(1 for term in important_terms if term in title_lower)
        snippet_matches = sum(1 for term in important_terms if term in snippet_lower)
        
        # If we have good keyword matches, do a very quick AI check
        if title_matches >= 1 or snippet_matches >= 2:
            # Ultra-minimal prompt with name extraction
            prompt = f"""Q: {research_question[:50]}...
T: {title[:100]}...

Quick check: Relevant? (Y/N) and list any person names found."""
            
            try:
                # Very short timeout for this check
                response = self._call_ollama(prompt)
                if response and 'y' in response.lower()[:10]:
                    return f"Relevant for {research_question} - Names: {response}"
            except:
                # If ultra-fast check fails, return None to trigger regular analysis
                pass
        
        return None

    def batch_analyze_relevance(self, leads: List[Dict[str, str]], research_question: str, max_batch_size: int = 5) -> List[Dict[str, str]]:
        """
        Analyze multiple leads in batches for better performance
        
        Args:
            leads: List of leads to analyze
            research_question: Research question to check against
            max_batch_size: Maximum number of leads to process in one batch
            
        Returns:
            List of relevant leads with AI summaries
        """
        if not self.selected_model:
            logger.warning("No model available, using keyword fallback")
            return self._keyword_fallback_analysis(leads, research_question)
        
        logger.info(f"Batch analyzing {len(leads)} leads")
        
        relevant_leads = []
        
        # Process in smaller batches for better performance
        for i in range(0, len(leads), max_batch_size):
            batch = leads[i:i + max_batch_size]
            logger.info(f"Processing batch {i//max_batch_size + 1}: {len(batch)} leads")
            
            # Try batch processing first
            batch_results = self._process_batch(batch, research_question)
            
            if batch_results:
                relevant_leads.extend(batch_results)
            else:
                # Fallback to individual processing if batch fails
                logger.info("Batch processing failed, falling back to individual analysis")
                individual_results = self._fallback_individual_analysis(batch, research_question)
                relevant_leads.extend(individual_results)
        
        logger.info(f"Batch analysis complete: {len(relevant_leads)} relevant leads found")
        return relevant_leads

    def _keyword_fallback_analysis(self, leads: List[Dict[str, str]], research_question: str) -> List[Dict[str, str]]:
        """
        Fallback analysis using keyword matching when AI is not available
        
        Args:
            leads: List of leads to analyze
            research_question: Research question to check against
            
        Returns:
            List of leads that match keywords
        """
        logger.info("Using keyword fallback analysis")
        
        # Extract key terms from research question
        key_terms = research_question.lower().split()
        important_terms = [term for term in key_terms if len(term) > 3]
        
        relevant_leads = []
        
        for lead in leads:
            title = lead.get('title', '').lower()
            snippet = lead.get('snippet', '').lower()
            
            # Count keyword matches
            title_matches = sum(1 for term in important_terms if term in title)
            snippet_matches = sum(1 for term in important_terms if term in snippet)
            
            # Consider relevant if we have good keyword matches
            if title_matches >= 1 or snippet_matches >= 2:
                lead_copy = lead.copy()
                lead_copy['ai_summary'] = f"Keyword match for {research_question}"
                relevant_leads.append(lead_copy)
        
        logger.info(f"Keyword analysis found {len(relevant_leads)} relevant leads")
        return relevant_leads

    def _process_batch(self, batch: List[Dict[str, str]], research_question: str) -> List[Dict[str, str]]:
        """
        Process a batch of leads with AI analysis
        
        Args:
            batch: List of leads to process
            research_question: Research question to check against
            
        Returns:
            List of relevant leads with AI summaries
        """
        relevant_leads = []
        
        for lead in batch:
            try:
                summary = self.analyze_relevance(
                    lead.get('title', ''),
                    lead.get('snippet', ''),
                    lead.get('link', ''),
                    research_question
                )
                if summary:
                    lead_copy = lead.copy()
                    lead_copy['ai_summary'] = summary
                    relevant_leads.append(lead_copy)
            except Exception as e:
                logger.error(f"Error analyzing lead {lead.get('title', 'Unknown')}: {e}")
                continue
        
        return relevant_leads

    def _fallback_individual_analysis(self, leads: List[Dict[str, str]], research_question: str) -> List[Dict[str, str]]:
        """Fallback to individual analysis if batch fails"""
        relevant_leads = []
        
        for lead in leads:
            summary = self.analyze_relevance(
                lead.get('title', ''),
                lead.get('snippet', ''),
                lead.get('link', ''),
                research_question
            )
            if summary:
                lead_copy = lead.copy()
                lead_copy['ai_summary'] = summary
                relevant_leads.append(lead_copy)
        
        return relevant_leads

    def _get_quick_summary(self, title: str, research_question: str) -> str:
        """Get a quick summary for a relevant lead"""
        summary_prompt = f"""Titel: {title}
Sammanfatta kort: företag, relevans för {research_question}"""
        
        summary_response = self._call_ollama(summary_prompt)
        return summary_response.strip() if summary_response else f"Relevant för {research_question}"
    
    def _parse_relevance_response(self, ai_response: str) -> bool:
        """
        Parse AI response to determine relevance with multiple fallback strategies
        
        Args:
            ai_response: Raw AI response text
            
        Returns:
            True if relevant, False otherwise
        """
        try:
            # Strategy 1: Check for both 'relevant' and 'context' with 'yes'
            if 'relevant' in ai_response and 'context' in ai_response:
                relevant_part = ai_response.split('relevant')[1]
                context_part = ai_response.split('context')[1]
                if 'yes' in relevant_part and 'yes' in context_part:
                    return True
            
            # Strategy 2: Simple yes/no check
            if 'yes' in ai_response and ('relevant' in ai_response or 'context' in ai_response):
                return True
            
            # Strategy 3: Check for positive indicators
            positive_indicators = ['relevant', 'yes', 'true', 'correct', 'match']
            negative_indicators = ['no', 'not', 'false', 'irrelevant', 'unrelated']
            
            positive_count = sum(1 for indicator in positive_indicators if indicator in ai_response)
            negative_count = sum(1 for indicator in negative_indicators if indicator in ai_response)
            
            if positive_count > negative_count:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error parsing AI response: {e}")
            return False
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Make a call to Ollama API with optimized timeout and parameters
        
        Args:
            prompt: Prompt to send to Ollama
            
        Returns:
            Response text or None if failed
        """
        payload = {
            "model": self.selected_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 50,  # Much shorter responses
                "top_k": 5,
                "top_p": 0.8,
                "repeat_penalty": 1.1,
                "num_ctx": 512  # Smaller context window
            }
        }
        
        try:
            # Use configurable timeout
            timeout = OLLAMA_TIMEOUT
            response = self.session.post(self.api_url, json=payload, timeout=timeout)
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
        except requests.exceptions.Timeout:
            logger.error(f"Ollama timeout after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def _call_ollama_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Call Ollama with retry logic and shorter timeout
        
        Args:
            prompt: The prompt to send to Ollama
            max_retries: Maximum number of retries
            
        Returns:
            AI response or None if failed
        """
        if not self.selected_model:
            logger.warning("No model selected for Ollama call")
            return None
        
        # Use longer timeout for comprehensive analysis
        timeout = min(int(OLLAMA_TIMEOUT), 180)  # Max 3 minutes for analysis
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Ollama call attempt {attempt + 1}/{max_retries}")
                
                # Shorter, more focused prompt for faster response
                if len(prompt) > 2000:
                    prompt = prompt[:2000] + "..."
                
                response = self.session.post(
                    self.api_url,
                    json={
                        "model": self.selected_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Lower temperature for more consistent output
                            "top_p": 0.9,
                            "num_predict": 500  # Limit response length
                        }
                    },
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get('response', '').strip()
                    
                    if ai_response:
                        logger.info(f"Ollama response received (attempt {attempt + 1})")
                        return ai_response
                    else:
                        logger.warning(f"Empty response from Ollama (attempt {attempt + 1})")
                else:
                    logger.error(f"Ollama API error: {response.status_code} (attempt {attempt + 1})")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Ollama timeout after {timeout} seconds (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    logger.error("Ollama timeout after all retries")
                    return None
            except Exception as e:
                logger.error(f"Ollama call error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None
            
            # Short delay before retry
            if attempt < max_retries - 1:
                time.sleep(1)
        
        logger.error("Failed to get AI response after retries")
        return None
    
    def start_status_check(self):
        """Start status check in background thread"""
        def check_thread():
            self.check_status()
        
        t = threading.Thread(target=check_thread, daemon=True)
        t.start()

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate service configuration and return detailed status
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            "service_available": False,
            "models_available": False,
            "selected_model": None,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if Ollama server is reachable
            response = self.session.get(self.tags_url, timeout=5)
            if response.status_code == 200:
                validation["service_available"] = True
            else:
                validation["errors"].append(f"Ollama server returned status {response.status_code}")
        except Exception as e:
            validation["errors"].append(f"Cannot connect to Ollama server: {e}")
            return validation
        
        # Check models
        if self.available_models:
            validation["models_available"] = True
            validation["selected_model"] = self.selected_model
            
            if not self.selected_model:
                validation["warnings"].append("No model selected")
        else:
            validation["errors"].append("No models available")
        
        return validation
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the service
        
        Returns:
            Health status dictionary
        """
        validation = self.validate_configuration()
        
        return {
            "healthy": validation["service_available"] and validation["models_available"],
            "service_status": "ok" if validation["service_available"] else "error",
            "models_status": "ok" if validation["models_available"] else "error",
            "selected_model": validation["selected_model"],
            "available_models_count": len(self.available_models),
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "cache_age": time.time() - self._model_cache_time if self._model_cache_time else None
        }

# Global service instance
ollama_service = OllamaService() 