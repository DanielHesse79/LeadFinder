from autogpt_client import LocalAutoGPTClient, AutoGPTConfig
from typing import List, Dict, Any
import json
import time

class LeadfinderAutoGPTIntegration:
    """Integration class for Leadfinder app with local AutoGPT using Ollama"""
    
    def __init__(self, model: str = "mistral:latest"):
        self.config = AutoGPTConfig(model=model)
        self.client = LocalAutoGPTClient(self.config)
    
    def generate_comprehensive_lead_research_prompt(self, company_name: str, industry: str) -> str:
        """Generate a comprehensive prompt for thorough lead research"""
        return f"""
        You are an expert lead researcher with 30 minutes to conduct comprehensive research for {company_name} in the {industry} industry.
        
        TASK: Find at least 20-30 high-quality potential leads for {company_name}
        
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
        
        RESEARCH AREAS TO COVER:
        - Direct competitors in {industry}
        - Companies in related industries that could expand into {industry}
        - Startups and scale-ups in {industry}
        - Companies that recently received funding
        - Companies with recent leadership changes
        - Companies expanding or entering new markets
        - Companies with technology needs in {industry}
        
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
        - Be thorough and comprehensive - you have 30 minutes
        - Provide at least 20-30 detailed leads
        - Focus on actionable, contactable leads
        - Include specific contact information when possible
        """
    
    def research_leads(self, company_name: str, industry: str) -> Dict[str, Any]:
        """Research leads using local AutoGPT with extended time and comprehensive analysis"""
        
        try:
            print(f"🔍 Starting comprehensive lead research for {company_name} in {industry}")
            print(f"⏱️  This research will take up to 30 minutes for thorough analysis")
            
            # Use the new comprehensive lead research function
            result = self.client.execute_comprehensive_lead_research(company_name, industry)
            
            if result.get("status") == "COMPLETED":
                print("✅ Comprehensive lead research completed successfully!")
                return result
            else:
                print(f"❌ Comprehensive research failed: {result.get('error', 'Unknown error')}")
                return result
            
        except Exception as e:
            print(f"❌ Lead research failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    def generate_lead_research_prompt(self, company_name: str, industry: str) -> str:
        """Generate a prompt for lead research (legacy method)"""
        return f"""
        Research and find potential leads for {company_name} in the {industry} industry.
        
        Please provide:
        1. Company names and descriptions
        2. Key decision makers and their roles (extract all person names, titles, and organizations)
        3. Contact information (emails, phone numbers)
        4. Company size and revenue estimates
        5. Recent news or developments
        6. Potential pain points or opportunities
        
        IMPORTANT: Always extract and list all person names mentioned in the text, along with their titles and organizations.
        Focus on companies that would benefit from {company_name}'s services.
        """
    
    def analyze_lead_data(self, lead_data: List[Dict]) -> Dict[str, Any]:
        """Analyze lead data using local AutoGPT"""
        
        analysis_prompt = f"""
        Analyze the following lead data and provide insights:
        
        {json.dumps(lead_data, indent=2)}
        
        Please provide:
        1. Lead scoring and prioritization
        2. Common patterns or trends
        3. Best contact strategies
        4. Potential objections or challenges
        5. Recommended next steps
        6. All person names mentioned in the data (with titles and organizations)
        
        IMPORTANT: Always extract and list all person names mentioned in the text, along with their titles and organizations.
        """
        
        return self.client.execute_data_analysis(lead_data, analysis_prompt)
    
    def enhance_search_results(self, search_results: List[Dict], research_question: str) -> Dict[str, Any]:
        """Enhance search results with AI analysis"""
        
        try:
            # Format search results for analysis
            results_text = ""
            for i, result in enumerate(search_results[:5], 1):  # Analyze top 5 results
                results_text += f"""
                Result {i}:
                Title: {result.get('title', 'N/A')}
                Description: {result.get('snippet', 'N/A')}
                URL: {result.get('link', 'N/A')}
                ---
                """
            
            analysis_prompt = f"""
            Analyze these search results in relation to: {research_question}
            
            Search Results:
            {results_text}
            
            Please provide:
            1. Relevance assessment for each result
            2. Key insights and patterns
            3. Potential leads or opportunities
            4. Recommended next steps
            5. Additional research suggestions
            6. All person names mentioned in the results (with titles and organizations)
            
            IMPORTANT: Always extract and list all person names mentioned in the text, along with their titles and organizations.
            """
            
            return self.client.execute_text_generation(analysis_prompt)
            
        except Exception as e:
            return {
                "status": "FAILED",
                "error": str(e)
            }
    
    def generate_lead_summary(self, lead_title: str, lead_description: str, research_question: str) -> Dict[str, Any]:
        """Generate a detailed summary for a specific lead"""
        
        summary_prompt = f"""
        Analyze this potential lead in relation to: {research_question}
        
        Lead Information:
        Title: {lead_title}
        Description: {lead_description}
        
        Please provide:
        1. Relevance score (1-10)
        2. Key insights about this lead
        3. Potential opportunities
        4. Recommended approach
        5. Risk assessment
        6. Next steps
        7. All person names mentioned in the text (with titles and organizations)
        
        IMPORTANT: Always extract and list all person names mentioned in the text, along with their titles and organizations.
        """
        
        return self.client.execute_text_generation(summary_prompt)

# Example usage in your Leadfinder app
def main():
    # Initialize integration
    integration = LeadfinderAutoGPTIntegration("mistral:latest")
    
    # Research leads for a company
    results = integration.research_leads(
        company_name="TechCorp Solutions",
        industry="SaaS"
    )
    
    print("Lead research results:", json.dumps(results, indent=2))
    
    # Analyze the results
    if results.get("status") == "COMPLETED":
        analysis = integration.analyze_lead_data(results.get("combined_data", {}))
        print("Analysis:", json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main() 