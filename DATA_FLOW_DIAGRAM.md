# 🔄 LeadFinder Data Flow Diagram

## 📊 **Complete Data Journey Visualization**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    📥 DATA MINING PHASE                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🌐 **WEB SEARCH**                    🎓 **ACADEMIC RESEARCH**              💰 **FUNDING DISCOVERY**
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│  SerpAPI    │                    │Semantic     │                    │    NIH      │
│  Service    │                    │ Scholar     │                    │   Service   │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│  Web Search │                    │Research     │                    │  Funding    │
│   Results   │                    │ Papers      │                    │  Grants     │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     └───────────────────────────────┬───────┴───────────────────────┬───────────────┘
                                     │                               │
                                     ▼                               ▼
                            ┌─────────────────────────────────────────────────────┐
                            │              📋 RAW DATA COLLECTION               │
                            │  • Web search results                             │
                            │  • Academic papers                                │
                            │  • Funding opportunities                          │
                            │  • Researcher profiles                            │
                            │  • Market data                                   │
                            └─────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   🔄 DATA PROCESSING PHASE                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🧠 **AI ANALYSIS**                   🔍 **RAG PROCESSING**                  📊 **WORKFLOW PROCESSING**
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Ollama    │                    │   Vector    │                    │ 3-Phase     │
│   Service   │                    │   Store     │                    │ Workflow    │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   OpenAI    │                    │   RAG       │                    │ Data Input  │
│   Service   │                    │  Search     │                    │   Phase     │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│  RunPod     │                    │ Embedding   │                    │ Data Process│
│  Service    │                    │  Service    │                    │   Phase     │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     └───────────────────────────────┬───────┴───────────────────────┬───────────────┘
                                     │                               │
                                     ▼                               ▼
                            ┌─────────────────────────────────────────────────────┐
                            │            🧠 PROCESSED DATA ANALYSIS              │
                            │  • AI-generated insights                           │
                            │  • Context-aware search results                   │
                            │  • Structured workflow outputs                     │
                            │  • Enhanced researcher profiles                    │
                            │  • Market trend analysis                          │
                            └─────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   📤 DATA OUTPUT PHASE                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

📋 **LEAD MANAGEMENT**              📊 **REPORTING & ANALYTICS**           🎯 **STRATEGIC PLANNING**
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Leads     │                    │  Reports    │                    │ Strategic   │
│  Database   │                    │  Service    │                    │  Planning   │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│ Lead        │                    │ Dashboard   │                    │ Market      │
│ Workshop    │                    │ Analytics   │                    │ Research    │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│ Researcher  │                    │ Performance │                    │ Competitive │
│ Management  │                    │  Metrics    │                    │  Analysis   │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     └───────────────────────────────┬───────┴───────────────────────┬───────────────┘
                                     │                               │
                                     ▼                               ▼
                            ┌─────────────────────────────────────────────────────┐
                            │              📤 FINAL DATA OUTPUTS                 │
                            │  • Structured lead database                        │
                            │  • Comprehensive research reports                  │
                            │  • Strategic planning documents                    │
                            │  • Performance analytics dashboards                │
                            │  • Market opportunity assessments                  │
                            └─────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   💾 DATA STORAGE LAYER                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

🗄️ **DATABASE SYSTEMS**             🔑 **SECURITY & CONFIG**               📈 **ANALYTICS STORAGE**
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   SQLite    │                    │  Encrypted  │                    │ Analytics   │
│  Database   │                    │  API Keys   │                    │  Database   │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│  ChromaDB   │                    │  Audit      │                    │ Performance │
│ Vector Store│                    │  Logging    │                    │  Metrics    │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     ▼                                       ▼                                       ▼
┌─────────────┐                    ┌─────────────┐                    ┌─────────────┐
│   Redis     │                    │  Usage      │                    │ User        │
│   Cache     │                    │  Tracking   │                    │ Activity    │
└─────────────┘                    └─────────────┘                    └─────────────┘
     │                                       │                                       │
     └───────────────────────────────┬───────┴───────────────────────┬───────────────┘
                                     │                               │
                                     ▼                               ▼
                            ┌─────────────────────────────────────────────────────┐
                            │            🔒 SECURE DATA STORAGE                  │
                            │  • Encrypted API keys                             │
                            │  • Vector embeddings                              │
                            │  • Structured lead data                           │
                            │  • Audit trails                                   │
                            │  • Performance metrics                             │
                            └─────────────────────────────────────────────────────┘
```

## 🔄 **Detailed Data Flow Paths**

### **Path 1: Web Search → Lead Generation**
```
🌐 SerpAPI → 🔍 Web Search → 🧠 AI Analysis → 📋 Lead Database → 📊 Lead Reports
```

### **Path 2: Academic Research → RAG Analysis**
```
🎓 Semantic Scholar → 📄 Research Papers → 🔍 RAG Processing → 📊 Research Reports
```

### **Path 3: Funding Discovery → Strategic Planning**
```
💰 NIH/NSF → 🏛️ Funding Data → 📊 Market Analysis → 🎯 Strategic Plans
```

### **Path 4: Researcher Data → Enhanced Profiles**
```
👥 ORCID → 👤 Researcher Data → 🧠 AI Enhancement → 📊 Researcher Database
```

## 🎯 **Key Integration Points**

### **API Key Dependencies**
```
🔑 SerpAPI Key → 🌐 Web Search Functions
🔑 OpenAI Key → 🧠 AI Analysis Functions  
🔑 Semantic Scholar Key → 🎓 Research Functions
🔑 NIH/NSF Keys → 💰 Funding Functions
```

### **RAG System Flow**
```
📄 Document Input → 🔍 Embedding → 🗄️ Vector Store → 🔍 RAG Search → 📊 Contextual Output
```

### **Workflow Integration**
```
📥 Data Input → 🔄 Data Process → 📤 Data Output
   (Mining)       (Analysis)       (Reporting)
```

## 📊 **Performance Metrics**

### **System Capabilities**
- **Data Mining**: 8+ external APIs and services
- **Data Processing**: 3 AI engines (Ollama, OpenAI, RunPod)
- **Data Storage**: 3 database systems (SQLite, ChromaDB, Redis)
- **Data Output**: 5+ reporting and analytics systems
- **Workflow Management**: 3-phase data processing pipeline
- **Security**: Encrypted API key storage and audit logging

### **Key Features**
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