# 🤖 AutoGPT Integration for LeadFinder

## Overview

LeadFinder includes comprehensive AutoGPT integration using your local Ollama and Mistral setup. This provides AI-powered analysis and insights for lead research without requiring external APIs, with a dedicated control panel for monitoring and management.

## 🎯 Features

### 🤖 **AI-Powered Lead Analysis**
- **Enhanced Search**: Get intelligent analysis of search results
- **Lead Research**: Research potential leads for your company in specific industries
- **Individual Analysis**: Analyze specific leads with detailed insights
- **Funding Research**: AI-powered research for funding opportunities

### 🎛️ **AutoGPT Control Panel**
- **Real-time Status Monitoring**: Live status of AutoGPT functionality
- **Interactive Testing**: Test AI models and prompts directly
- **Text Analysis Tools**: Analyze text for lead relevance and company research
- **Research Automation**: Comprehensive lead discovery automation
- **Model Management**: Control and configure AI models

### 🔧 **Technical Features**
- **Local Processing**: Uses your local Mistral model via Ollama
- **No External APIs**: Everything runs locally for privacy and cost control
- **Configurable**: Easy to enable/disable and configure
- **Integrated**: Seamlessly integrated into existing LeadFinder workflows
- **Real-time Monitoring**: Live status updates and performance metrics

## 🚀 Quick Start

### 1. Access the Control Panel
Navigate to **AutoGPT Control** in the main navigation menu, or go directly to:
```
http://localhost:5050/autogpt/control
```

### 2. Check Status
The control panel shows:
- **Enabled/Disabled** status
- **Connection status** (Ready/Failed)
- **Current model** being used
- **Timeout settings**

### 3. Test Functionality
Use the **Test Connection** button to verify AutoGPT is working properly.

## 🔧 Configuration

### Environment Variables
```bash
# AutoGPT Configuration
AUTOGPT_ENABLED=True                    # Enable/disable AutoGPT
AUTOGPT_MODEL=mistral:latest           # Model to use (should match Ollama)
AUTOGPT_TIMEOUT=1800                   # Request timeout in seconds
```

### Ollama Requirements
- Ollama must be running: `ollama serve`
- Mistral model must be installed: `ollama pull mistral:latest`
- Ollama must be accessible at: `http://localhost:11434`

## 🎛️ Control Panel Features

### Status Monitoring
- **Real-time status** of AutoGPT functionality
- **Model information** and configuration
- **Connection health** checks
- **Performance metrics**

### Interactive Testing
- **Custom prompt testing** with different models
- **Response validation** and analysis
- **Model comparison** testing
- **Error diagnostics**

### Text Analysis
- **General Analysis**: Basic text analysis and insights
- **Lead Relevance**: Business opportunity assessment
- **Company Research**: Detailed company analysis
- **Custom Analysis**: User-defined analysis types

### Research Automation
- **Topic Research**: Comprehensive research on specific topics
- **Company Research**: Research for specific companies and industries
- **Lead Discovery**: Automated lead identification and analysis
- **Market Analysis**: Industry and market trend analysis

## 📋 Usage Examples

### 1. General Search with AI Analysis
1. Go to **General Search**
2. Check **"Enable AutoGPT Analysis"**
3. Enter your search terms
4. Get AI-enhanced results with insights and recommendations

### 2. Lead Research via Control Panel
1. Navigate to **AutoGPT Control**
2. Click **"Research Topic"**
3. Enter company name and target industry
4. Click **"Research"** for comprehensive analysis

### 3. Text Analysis
1. In **AutoGPT Control**, click **"Analyze Text"**
2. Enter text to analyze
3. Select analysis type (General, Lead Relevance, Company Research)
4. Choose AI model
5. Get detailed analysis results

### 4. Individual Lead Analysis
1. For leads without AI analysis, use the control panel
2. Copy lead information to the text analysis section
3. Select "Lead Relevance" analysis type
4. Get detailed insights including:
   - Relevance score (1-10)
   - Key insights and opportunities
   - Recommended approach
   - Risk assessment

