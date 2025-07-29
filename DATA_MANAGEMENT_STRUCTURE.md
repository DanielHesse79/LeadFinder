# 📊 LeadFinder Data Management Structure

## 🔄 **Complete Data Flow Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    LEADFINDER DATA ECOSYSTEM                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    📥 DATA MINING LAYER                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🔍 **SEARCH & DISCOVERY**
├── 🌐 Web Search (SerpAPI)
│   ├── routes/search.py
│   │   ├── search_web() → SerpAPI integration
│   │   ├── search_research() → Academic search
│   │   └── search_funding() → Funding opportunities
│   └── services/serpapi_service.py
│       ├── search_web_results()
│       ├── search_research_papers()
│       └── search_funding_opportunities()
│
├── 🎓 Academic Research
│   ├── services/semantic_scholar_service.py
│   │   ├── search_papers()
│   │   ├── get_paper_details()
│   │   └── get_author_profile()
│   ├── services/pubmed_service.py
│   │   ├── search_medical_research()
│   │   └── get_publication_details()
│   └── services/orcid_service.py
│       ├── search_researchers()
│       ├── get_researcher_profile()
│       └── get_enhanced_profile()
│
├── 💰 Funding Discovery
│   ├── services/nih_service.py
│   │   ├── search_grants()
│   │   └── get_grant_details()
│   ├── services/nsf_service.py
│   │   ├── search_funding()
│   │   └── get_project_details()
│   └── services/cordis_service.py
│       ├── search_eu_projects()
│       └── get_project_info()
│
└── 🔬 Research Data
    ├── services/swecris_service.py
    │   ├── search_swedish_research()
    │   └── get_researcher_data()
    └── services/fundnsf_service.py
        ├── search_nsf_funding()
        └── get_funding_details()

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   🔄 DATA PROCESSING LAYER                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🧠 **AI & ANALYSIS**
├── 🤖 AI Analysis
│   ├── services/ollama_service.py
│   │   ├── generate_text()
│   │   ├── analyze_content()
│   │   ├── batch_analyze_relevance()
│   │   └── generate_insights()
│   ├── services/openai_service.py
│   │   ├── analyze_with_gpt()
│   │   ├── generate_summaries()
│   │   └── extract_key_insights()
│   └── services/runpod_service.py
│       ├── analyze_lead()
│       ├── analyze_multiple_leads()
│       └── batch_process_data()
│
├── 🔍 RAG (Retrieval-Augmented Generation)
│   ├── services/rag_search_service.py
│   │   ├── search_with_context()
│   │   ├── generate_rag_response()
│   │   └── build_context_from_documents()
│   ├── services/vector_store_service.py
│   │   ├── upsert_documents()
│   │   ├── search_similar()
│   │   └── get_stats()
│   └── services/embedding_service.py
│       ├── generate_embeddings()
│       └── similarity_search()
│
├── 📊 Data Processing
│   ├── services/workflow_service.py
│   │   ├── DataWorkflow.process_data()
│   │   ├── DataProcessService._rag_analysis()
│   │   ├── DataProcessService._lead_analysis()
│   │   ├── DataProcessService._market_research()
│   │   └── DataProcessService._strategic_planning()
│   └── services/unified_search_service.py
│       ├── search()
│       ├── quick_search()
│       └── advanced_search()
│
└── 🔄 AutoGPT Integration
    ├── services/autogpt_service.py
    │   ├── run_research_task()
    │   ├── analyze_research_results()
    │   └── generate_research_report()
    └── routes/autogpt_control.py
        ├── start_research()
        ├── get_research_status()
        └── get_research_results()

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   📤 DATA OUTPUT LAYER                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

📋 **LEAD MANAGEMENT**
├── 🎯 Lead Processing
│   ├── models/database.py
│   │   ├── save_lead()
│   │   ├── get_all_leads()
│   │   ├── update_lead()
│   │   └── delete_lead()
│   └── routes/leads.py
│       ├── show_leads()
│       ├── add_lead()
│       └── edit_lead()
│
├── 🏭 Lead Workshop
│   ├── routes/lead_workshop.py
│   │   ├── create_project()
│   │   ├── analyze_lead()
│   │   └── get_project_analyses()
│   └── models/database.py
│       ├── create_project()
│       ├── save_lead_analysis()
│       └── get_project_analyses()
│
└── 👥 Researcher Management
    ├── models/database.py
    │   ├── save_researcher()
    │   ├── get_researcher()
    │   ├── update_researcher()
    │   └── remove_researcher()
    └── routes/researchers.py
        ├── search_researchers_route()
        ├── save_selected_researchers()
        └── enhance_researcher_data()

