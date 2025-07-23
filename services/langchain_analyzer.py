"""
LangChain Analyzer Service for Scientific Content

This module provides LangChain integration for analyzing scraped scientific content
and extracting structured data using LLMs.
"""

import json
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    from langchain.output_parsers import PydanticOutputParser
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.chains.summarize import load_summarize_chain
    from langchain.chains.question_answering import load_qa_chain
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain import error: {e}")
    LANGCHAIN_AVAILABLE = False

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from services.runpod_service import runpod_service
except ImportError:
    runpod_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('langchain_analyzer')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

class ScientificPaper(BaseModel):
    """Structured data model for scientific papers"""
    title: str = Field(description="Title of the paper")
    authors: List[str] = Field(description="List of authors")
    abstract: str = Field(description="Abstract or summary")
    doi: Optional[str] = Field(description="DOI if available")
    publication_date: Optional[str] = Field(description="Publication date")
    keywords: List[str] = Field(description="Keywords or tags")
    institution: Optional[str] = Field(description="Institution or organization")
    funding: Optional[str] = Field(description="Funding information")
    methodology: Optional[str] = Field(description="Research methodology")
    results: Optional[str] = Field(description="Key results")
    conclusions: Optional[str] = Field(description="Conclusions")
    relevance_score: int = Field(description="Relevance score 1-5")
    research_areas: List[str] = Field(description="Research areas")
    potential_collaborations: List[str] = Field(description="Potential collaboration opportunities")

class ResearchProfile(BaseModel):
    """Structured data model for research profiles"""
    name: str = Field(description="Researcher name")
    title: str = Field(description="Professional title")
    institution: str = Field(description="Institution or organization")
    department: Optional[str] = Field(description="Department or division")
    research_interests: List[str] = Field(description="Research interests")
    expertise: List[str] = Field(description="Areas of expertise")
    publications: List[str] = Field(description="Key publications")
    contact_info: Optional[str] = Field(description="Contact information")
    collaboration_potential: str = Field(description="Collaboration potential assessment")
    relevance_score: int = Field(description="Relevance score 1-5")

class Institution(BaseModel):
    """Structured data model for institutions"""
    name: str = Field(description="Institution name")
    type: str = Field(description="Type of institution (university, research institute, etc.)")
    location: Optional[str] = Field(description="Location")
    research_areas: List[str] = Field(description="Research areas")
    departments: List[str] = Field(description="Departments or divisions")
    key_researchers: List[str] = Field(description="Key researchers")
    facilities: List[str] = Field(description="Research facilities")
    collaboration_opportunities: List[str] = Field(description="Collaboration opportunities")
    relevance_score: int = Field(description="Relevance score 1-5")

@dataclass
class AnalysisResult:
    """Result from LangChain analysis"""
    success: bool
    structured_data: Optional[Union[ScientificPaper, ResearchProfile, Institution]]
    summary: str
    insights: List[str]
    processing_time: float
    model_used: str
    error: Optional[str] = None

