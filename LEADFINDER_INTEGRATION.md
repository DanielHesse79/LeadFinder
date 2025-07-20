# AutoGPT Platform Integration for Leadfinder App

## 🚀 Quick Start

Copy these files to your Leadfinder app directory and follow the setup instructions.

---

## 📁 Files to Copy

### 1. `autogpt_client.py` - Main API Client
```python
import requests
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class AutoGPTConfig:
    """Configuration for AutoGPT API connection"""
    base_url: str = "http://localhost:8000/external-api/v1"
    api_key: str = ""
    timeout: int = 30

class AutoGPTClient:
    """Client for interacting with AutoGPT Platform API"""
    
    def __init__(self, config: AutoGPTConfig):
        self.config = config
        self.headers = {
            "X-API-Key": config.api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to AutoGPT API"""
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=self.config.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=self.config.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def list_blocks(self) -> List[Dict]:
        """Get all available blocks"""
        return self._make_request("GET", "/blocks")
    
    def execute_block(self, block_id: str, input_data: Dict[str, Any]) -> Dict:
        """Execute a single block"""
        data = {"input_data": input_data}
        return self._make_request("POST", f"/blocks/{block_id}/execute", data)
    
    def execute_graph(self, graph_id: str, version: int, node_input: Dict[str, Any]) -> Dict:
        """Execute a graph workflow"""
        data = {"node_input": node_input}
        return self._make_request("POST", f"/graphs/{graph_id}/execute/{version}", data)
    
    def get_execution_results(self, graph_id: str, execution_id: str) -> Dict:
        """Get execution results"""
        return self._make_request("GET", f"/graphs/{graph_id}/executions/{execution_id}/results")
    
    def wait_for_completion(self, graph_id: str, execution_id: str, max_wait: int = 300) -> Dict:
        """Wait for graph execution to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            results = self.get_execution_results(graph_id, execution_id)
            
            if results["status"] == "COMPLETED":
                return results
            elif results["status"] == "FAILED":
                raise Exception(f"Graph execution failed: {results}")
            
            time.sleep(2)  # Poll every 2 seconds
        
        raise TimeoutError(f"Graph execution timed out after {max_wait} seconds")

# Example usage
if __name__ == "__main__":
    config = AutoGPTConfig(
        api_key="your_api_key_here"
    )
    
    client = AutoGPTClient(config)
    
    # List available blocks
    blocks = client.list_blocks()
    print("Available blocks:", [b["name"] for b in blocks])
```

### 2. `leadfinder_autogpt_integration.py` - Leadfinder-specific integration
```python
from autogpt_client import AutoGPTClient, AutoGPTConfig
from typing import List, Dict, Any
import json

class LeadfinderAutoGPTIntegration:
    """Integration class for Leadfinder app with AutoGPT"""
    
    def __init__(self, api_key: str):
        self.config = AutoGPTConfig(api_key=api_key)
        self.client = AutoGPTClient(self.config)
        
        # Common block IDs (you'll need to get these from the API)
        self.block_ids = {
            "text_generation": "text_generator",
            "web_search": "web_search",
            "email_finder": "email_finder",
            "linkedin_scraper": "linkedin_scraper",
            "data_analysis": "data_analyzer"
        }
    
    def generate_lead_research_prompt(self, company_name: str, industry: str) -> str:
        """Generate a prompt for lead research"""
        return f"""
        Research and find potential leads for {company_name} in the {industry} industry.
        
        Please provide:
        1. Company names and descriptions
        2. Key decision makers and their roles
        3. Contact information (emails, phone numbers)
        4. Company size and revenue estimates
        5. Recent news or developments
        6. Potential pain points or opportunities
        
        Focus on companies that would benefit from {company_name}'s services.
        """
    
    def research_leads(self, company_name: str, industry: str, graph_id: str = None) -> Dict[str, Any]:
        """Research leads using AutoGPT blocks"""
        
        # If you have a pre-built graph for lead research
        if graph_id:
            node_input = {
                "company_name": company_name,
                "industry": industry,
                "research_prompt": self.generate_lead_research_prompt(company_name, industry)
            }
            
            # Execute the graph
            result = self.client.execute_graph(graph_id, 1, node_input)
            execution_id = result["id"]
            
            # Wait for completion and get results
            results = self.client.wait_for_completion(graph_id, execution_id)
            return results
        
        # Otherwise, execute individual blocks
        else:
            # Step 1: Generate research prompt
            prompt_result = self.client.execute_block(
                self.block_ids["text_generation"],
                {"prompt": self.generate_lead_research_prompt(company_name, industry)}
            )
            
            # Step 2: Web search for companies
            search_result = self.client.execute_block(
                self.block_ids["web_search"],
                {"query": f"{industry} companies potential clients leads"}
            )
            
            # Step 3: Find email addresses
            email_result = self.client.execute_block(
                self.block_ids["email_finder"],
                {"company_names": search_result.get("results", [])}
            )
            
            return {
                "prompt": prompt_result,
                "search_results": search_result,
                "email_results": email_result
            }
    
    def analyze_lead_data(self, lead_data: List[Dict]) -> Dict[str, Any]:
        """Analyze lead data using AutoGPT"""
        
        analysis_prompt = f"""
        Analyze the following lead data and provide insights:
        
        {json.dumps(lead_data, indent=2)}
        
        Please provide:
        1. Lead scoring and prioritization
        2. Common patterns or trends
        3. Best contact strategies
        4. Potential objections or challenges
        5. Recommended next steps
        """
        
        return self.client.execute_block(
            self.block_ids["data_analysis"],
            {"data": lead_data, "analysis_prompt": analysis_prompt}
        )
    
    def find_contact_info(self, company_name: str, person_name: str = None) -> Dict[str, Any]:
        """Find contact information for a company or person"""
        
        if person_name:
            # Find specific person's contact info
            return self.client.execute_block(
                self.block_ids["email_finder"],
                {"company": company_name, "person": person_name}
            )
        else:
            # Find general company contact info
            return self.client.execute_block(
                self.block_ids["email_finder"],
                {"company": company_name}
            )

# Example usage in your Leadfinder app
def main():
    # Initialize integration
    integration = LeadfinderAutoGPTIntegration("your_api_key_here")
    
    # Research leads for a company
    results = integration.research_leads(
        company_name="TechCorp Solutions",
        industry="SaaS"
    )
    
    print("Lead research results:", json.dumps(results, indent=2))
    
    # Analyze the results
    analysis = integration.analyze_lead_data(results.get("output", []))
    print("Analysis:", json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main()
```

