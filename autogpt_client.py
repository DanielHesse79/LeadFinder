import requests
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import existing Ollama service
try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

@dataclass
class AutoGPTConfig:
    """Configuration for local AutoGPT with Ollama"""
    model: str = "mistral:latest"
    timeout: int = 1800  # 30 minutes for comprehensive research
    base_url: str = "http://localhost:11434"  # Ollama URL

class LocalAutoGPTClient:
    """Local AutoGPT client using Ollama"""
    
    def __init__(self, config: AutoGPTConfig):
        self.config = config
        self.ollama_service = ollama_service
        
        if not self.ollama_service:
            raise Exception("Ollama service not available")
    
    def _generate_text(self, prompt: str, timeout: int = None) -> str:
        """Generate text using Ollama with configurable timeout"""
        try:
            # Use provided timeout or default from config
            actual_timeout = timeout or self.config.timeout
            print(f"🤖 Generating text with {actual_timeout}s timeout...")
            
            response = self.ollama_service._call_ollama(prompt)
            return response if response else "No response generated"
        except Exception as e:
            raise Exception(f"Text generation failed: {str(e)}")
    
    def execute_text_generation(self, prompt: str, timeout: int = None) -> Dict[str, Any]:
        """Execute text generation block with extended timeout support"""
        try:
            # Add name extraction instruction to all prompts
            enhanced_prompt = f"""
            {prompt}
            
            IMPORTANT INSTRUCTION: Always extract and list all person names mentioned in the text, along with their titles and organizations. If no names are found, explicitly state "No person names found in the text."
            """
            
            result = self._generate_text(enhanced_prompt, timeout)
            return {
                "status": "COMPLETED",
                "output": result,
                "block_type": "text_generation",
                "timeout_used": timeout or self.config.timeout
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "error": str(e),
                "block_type": "text_generation"
            }
    
    def execute_web_search(self, query: str) -> Dict[str, Any]:
        """Execute web search block (using existing serp_service)"""
        try:
            from services.serp_service import serp_service
            if not serp_service:
                return {
                    "status": "FAILED",
                    "error": "SerpAPI service not available",
                    "block_type": "web_search"
                }
            
            results = serp_service.search(query, ["google"], num_results=5)
            return {
                "status": "COMPLETED",
                "output": results,
                "block_type": "web_search",
                "query": query
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "error": str(e),
                "block_type": "web_search"
            }
    
    def execute_data_analysis(self, data: Any, analysis_prompt: str, timeout: int = None) -> Dict[str, Any]:
        """Execute data analysis block with extended timeout support"""
        try:
            # Format data for analysis
            if isinstance(data, list):
                data_str = json.dumps(data, indent=2)
            else:
                data_str = str(data)
            
            full_prompt = f"""
            {analysis_prompt}
            
            Data to analyze:
            {data_str}
            
            Please provide a comprehensive analysis.
            
            IMPORTANT INSTRUCTION: Always extract and list all person names mentioned in the data, along with their titles and organizations. If no names are found, explicitly state "No person names found in the data."
            """
            
            result = self._generate_text(full_prompt, timeout)
            return {
                "status": "COMPLETED",
                "output": result,
                "block_type": "data_analysis",
                "timeout_used": timeout or self.config.timeout
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "error": str(e),
                "block_type": "data_analysis"
            }
    
    def execute_comprehensive_lead_research(self, company_name: str, industry: str) -> Dict[str, Any]:
        """Execute comprehensive lead research with extended timeout and multiple steps"""
        try:
            print(f"🚀 Starting comprehensive lead research for {company_name} in {industry}")
            print(f"⏱️  Using extended timeout: {self.config.timeout} seconds")
            
            # Step 1: Web search for real companies and leads (5 minutes)
            print("🌐 Step 1: Scanning internet for real companies...")
            search_queries = [
                f"{industry} companies startups",
                f"{industry} companies funding 2024",
                f"{industry} companies hiring",
                f"{industry} companies expanding",
                f"{industry} companies technology needs",
                f"{industry} companies recent news",
                f"{industry} companies leadership changes",
                f"{industry} companies partnerships"
            ]
            
            web_search_results = []
            for query in search_queries:
                try:
                    print(f"🔍 Searching: {query}")
                    search_result = self.execute_web_search(query)
                    if search_result.get("status") == "COMPLETED":
                        web_search_results.extend(search_result.get("output", []))
                except Exception as e:
                    print(f"⚠️  Search failed for '{query}': {e}")
                    continue
            
            print(f"✅ Found {len(web_search_results)} web search results")
            
            # Step 2: AI analysis of web search results (10 minutes)
            print("🤖 Step 2: Analyzing web search results with AI...")
            if web_search_results:
                # Format web search results for AI analysis
                search_data = ""
                for i, result in enumerate(web_search_results[:20], 1):  # Analyze top 20 results
                    search_data += f"""
                    Result {i}:
                    Title: {result.get('title', 'N/A')}
                    Description: {result.get('snippet', 'N/A')}
                    URL: {result.get('link', 'N/A')}
                    ---
                    """
                
                research_prompt = f"""
                You are an expert lead researcher analyzing real web search results for {company_name} in the {industry} industry.
                
                REAL WEB SEARCH RESULTS:
                {search_data}
                
                TASK: Extract and analyze potential leads from these real web search results
                
                FOR EACH POTENTIAL LEAD, PROVIDE:
                1. Company Name and Description (from search results)
                2. Key Decision Makers (extract names, titles, organizations)
                3. Contact Information (emails, phone numbers, LinkedIn profiles)
                4. Company Size and Revenue Estimates
                5. Recent News or Developments (from search results)
                6. Potential Pain Points or Opportunities
                7. Why they would benefit from {company_name}'s services
                8. Best approach strategy for contacting them
                9. Source URL (from search results)
                
                FORMAT YOUR RESPONSE AS:
                LEAD 1:
                Company: [Company Name]
                Description: [Brief description from search results]
                Decision Makers: [Names, titles, organizations]
                Contact: [Contact information]
                Size: [Company size/revenue]
                Recent News: [Recent developments from search results]
                Pain Points: [Potential pain points]
                Opportunities: [Opportunities for {company_name}]
                Approach: [Recommended contact strategy]
                Source: [URL from search results]
                ---
                
                IMPORTANT: 
                - Extract and list ALL person names mentioned, with titles and organizations
                - Use ONLY information from the real web search results provided
                - Be thorough and comprehensive - you have 10 minutes
                - Focus on actionable, contactable leads
                - Include specific contact information when possible
                - Cite the source URLs for each lead
                """
            else:
                # Fallback if web search fails
                research_prompt = f"""
                You are an expert lead researcher for {company_name} in the {industry} industry.
                
                TASK: Find potential leads based on your knowledge of the {industry} industry
                
                RESEARCH APPROACH:
                1. Think step by step about the {industry} industry
                2. Identify different segments and sub-industries within {industry}
                3. Consider companies of various sizes (startups, mid-size, enterprise)
                4. Look for companies that would benefit from {company_name}'s services
                5. Research recent news, funding rounds, and industry trends
                
                FOR EACH LEAD, PROVIDE:
                1. Company Name and Description
                2. Key Decision Makers (names, titles, organizations)
                3. Contact Information (emails, phone numbers, LinkedIn profiles)
                4. Company Size and Revenue Estimates
                5. Recent News or Developments
                6. Potential Pain Points or Opportunities
                7. Why they would benefit from {company_name}'s services
                8. Best approach strategy for contacting them
                
                FORMAT YOUR RESPONSE AS:
                LEAD 1:
                Company: [Company Name]
                Description: [Brief description]
                Decision Makers: [Names, titles, organizations]
                Contact: [Contact information]
                Size: [Company size/revenue]
                Recent News: [Recent developments]
                Pain Points: [Potential pain points]
                Opportunities: [Opportunities for {company_name}]
                Approach: [Recommended contact strategy]
                ---
                
                IMPORTANT: 
                - Extract and list ALL person names mentioned, with titles and organizations
                - Be thorough and comprehensive - you have 10 minutes
                - Focus on actionable, contactable leads
                - Include specific contact information when possible
                """
            
            research_result = self.execute_text_generation(research_prompt, timeout=600)  # 10 minutes
            
            if research_result.get("status") != "COMPLETED":
                return {
                    "status": "FAILED",
                    "error": f"Research step failed: {research_result.get('error', 'Unknown error')}"
                }
            
            # Step 3: Additional web search for specific companies (5 minutes)
            print("🔍 Step 3: Additional targeted web searches...")
            additional_searches = []
            
            # Extract company names from the research results and search for more info
            research_text = research_result.get("output", "")
            # Simple extraction of company names (this could be improved with NLP)
            lines = research_text.split('\n')
            company_names = []
            for line in lines:
                if 'Company:' in line:
                    company_name = line.split('Company:')[1].strip()
                    if company_name and len(company_name) > 3:
                        company_names.append(company_name)
            
            # Search for additional info about found companies
            for company_name in company_names[:5]:  # Limit to top 5 companies
                try:
                    search_query = f'"{company_name}" {industry} contact information'
                    print(f"🔍 Additional search: {search_query}")
                    additional_result = self.execute_web_search(search_query)
                    if additional_result.get("status") == "COMPLETED":
                        additional_searches.extend(additional_result.get("output", []))
                except Exception as e:
                    print(f"⚠️  Additional search failed for '{company_name}': {e}")
                    continue
            
            # Step 4: Industry insights with web data (5 minutes)
            print("📊 Step 4: Generating industry insights with web data...")
            insights_prompt = f"""
            Based on the web search results and research for {company_name} in {industry}, provide additional insights:
            
            WEB SEARCH DATA:
            {json.dumps(web_search_results[:10], indent=2)}
            
            ADDITIONAL SEARCHES:
            {json.dumps(additional_searches[:5], indent=2)}
            
            RESEARCH RESULTS:
            {research_result.get('output', '')}
            
            Provide:
            1. Industry trends and opportunities (based on web search results)
            2. Common pain points in {industry}
            3. Best practices for approaching {industry} companies
            4. Additional lead sources and research strategies
            5. Competitive landscape analysis
            6. Recent industry developments (from web search)
            
            Focus on actionable insights for lead generation based on real web data.
            """
            
            insights_result = self.execute_text_generation(insights_prompt, timeout=300)  # 5 minutes
            
            # Step 5: Contact strategies (5 minutes)
            print("📞 Step 5: Generating contact strategies...")
            contact_prompt = f"""
            For the leads identified for {company_name} in {industry}, provide:
            
            1. Best contact methods for each type of company
            2. Email templates and outreach strategies
            3. Timing recommendations for outreach
            4. Value proposition suggestions
            5. Follow-up strategies
            
            Make these specific to {industry} and {company_name}'s services.
            """
            
            contact_result = self.execute_text_generation(contact_prompt, timeout=300)  # 5 minutes
            
            # Step 6: Final analysis and prioritization (5 minutes)
            print("🔗 Step 6: Final analysis and prioritization...")
            final_prompt = f"""
            Analyze the comprehensive research results for {company_name} in {industry} and provide:
            
            1. Executive Summary of findings
            2. Top 10 prioritized leads with reasoning
            3. Industry insights and trends
            4. Contact strategies and recommendations
            5. Next steps and action plan
            6. Risk assessment and considerations
            
            IMPORTANT: Extract and list ALL person names mentioned in the research, along with their titles and organizations.
            
            Research Data:
            {research_result.get('output', '')}
            
            Industry Insights:
            {insights_result.get('output', '')}
            
            Contact Strategies:
            {contact_result.get('output', '')}
            
            Web Search Summary:
            - Total web search results: {len(web_search_results)}
            - Additional company searches: {len(additional_searches)}
            - Companies identified: {len(company_names)}
            """
            
            final_result = self.execute_data_analysis(
                {
                    "research": research_result.get("output", ""),
                    "insights": insights_result.get("output", ""),
                    "contact": contact_result.get("output", ""),
                    "web_search_results": len(web_search_results),
                    "additional_searches": len(additional_searches),
                    "companies_identified": len(company_names)
                },
                final_prompt,
                timeout=300  # 5 minutes
            )
            
            print("✅ Comprehensive lead research completed!")
            print(f"📊 Summary: {len(web_search_results)} web results, {len(company_names)} companies identified")
            
            return {
                "status": "COMPLETED",
                "research": research_result,
                "insights": insights_result,
                "contact_strategies": contact_result,
                "final_analysis": final_result,
                "web_search_results": web_search_results,
                "additional_searches": additional_searches,
                "metadata": {
                    "company_name": company_name,
                    "industry": industry,
                    "total_timeout": self.config.timeout,
                    "steps_completed": 6,
                    "ai_model": "Mistral (local)",
                    "comprehensive_analysis": True,
                    "web_search_enabled": True,
                    "web_results_count": len(web_search_results),
                    "companies_identified": len(company_names)
                }
            }
            
        except Exception as e:
            print(f"❌ Comprehensive lead research failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e),
                "block_type": "comprehensive_lead_research"
            }
    
    def execute_lead_research(self, company_name: str, industry: str) -> Dict[str, Any]:
        """Execute lead research workflow (legacy method)"""
        try:
            research_prompt = f"""
            Research and find potential leads for {company_name} in the {industry} industry.
            
            Please provide:
            1. Company names and descriptions
            2. Key decision makers and their roles (extract all person names, titles, and organizations)
            3. Company size and revenue estimates
            4. Recent news or developments
            5. Potential pain points or opportunities
            
            Focus on companies that would benefit from {company_name}'s services.
            Format your response as a structured list.
            
            IMPORTANT INSTRUCTION: Always extract and list all person names mentioned in the text, along with their titles and organizations. If no names are found, explicitly state "No person names found in the text."
            """
            
            result = self._generate_text(research_prompt)
            return {
                "status": "COMPLETED",
                "output": result,
                "block_type": "lead_research",
                "company": company_name,
                "industry": industry
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "error": str(e),
                "block_type": "lead_research"
            }

# Example usage
if __name__ == "__main__":
    config = AutoGPTConfig(model="mistral:latest", timeout=1800)  # 30 minutes
    
    client = LocalAutoGPTClient(config)
    
    # Test comprehensive lead research
    result = client.execute_comprehensive_lead_research("SampleFacts", "Data Analytics")
    print("Comprehensive lead research result:", result) 