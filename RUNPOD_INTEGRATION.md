# RunPod.ai Integration for Lead Workshop

## Overview

LeadFinder now includes integration with RunPod.ai to provide enhanced AI analysis capabilities in the Lead Workshop. This integration allows users to leverage more powerful cloud-based AI models for comprehensive lead analysis, offering better data extraction and insights compared to local Ollama models.

## Features

### Enhanced Analysis Capabilities
- **More Powerful Models**: Access to larger, more sophisticated AI models
- **Better Data Extraction**: Improved extraction of people, contacts, products, and company information
- **Comprehensive Analysis**: Detailed analysis with opportunities, concerns, and actionable insights
- **Faster Processing**: Cloud-based processing with dedicated GPU resources
- **Scalable**: Handle larger datasets and more complex analysis tasks

### Analysis Output
RunPod.ai analysis provides structured data including:
- **Relevancy Score**: 1-5 rating with detailed justification
- **People**: Names, titles, roles, organizations mentioned
- **Contact Information**: Emails, phones, social media profiles
- **Products**: Product names, technologies, services mentioned
- **Company Information**: Company details, size, industry, location
- **Opportunities**: Potential collaboration or business opportunities
- **Concerns**: Red flags, risks, or potential issues
- **Analysis**: Comprehensive analysis with actionable recommendations

## Setup Instructions