class LangChainAnalyzer:
    """
    Service for analyzing scientific content using LangChain and LLMs
    """
    
    def __init__(self, model_name: str = "mistral:latest"):
        self.model_name = model_name
        self.llm = None
        self.text_splitter = None
        self._initialized = False
        
        # Initialize text splitter
        if LANGCHAIN_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
        
        if logger:
            logger.info(f"LangChain analyzer initialized with model: {model_name}")
    
    def initialize(self) -> bool:
        """Initialize LangChain with LLM"""
        if not LANGCHAIN_AVAILABLE:
            if logger:
                logger.error("LangChain not available")
            return False
        
        try:
            # Try to use Ollama first
            if ollama_service and ollama_service.check_status().get('ok', False):
                self.llm = Ollama(model=self.model_name)
                self._initialized = True
                if logger:
                    logger.info(f"LangChain initialized with Ollama model: {self.model_name}")
                return True
            
            # Fallback to RunPod if available
            elif runpod_service and runpod_service.is_available():
                # Use RunPod through a custom wrapper
                self.llm = self._create_runpod_llm()
                self._initialized = True
                if logger:
                    logger.info(f"LangChain initialized with RunPod model")
                return True
            
            else:
                if logger:
                    logger.error("No LLM service available")
                return False
                
        except Exception as e:
            if logger:
                logger.error(f"Failed to initialize LangChain: {e}")
            return False
    
    def _create_runpod_llm(self):
        """Create a custom LLM wrapper for RunPod"""
        class RunPodLLM:
            def __init__(self, model_name: str):
                self.model_name = model_name
            
            def __call__(self, prompt: str) -> str:
                try:
                    result = runpod_service.analyze_lead({
                        'title': 'Analysis Request',
                        'description': prompt,
                        'link': '',
                        'source': 'langchain'
                    }, "Content analysis")
                    
                    if result.success:
                        return result.analysis
                    else:
                        return f"Analysis failed: {result.analysis}"
                except Exception as e:
                    return f"RunPod analysis error: {str(e)}"
        
        return RunPodLLM(self.model_name)
    
    def analyze_scientific_paper(self, content: str, url: str, research_context: str = "") -> AnalysisResult:
        """
        Analyze scientific paper content and extract structured data
        
        Args:
            content: Scraped content from the paper
            url: Source URL
            research_context: Research context for relevance scoring
            
        Returns:
            AnalysisResult with structured data and insights
        """
        start_time = time.time()
        
        if not self._initialized:
            success = self.initialize()
            if not success:
                return AnalysisResult(
                    success=False,
                    structured_data=None,
                    summary="LangChain not available",
                    insights=[],
                    processing_time=time.time() - start_time,
                    model_used="none",
                    error="Failed to initialize LangChain"
                )
        
        try:
            # Create document from content
            doc = Document(page_content=content, metadata={"source": url})
            
            # Split content if too long
            if len(content) > 4000:
                docs = self.text_splitter.split_documents([doc])
            else:
                docs = [doc]
            
            # Create analysis prompt
            analysis_prompt = self._create_scientific_paper_prompt(research_context)
            
            # Create LLM chain
            chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
            
            # Analyze content
            combined_content = " ".join([doc.page_content for doc in docs])
            result = chain.run(content=combined_content, context=research_context)
            
            # Parse structured data
            structured_data = self._parse_scientific_paper_result(result)
            
            # Generate summary
            summary = self._generate_summary(combined_content)
            
            # Extract insights
            insights = self._extract_insights(structured_data, research_context)
            
            processing_time = time.time() - start_time
            
            return AnalysisResult(
                success=True,
                structured_data=structured_data,
                summary=summary,
                insights=insights,
                processing_time=processing_time,
                model_used=self.model_name
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Analysis failed: {str(e)}"
            
            if logger:
                logger.error(error_msg)
            
            return AnalysisResult(
                success=False,
                structured_data=None,
                summary="Analysis failed",
                insights=[],
                processing_time=processing_time,
                model_used=self.model_name,
                error=error_msg
            )
    
    def analyze_research_profile(self, content: str, url: str, research_context: str = "") -> AnalysisResult:
        """
        Analyze research profile content and extract structured data
        """
        start_time = time.time()
        
        if not self._initialized:
            success = self.initialize()
            if not success:
                return AnalysisResult(
                    success=False,
                    structured_data=None,
                    summary="LangChain not available",
                    insights=[],
                    processing_time=time.time() - start_time,
                    model_used="none",
                    error="Failed to initialize LangChain"
                )
        
        try:
            # Create analysis prompt
            analysis_prompt = self._create_research_profile_prompt(research_context)
            
            # Create LLM chain
            chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
            
            # Analyze content
            result = chain.run(content=content, context=research_context)
            
            # Parse structured data
            structured_data = self._parse_research_profile_result(result)
            
            # Generate summary
            summary = self._generate_summary(content)
            
            # Extract insights
            insights = self._extract_profile_insights(structured_data, research_context)
            
            processing_time = time.time() - start_time
            
            return AnalysisResult(
                success=True,
                structured_data=structured_data,
                summary=summary,
                insights=insights,
                processing_time=processing_time,
                model_used=self.model_name
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Analysis failed: {str(e)}"
            
            if logger:
                logger.error(error_msg)
            
            return AnalysisResult(
                success=False,
                structured_data=None,
                summary="Analysis failed",
                insights=[],
                processing_time=processing_time,
                model_used=self.model_name,
                error=error_msg
            )
    
    def analyze_institution(self, content: str, url: str, research_context: str = "") -> AnalysisResult:
        """
        Analyze institution content and extract structured data
        """
        start_time = time.time()
        
        if not self._initialized:
            success = self.initialize()
            if not success:
                return AnalysisResult(
                    success=False,
                    structured_data=None,
                    summary="LangChain not available",
                    insights=[],
                    processing_time=time.time() - start_time,
                    model_used="none",
                    error="Failed to initialize LangChain"
                )
        
        try:
            # Create analysis prompt
            analysis_prompt = self._create_institution_prompt(research_context)
            
            # Create LLM chain
            chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
            
            # Analyze content
            result = chain.run(content=content, context=research_context)
            
            # Parse structured data
            structured_data = self._parse_institution_result(result)
            
            # Generate summary
            summary = self._generate_summary(content)
            
            # Extract insights
            insights = self._extract_institution_insights(structured_data, research_context)
            
            processing_time = time.time() - start_time
            
            return AnalysisResult(
                success=True,
                structured_data=structured_data,
                summary=summary,
                insights=insights,
                processing_time=processing_time,
                model_used=self.model_name
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Analysis failed: {str(e)}"
            
            if logger:
                logger.error(error_msg)
            
            return AnalysisResult(
                success=False,
                structured_data=None,
                summary="Analysis failed",
                insights=[],
                processing_time=processing_time,
                model_used=self.model_name,
                error=error_msg
            )
    
    def _create_scientific_paper_prompt(self, research_context: str) -> PromptTemplate:
        """Create prompt for scientific paper analysis"""
        template = """
        Analyze the following scientific paper content and extract structured information.
        
        Research Context: {context}
        
        Content:
        {content}
        
        Please provide a detailed analysis in the following JSON format:
        {{
            "title": "Paper title",
            "authors": ["Author 1", "Author 2"],
            "abstract": "Abstract or summary",
            "doi": "DOI if available",
            "publication_date": "Publication date",
            "keywords": ["keyword1", "keyword2"],
            "institution": "Institution or organization",
            "funding": "Funding information",
            "methodology": "Research methodology",
            "results": "Key results",
            "conclusions": "Conclusions",
            "relevance_score": 5,
            "research_areas": ["area1", "area2"],
            "potential_collaborations": ["collaboration1", "collaboration2"]
        }}
        
        Focus on extracting accurate information and assessing relevance to the research context.
        """
        
        return PromptTemplate(
            input_variables=["content", "context"],
            template=template
        )
    
    def _create_research_profile_prompt(self, research_context: str) -> PromptTemplate:
        """Create prompt for research profile analysis"""
        template = """
        Analyze the following research profile content and extract structured information.
        
        Research Context: {context}
        
        Content:
        {content}
        
        Please provide a detailed analysis in the following JSON format:
        {{
            "name": "Researcher name",
            "title": "Professional title",
            "institution": "Institution or organization",
            "department": "Department or division",
            "research_interests": ["interest1", "interest2"],
            "expertise": ["expertise1", "expertise2"],
            "publications": ["publication1", "publication2"],
            "contact_info": "Contact information",
            "collaboration_potential": "Assessment of collaboration potential",
            "relevance_score": 5
        }}
        
        Focus on identifying research interests, expertise, and collaboration potential.
        """
        
        return PromptTemplate(
            input_variables=["content", "context"],
            template=template
        )
    
    def _create_institution_prompt(self, research_context: str) -> PromptTemplate:
        """Create prompt for institution analysis"""
        template = """
        Analyze the following institution content and extract structured information.
        
        Research Context: {context}
        
        Content:
        {content}
        
        Please provide a detailed analysis in the following JSON format:
        {{
            "name": "Institution name",
            "type": "Type of institution",
            "location": "Location",
            "research_areas": ["area1", "area2"],
            "departments": ["dept1", "dept2"],
            "key_researchers": ["researcher1", "researcher2"],
            "facilities": ["facility1", "facility2"],
            "collaboration_opportunities": ["opportunity1", "opportunity2"],
            "relevance_score": 5
        }}
        
        Focus on identifying research capabilities and collaboration opportunities.
        """
        
        return PromptTemplate(
            input_variables=["content", "context"],
            template=template
        )
    
    def _parse_scientific_paper_result(self, result: str) -> ScientificPaper:
        """Parse LLM result into ScientificPaper object"""
        try:
            # Try to extract JSON from result
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = result[json_start:json_end]
                data = json.loads(json_str)
                
                return ScientificPaper(**data)
            else:
                # Fallback to creating basic structure
                return ScientificPaper(
                    title="Analysis Result",
                    authors=[],
                    abstract=result[:500],
                    keywords=[],
                    relevance_score=3,
                    research_areas=[],
                    potential_collaborations=[]
                )
                
        except Exception as e:
            if logger:
                logger.error(f"Failed to parse scientific paper result: {e}")
            
            # Return basic structure
            return ScientificPaper(
                title="Analysis Result",
                authors=[],
                abstract=result[:500],
                keywords=[],
                relevance_score=3,
                research_areas=[],
                potential_collaborations=[]
            )
    
    def _parse_research_profile_result(self, result: str) -> ResearchProfile:
        """Parse LLM result into ResearchProfile object"""
        try:
            # Try to extract JSON from result
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = result[json_start:json_end]
                data = json.loads(json_str)
                
                return ResearchProfile(**data)
            else:
                # Fallback to creating basic structure
                return ResearchProfile(
                    name="Researcher",
                    title="Unknown",
                    institution="Unknown",
                    research_interests=[],
                    expertise=[],
                    publications=[],
                    collaboration_potential="Unknown",
                    relevance_score=3
                )
                
        except Exception as e:
            if logger:
                logger.error(f"Failed to parse research profile result: {e}")
            
            # Return basic structure
            return ResearchProfile(
                name="Researcher",
                title="Unknown",
                institution="Unknown",
                research_interests=[],
                expertise=[],
                publications=[],
                collaboration_potential="Unknown",
                relevance_score=3
            )
    
    def _parse_institution_result(self, result: str) -> Institution:
        """Parse LLM result into Institution object"""
        try:
            # Try to extract JSON from result
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = result[json_start:json_end]
                data = json.loads(json_str)
                
                return Institution(**data)
            else:
                # Fallback to creating basic structure
                return Institution(
                    name="Institution",
                    type="Unknown",
                    research_areas=[],
                    departments=[],
                    key_researchers=[],
                    facilities=[],
                    collaboration_opportunities=[],
                    relevance_score=3
                )
                
        except Exception as e:
            if logger:
                logger.error(f"Failed to parse institution result: {e}")
            
            # Return basic structure
            return Institution(
                name="Institution",
                type="Unknown",
                research_areas=[],
                departments=[],
                key_researchers=[],
                facilities=[],
                collaboration_opportunities=[],
                relevance_score=3
            )
    
    def _generate_summary(self, content: str) -> str:
        """Generate a summary of the content"""
        try:
            if not self._initialized:
                return content[:200] + "..." if len(content) > 200 else content
            
            summary_prompt = PromptTemplate(
                input_variables=["content"],
                template="Summarize the following content in 2-3 sentences:\n\n{content}"
            )
            
            chain = LLMChain(llm=self.llm, prompt=summary_prompt)
            result = chain.run(content=content[:2000])  # Limit content length
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to generate summary: {e}")
            return content[:200] + "..." if len(content) > 200 else content
    
    def _extract_insights(self, structured_data: ScientificPaper, research_context: str) -> List[str]:
        """Extract insights from scientific paper analysis"""
        insights = []
        
        if structured_data.relevance_score >= 4:
            insights.append("High relevance to research context")
        
        if structured_data.potential_collaborations:
            insights.append(f"Potential collaborations: {', '.join(structured_data.potential_collaborations)}")
        
        if structured_data.research_areas:
            insights.append(f"Research areas: {', '.join(structured_data.research_areas)}")
        
        if structured_data.funding:
            insights.append(f"Funding information available: {structured_data.funding}")
        
        return insights
    
    def _extract_profile_insights(self, structured_data: ResearchProfile, research_context: str) -> List[str]:
        """Extract insights from research profile analysis"""
        insights = []
        
        if structured_data.relevance_score >= 4:
            insights.append("High relevance to research context")
        
        if structured_data.research_interests:
            insights.append(f"Research interests: {', '.join(structured_data.research_interests)}")
        
        if structured_data.expertise:
            insights.append(f"Areas of expertise: {', '.join(structured_data.expertise)}")
        
        if structured_data.collaboration_potential:
            insights.append(f"Collaboration potential: {structured_data.collaboration_potential}")
        
        return insights
    
    def _extract_institution_insights(self, structured_data: Institution, research_context: str) -> List[str]:
        """Extract insights from institution analysis"""
        insights = []
        
        if structured_data.relevance_score >= 4:
            insights.append("High relevance to research context")
        
        if structured_data.research_areas:
            insights.append(f"Research areas: {', '.join(structured_data.research_areas)}")
        
        if structured_data.collaboration_opportunities:
            insights.append(f"Collaboration opportunities: {', '.join(structured_data.collaboration_opportunities)}")
        
        if structured_data.facilities:
            insights.append(f"Research facilities: {', '.join(structured_data.facilities)}")
        
        return insights
    
    def is_available(self) -> bool:
        """Check if LangChain analyzer is available"""
        return LANGCHAIN_AVAILABLE and (ollama_service is not None or runpod_service is not None)
    
    def get_status(self) -> Dict[str, Any]:
        """Get LangChain analyzer status"""
        return {
            'available': self.is_available(),
            'langchain_available': LANGCHAIN_AVAILABLE,
            'ollama_available': ollama_service is not None,
            'runpod_available': runpod_service is not None,
            'initialized': self._initialized,
            'model': self.model_name
        }

# Global instance
langchain_analyzer = LangChainAnalyzer() 