### 5. Funding Research
1. Go to **Funding** page
2. Use the **"AutoGPT Funding Research"** section
3. Enter research area and institution
4. Get AI insights on funding opportunities

### 6. Lead Workshop Integration
1. Go to **Lead Workshop**
2. Use **"AutoGPT Enhanced Analysis"** for project analysis
3. Get intelligent insights for your lead projects

## 🔌 API Endpoints

### Status Endpoints
```bash
# Get AutoGPT status
GET /autogpt/status

# Response:
{
  "enabled": true,
  "status": "ready",
  "model": "mistral:latest",
  "last_test": "AutoGPT test completed successfully..."
}
```

### Testing Endpoints
```bash
# Test AutoGPT functionality
POST /autogpt/test
Content-Type: application/x-www-form-urlencoded

test_prompt=Hello, this is a test
model=mistral:latest

# Response:
{
  "success": true,
  "output": "Hello! This is a test response from AutoGPT...",
  "model": "mistral:latest",
  "message": "AutoGPT test completed successfully"
}
```

### Analysis Endpoints
```bash
# Analyze text
POST /autogpt/analyze
Content-Type: application/x-www-form-urlencoded

text=Company description to analyze...
analysis_type=lead_relevance
model=mistral:latest

# Response:
{
  "success": true,
  "analysis": "Detailed analysis of the text...",
  "analysis_type": "lead_relevance",
  "model": "mistral:latest"
}
```

### Research Endpoints
```bash
# Perform research
POST /autogpt/research
Content-Type: application/x-www-form-urlencoded

research_topic=AI in healthcare
company_name=YourCompany
industry=Healthcare
model=mistral:latest

# Response:
{
  "success": true,
  "research": "Comprehensive research results...",
  "topic": "AI in healthcare",
  "model": "mistral:latest"
}
```

## 🏥 Health Checks

### Startup Validation
The application automatically validates AutoGPT on startup:
```bash
python app.py
```

You should see:
```
✅ All required configurations are present
🤖 AutoGPT: Ready (Mistral + Ollama)
```

### Manual Health Check
Run the startup check script:
```bash
python startup_check.py
```

### Health Endpoint
Check AutoGPT status via API:
```bash
curl http://localhost:5050/health
```

Response includes AutoGPT status:
```json
{
  "status": "healthy",
  "database": "connected",
  "autogpt": "ready",
  "configuration": "valid"
}
```

### Control Panel Health Check
Use the **Refresh Status** button in the AutoGPT Control Panel for real-time status updates.

## 🔧 Troubleshooting

### AutoGPT Not Available
1. **Check Ollama**: Ensure Ollama is running
   ```bash
   ollama serve
   ```

2. **Check Model**: Ensure Mistral is installed
   ```bash
   ollama list
   ollama pull mistral:latest
   ```

3. **Check Connection**: Test Ollama connection
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Check Configuration**: Verify AutoGPT settings
   ```bash
   python startup_check.py
   ```

5. **Use Control Panel**: Check status via the AutoGPT Control Panel

### Performance Issues
- **Timeout**: Increase `AUTOGPT_TIMEOUT` for complex queries
- **Model Size**: Consider using a smaller model for faster responses
- **Memory**: Ensure sufficient RAM for Mistral model
- **Concurrent Requests**: Limit simultaneous AutoGPT requests

### Common Errors
- **"Ollama service not available"**: Start Ollama with `ollama serve`
- **"Model not found"**: Install Mistral with `ollama pull mistral:latest`
- **"Connection refused"**: Check Ollama is running on port 11434
- **"Timeout error"**: Increase timeout in configuration

### Control Panel Issues
- **Page not loading**: Check if the route is registered in app.py
- **Test failures**: Verify Ollama and model availability
- **Analysis errors**: Check input text format and length
- **Research timeouts**: Increase timeout for complex research

## 🔧 Advanced Configuration