### 3. `requirements.txt` - Dependencies
```
requests>=2.31.0
dataclasses-json>=0.6.0
```

### 4. `.env.example` - Environment variables
```bash
# AutoGPT Platform Configuration
AUTOGPT_API_KEY=your_api_key_here
AUTOGPT_BASE_URL=http://localhost:8000/external-api/v1
AUTOGPT_TIMEOUT=30

# Leadfinder Configuration
LEADFINDER_DB_PATH=/path/to/your/database
LEADFINDER_API_PORT=3000
```

---

## 🛠️ Setup Instructions

### Step 1: Install Dependencies
```bash
cd /path/to/your/Leadfinder/app
pip install -r requirements.txt
```

### Step 2: Get API Key
```bash
# Create API key via curl (replace YOUR_AUTH_TOKEN)
curl -X POST http://localhost:8000/api/v1/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "name": "Leadfinder Integration",
    "permissions": ["READ_BLOCK", "EXECUTE_BLOCK", "EXECUTE_GRAPH", "READ_GRAPH"],
    "description": "API key for Leadfinder app integration"
  }'
```

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env with your API key and settings
```

### Step 4: Test Connection
```python
from autogpt_client import AutoGPTClient, AutoGPTConfig

config = AutoGPTConfig(api_key="your_api_key_here")
client = AutoGPTClient(config)

# Test by listing blocks
blocks = client.list_blocks()
print(f"Found {len(blocks)} available blocks")
```

---

## 🎯 Integration Examples

### Example 1: Lead Research Workflow
```python
from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration

integration = LeadfinderAutoGPTIntegration("your_api_key")

# Research leads for a company
results = integration.research_leads(
    company_name="Your Company",
    industry="Technology"
)

# Process results in your Leadfinder app
for lead in results.get("output", []):
    # Add to your database
    # Send to your CRM
    # Create follow-up tasks
    pass
```

### Example 2: Contact Information Finder
```python
# Find contact info for a specific person
contact_info = integration.find_contact_info(
    company_name="Target Company",
    person_name="John Doe"
)

# Use in your outreach campaigns
email = contact_info.get("email")
phone = contact_info.get("phone")
```

### Example 3: Lead Analysis
```python
# Analyze your existing lead data
analysis = integration.analyze_lead_data(your_lead_data)

# Use insights for better targeting
priority_leads = analysis.get("priority_leads", [])
contact_strategies = analysis.get("contact_strategies", [])
```

---

## 🔧 Customization

### Adding New Blocks
1. Check available blocks: `client.list_blocks()`
2. Find block ID for your use case
3. Add to `block_ids` in `LeadfinderAutoGPTIntegration`
4. Create new methods using the block

### Creating Custom Graphs
1. Use the AutoGPT platform UI to create workflows
2. Save the graph ID
3. Use `execute_graph()` with your custom graph

### Error Handling
```python
try:
    results = integration.research_leads("Company", "Industry")
except Exception as e:
    print(f"AutoGPT integration failed: {e}")
    # Fallback to your existing methods
```

---

## 📊 Monitoring and Logging

Add logging to track API usage:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In your integration methods
logger.info(f"Researching leads for {company_name}")
logger.info(f"Found {len(results)} leads")
```

---

## 🚀 Next Steps

1. **Copy the files** to your Leadfinder app
2. **Get an API key** from the AutoGPT platform
3. **Test the connection** with simple requests
4. **Integrate gradually** - start with one feature
5. **Monitor performance** and adjust as needed

The AutoGPT platform will handle the AI processing with your local Mistral 7B model, while your Leadfinder app focuses on lead management and business logic. 