📊 **REPORTING & ANALYTICS**
├── 📈 Reports Generation
│   ├── routes/reports.py
│   │   ├── generate_lead_report()
│   │   ├── generate_research_report()
│   │   └── generate_funding_report()
│   └── services/reporting_service.py
│       ├── create_lead_analytics()
│       ├── generate_research_summary()
│       └── create_funding_analysis()
│
├── 🎯 Strategic Planning
│   ├── routes/strategic_planning.py
│   │   ├── strategic_analysis()
│   │   ├── market_research()
│   │   └── competitive_analysis()
│   └── services/strategic_service.py
│       ├── analyze_market_trends()
│       ├── identify_opportunities()
│       └── generate_strategic_recommendations()
│
└── 📊 Dashboard Analytics
    ├── routes/dashboard.py
    │   ├── dashboard_home()
    │   ├── get_dashboard_stats()
    │   └── get_lead_analytics()
    └── services/analytics_service.py
        ├── calculate_lead_metrics()
        ├── generate_performance_stats()
        └── create_visualization_data()

🔄 **WORKFLOW MANAGEMENT**
├── 📋 3-Phase Data Workflow
│   ├── routes/workflow.py
│   │   ├── data_input_phase()
│   │   ├── data_process_phase()
│   │   └── data_output_phase()
│   └── services/workflow_service.py
│       ├── DataWorkflow.process_data()
│       ├── DataProcessService.analyze_data()
│       └── DataOutputService.generate_reports()
│
├── 🔍 Unified Search
│   ├── routes/unified_search.py
│   │   ├── unified_search_form()
│   │   ├── perform_search()
│   │   └── get_search_results()
│   └── services/unified_search_service.py
│       ├── search()
│       ├── quick_search()
│       └── advanced_search()
│
└── 🤖 AutoGPT Control
    ├── routes/autogpt_control.py
    │   ├── start_research_task()
    │   ├── monitor_progress()
    │   └── get_results()
    └── services/autogpt_service.py
        ├── run_research_task()
        ├── analyze_results()
        └── generate_report()

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   💾 DATA STORAGE LAYER                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🗄️ **DATABASE MANAGEMENT**
├── 📊 Core Data Storage
│   ├── models/database.py
│   │   ├── leads table
│   │   ├── researchers table
│   │   ├── search_history table
│   │   ├── workshop_projects table
│   │   ├── workshop_analysis table
│   │   └── api_usage_log table
│   └── models/database_pool.py
│       ├── connection_pooling()
│       └── connection_management()
│
├── 🔍 RAG Data Storage
│   ├── models/database.py
│   │   ├── rag_chunks table
│   │   └── rag_search_sessions table
│   └── services/vector_store_service.py
│       ├── ChromaDB integration
│       ├── document_embeddings
│       └── similarity_search()
│
├── 🔑 API Key Management
│   ├── models/api_keys.py
│   │   ├── api_keys table
│   │   ├── api_services table
│   │   └── api_usage_log table
│   └── services/api_key_service.py
│       ├── encrypt_keys()
│       ├── decrypt_keys()
│       └── usage_tracking()
│
└── 📈 Analytics Storage
    ├── models/database.py
    │   ├── analytics_data table
    │   ├── performance_metrics table
    │   └── user_activity_log table
    └── services/analytics_service.py
        ├── store_metrics()
        ├── track_usage()
        └── generate_reports()

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   🔧 CONFIGURATION LAYER                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

⚙️ **SYSTEM CONFIGURATION**
├── 🔑 API Key Management
│   ├── routes/api_keys.py
│   │   ├── api_keys_dashboard()
│   │   ├── add_api_key()
│   │   ├── update_api_key()
│   │   └── test_api_key()
│   └── models/api_keys.py
│       ├── APIKeyManager
│       ├── encrypt_key()
│       └── decrypt_key()
│
├── ⚙️ System Configuration
│   ├── routes/config.py
│   │   ├── config_home()
│   │   ├── update_settings()
│   │   └── test_connections()
│   └── config.py
│       ├── load_config()
│       ├── validate_settings()
│       └── get_service_config()
│
└── 🔍 Service Integration
    ├── services/orcid_service.py
    ├── services/semantic_scholar_service.py
    ├── services/serpapi_service.py
    ├── services/openai_service.py
    ├── services/ollama_service.py
    └── services/runpod_service.py

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   📊 DATA FLOW SUMMARY                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🔄 **COMPLETE DATA JOURNEY**