### 1. Create RunPod.ai Account
1. Visit [RunPod.ai](https://runpod.io) and create an account
2. Add payment method (RunPod uses pay-per-use pricing)
3. Navigate to the API Keys section and generate an API key

### 2. Deploy AI Model Endpoint
1. Go to the RunPod Cloud section
2. Choose a suitable AI model (recommended: Llama 2, Mistral, or GPT models)
3. Deploy the endpoint and note the endpoint ID
4. Ensure the endpoint is configured for text generation

### 3. Configure LeadFinder
1. Open LeadFinder configuration page (`/config`)
2. Add the following configuration values:
   - **RUNPOD_API_KEY**: Your RunPod API key
   - **RUNPOD_ENDPOINT_ID**: Your deployed endpoint ID (e.g., n5ljtp41xfy3oy)
   - **RUNPOD_BASE_URL**: `https://api.runpod.ai/v2` (default)
   - **RUNPOD_TIMEOUT**: `300` (5 minutes, default)
   - **RUNPOD_MAX_RETRIES**: `3` (default)
   - **RUNPOD_RETRY_DELAY**: `2` (seconds, default)

### 4. Environment Variables (Alternative)
You can also set these as environment variables:
```bash
export RUNPOD_API_KEY="your-api-key-here"
export RUNPOD_ENDPOINT_ID="n5ljtp41xfy3oy"
export RUNPOD_BASE_URL="https://api.runpod.ai/v2"
export RUNPOD_TIMEOUT="300"
export RUNPOD_MAX_RETRIES="3"
export RUNPOD_RETRY_DELAY="2"
```

## Usage

### In the Lead Workshop
1. Navigate to the Lead Workshop (`/lead-workshop`)
2. Select leads for analysis
3. Choose a project and add context
4. **Select AI Service**: Choose between:
   - **Ollama (Local)**: Fast analysis using local models
   - **RunPod.ai (Cloud)**: Enhanced analysis using cloud models
5. Click "Analyze with AI"

### Service Selection
- **Ollama**: Best for quick analysis and when internet connectivity is limited
- **RunPod.ai**: Best for comprehensive analysis requiring detailed insights

## Technical Details

### API Integration
The RunPod integration uses the RunPod API v2 with the following features:
- **Asynchronous Processing**: Jobs are submitted and polled for completion
- **Retry Logic**: Automatic retries with exponential backoff
- **Timeout Handling**: Configurable timeouts for long-running jobs
- **Error Handling**: Comprehensive error handling and fallback mechanisms

### Model Configuration
The integration is designed to work with various text generation models:
- **Llama 2**: Good for general analysis
- **Mistral**: Excellent for business analysis
- **GPT Models**: High-quality analysis with detailed insights
- **Custom Models**: Any model that supports text generation

### Performance Characteristics
- **Processing Time**: 30-120 seconds per lead (depending on model and complexity)
- **Concurrent Requests**: Limited by RunPod endpoint capacity
- **Cost**: Pay-per-use based on RunPod pricing
- **Reliability**: High availability with automatic failover to Ollama

## Configuration Options

### Timeout Settings
```python
RUNPOD_TIMEOUT = 300  # 5 minutes per request
RUNPOD_MAX_RETRIES = 3  # Retry failed requests
RUNPOD_RETRY_DELAY = 2  # Seconds between retries
```

### Model Parameters
```python
max_tokens = 2000  # Maximum response length
temperature = 0.3  # Creativity level (lower = more focused)
top_p = 0.9  # Nucleus sampling parameter
```

## Troubleshooting

### Common Issues

#### 1. "RunPod not configured" Error
**Cause**: Missing API key or endpoint ID
**Solution**: 
- Check configuration in `/config` page
- Verify API key and endpoint ID are correct
- Ensure endpoint is active in RunPod dashboard

#### 2. "Endpoint status check failed" Error
**Cause**: Endpoint is not running or misconfigured
**Solution**:
- Check RunPod dashboard for endpoint status
- Restart the endpoint if needed
- Verify endpoint supports text generation

#### 3. "Request timeout" Error
**Cause**: Analysis taking too long
**Solution**:
- Increase `RUNPOD_TIMEOUT` value
- Check endpoint performance in RunPod dashboard
- Consider using a faster model

#### 4. "Job polling timeout" Error
**Cause**: Endpoint is overloaded or unresponsive
**Solution**:
- Wait and retry the analysis
- Check RunPod dashboard for endpoint health
- Consider scaling up the endpoint

### Debugging
Enable debug logging by setting `LOG_LEVEL=DEBUG` in configuration to see detailed RunPod API interactions.

## Cost Considerations

### RunPod Pricing
- **Pay-per-use**: Only pay for actual processing time
- **Model-dependent**: Larger models cost more per request
- **Endpoint costs**: Small fee for keeping endpoints warm
- **Data transfer**: Minimal costs for API calls

### Cost Optimization
1. **Use appropriate models**: Smaller models for simple analysis
2. **Batch processing**: Analyze multiple leads together when possible
3. **Endpoint management**: Stop unused endpoints to save costs
4. **Monitor usage**: Check RunPod dashboard for usage patterns

## Security

### API Key Security
- **Secret storage**: API keys are stored securely in the database
- **Environment variables**: Can be set as environment variables for additional security
- **Access control**: API keys are not exposed in logs or error messages

### Data Privacy
- **No data retention**: RunPod does not retain your data after processing
- **Secure transmission**: All API calls use HTTPS
- **Local processing**: Sensitive data can be processed locally with Ollama

## Comparison: Ollama vs RunPod.ai

| Feature | Ollama (Local) | RunPod.ai (Cloud) |
|---------|----------------|-------------------|
| **Speed** | Fast (5-30 seconds) | Moderate (30-120 seconds) |
| **Quality** | Good | Excellent |
| **Cost** | Free | Pay-per-use |
| **Reliability** | Depends on local hardware | High availability |
| **Scalability** | Limited by local resources | Highly scalable |
| **Privacy** | Complete local processing | Cloud processing |
| **Setup** | Simple | Requires account and configuration |

## Best Practices

### When to Use RunPod.ai
- **Complex analysis**: When detailed insights are needed
- **Large datasets**: When processing many leads
- **Quality over speed**: When accuracy is more important than speed
- **Resource constraints**: When local hardware is limited

### When to Use Ollama
- **Quick analysis**: When speed is important
- **Privacy concerns**: When data must stay local
- **Cost sensitivity**: When avoiding cloud costs
- **Simple analysis**: When basic insights are sufficient

## Future Enhancements

### Planned Features
- **Batch processing**: Analyze multiple leads simultaneously
- **Model selection**: Choose specific models for different analysis types
- **Custom prompts**: User-defined analysis prompts
- **Result caching**: Cache analysis results to reduce costs
- **Advanced filtering**: Filter leads based on analysis results

### Integration Improvements
- **Real-time status**: Live updates on analysis progress
- **Result comparison**: Compare Ollama vs RunPod results
- **Export options**: Export analysis results in various formats
- **API endpoints**: REST API for external integrations

## Support

For issues with RunPod.ai integration:
1. Check the troubleshooting section above
2. Review RunPod.ai documentation
3. Check LeadFinder logs for detailed error messages
4. Contact support with specific error details

For RunPod.ai service issues:
- Visit [RunPod.ai Support](https://runpod.io/support)
- Check RunPod.ai status page
- Contact RunPod.ai support directly 