### Custom Models
You can use different Ollama models:
```bash
# Set environment variable
export AUTOGPT_MODEL=llama2:latest

# Or configure in database via UI
```

### Disable AutoGPT
To disable AutoGPT integration:
```bash
export AUTOGPT_ENABLED=False
```

### Custom Timeouts
Adjust timeout for different use cases:
```bash
export AUTOGPT_TIMEOUT=3600  # 1 hour for complex analysis
```

### Model Switching
Switch models dynamically via the control panel:
1. Go to AutoGPT Control
2. Select different model in test/analysis forms
3. Test with new model
4. Update configuration if needed

## 🔗 Integration Points

### Search Routes
- `/search` - Enhanced search with AutoGPT analysis
- `/search_ajax` - AJAX search with AutoGPT
- `/analyze_lead` - Individual lead analysis
- `/research_leads` - Lead research for companies

### Control Panel Routes
- `/autogpt/control` - Main control panel interface
- `/autogpt/test` - Test AutoGPT functionality
- `/autogpt/analyze` - Text analysis endpoint
- `/autogpt/research` - Research automation endpoint
- `/autogpt/status` - Status monitoring endpoint

### Templates
- `templates/autogpt_control.html` - Control panel interface
- `templates/leads.html` - Main search interface with AutoGPT
- `templates/research.html` - Funding research with AutoGPT
- `templates/lead_workshop.html` - Project analysis with AutoGPT

### Services
- `autogpt_client.py` - Local AutoGPT client
- `leadfinder_autogpt_integration.py` - LeadFinder-specific integration
- `services/unified_search.py` - Unified search with AutoGPT
- `services/ollama_service.py` - Ollama service integration

## 🚀 Development

### Adding New AutoGPT Features
1. Extend `LocalAutoGPTClient` in `autogpt_client.py`
2. Add methods to `LeadfinderAutoGPTIntegration`
3. Create routes in `routes/autogpt_control.py`
4. Update templates with UI elements
5. Add configuration options

### Testing
```bash
# Test AutoGPT integration
python test_integration.py

# Test startup
python startup_check.py

# Test full application
python app.py

# Test control panel
curl http://localhost:5050/autogpt/status
```

### Debugging
1. Check application logs: `data/logs/leadfinder.log`
2. Use control panel for real-time testing
3. Monitor Ollama logs: `ollama logs`
4. Test individual components via API endpoints

## 📊 Performance Monitoring

### Metrics to Monitor
- **Response times** for AutoGPT requests
- **Success rates** for different analysis types
- **Model performance** comparisons
- **Resource usage** (CPU, memory)
- **Error rates** and types

### Optimization Tips
- **Use appropriate timeouts** for different operations
- **Cache analysis results** for repeated queries
- **Batch similar requests** when possible
- **Monitor model performance** and switch if needed
- **Optimize prompts** for better results

## 🔮 Future Enhancements

### Planned Features
- **Multi-model support**: Use different models for different tasks
- **Batch processing**: Analyze multiple leads simultaneously
- **Custom prompts**: Allow users to customize analysis prompts
- **Result caching**: Cache analysis results for performance
- **Export integration**: Include AutoGPT insights in exports
- **Advanced analytics**: Detailed performance and usage analytics
- **Model fine-tuning**: Custom model training for specific domains
- **API rate limiting**: Intelligent request throttling

### Integration Improvements
- **Webhook support**: Real-time notifications for analysis completion
- **External API integration**: Connect with external AI services
- **Advanced filtering**: AI-powered result filtering
- **Predictive analytics**: Lead scoring and prioritization
- **Automated workflows**: End-to-end lead processing automation

## 🆘 Support

For issues with AutoGPT integration:
1. Check the control panel status
2. Review the startup logs for error messages
3. Run `python startup_check.py` for diagnostics
4. Verify Ollama and Mistral are working correctly
5. Check the `/health` endpoint for status information
6. Test individual components via the control panel
7. Review application logs in `data/logs/`

## 📚 Related Documentation

- [Configuration Guide](CONFIGURATION.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Development Guide](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md) 