1. 📥 **DATA MINING**
   ├── Web Search → SerpAPI → routes/search.py
   ├── Academic Research → Semantic Scholar → services/semantic_scholar_service.py
   ├── Funding Discovery → NIH/NSF → services/nih_service.py, services/nsf_service.py
   └── Researcher Data → ORCID → services/orcid_service.py

2. 🔄 **DATA PROCESSING**
   ├── AI Analysis → Ollama/OpenAI → services/ollama_service.py, services/openai_service.py
   ├── RAG Processing → Vector Store → services/rag_search_service.py, services/vector_store_service.py
   ├── Workflow Processing → 3-Phase System → services/workflow_service.py
   └── AutoGPT Research → AutoGPT → services/autogpt_service.py

3. 📤 **DATA OUTPUT**
   ├── Lead Management → Database → models/database.py, routes/leads.py
   ├── Research Reports → Analytics → routes/reports.py, services/reporting_service.py
   ├── Strategic Planning → Analysis → routes/strategic_planning.py, services/strategic_service.py
   └── Dashboard Analytics → Metrics → routes/dashboard.py, services/analytics_service.py

4. 💾 **DATA STORAGE**
   ├── Core Data → SQLite → models/database.py
   ├── RAG Data → ChromaDB → services/vector_store_service.py
   ├── API Keys → Encrypted SQLite → models/api_keys.py
   └── Analytics → Metrics Database → services/analytics_service.py

5. 🔧 **CONFIGURATION**
   ├── API Keys → Secure Management → routes/api_keys.py, models/api_keys.py
   ├── System Settings → Configuration → routes/config.py, config.py
   └── Service Integration → External APIs → Various service files

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   🎯 KEY INTEGRATION POINTS                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🔗 **CRITICAL CONNECTIONS**

1. **Search → Processing → Storage**
   ```
   SerpAPI → Ollama Analysis → Lead Database
   Semantic Scholar → RAG Processing → Vector Store
   ORCID → Enhanced Profiles → Researcher Database
   ```

2. **Workflow Integration**
   ```
   Data Input → Data Process → Data Output
   (Mining)    (Analysis)    (Reporting)
   ```

3. **API Key Dependencies**
   ```
   SerpAPI Key → Web Search Functions
   OpenAI Key → AI Analysis Functions
   Semantic Scholar Key → Research Functions
   ```

4. **RAG System Integration**
   ```
   Document Input → Embedding → Vector Store → RAG Search → Contextual Output
   ```

5. **AutoGPT Research Flow**
   ```
   Research Task → AutoGPT → Data Collection → Analysis → Report Generation
   ```

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   📈 PERFORMANCE METRICS                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

📊 **SYSTEM CAPABILITIES**

• **Data Mining**: 8+ external APIs and services
• **Data Processing**: 3 AI engines (Ollama, OpenAI, RunPod)
• **Data Storage**: 3 database systems (SQLite, ChromaDB, Redis)
• **Data Output**: 5+ reporting and analytics systems
• **Workflow Management**: 3-phase data processing pipeline
• **Security**: Encrypted API key storage and audit logging
• **Scalability**: Connection pooling and caching systems

🎯 **KEY FEATURES**

✅ **Comprehensive Data Mining**: Web, academic, funding, and researcher data
✅ **Advanced AI Processing**: Multiple AI engines for different analysis types
✅ **RAG Integration**: Context-aware search and analysis
✅ **Workflow Management**: Structured 3-phase data processing
✅ **Secure Storage**: Encrypted keys and comprehensive audit trails
✅ **Rich Reporting**: Multiple output formats and analytics
✅ **AutoGPT Research**: Automated research and analysis capabilities
✅ **Unified Search**: Single interface for all search functions
✅ **Strategic Planning**: Market analysis and opportunity identification
✅ **Real-time Analytics**: Live dashboard and performance metrics