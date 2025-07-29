# RunPod.ai Smart Integration for Lead Workshop

## Overview

LeadFinder now includes **smart RunPod.ai integration** that automatically chooses between RunPod and Ollama based on your workload and configuration. This intelligent system saves RunPod power for batch processing and complex analysis while providing seamless fallback to local Ollama.

## 🧠 Smart Decision Making

### Automatic Service Selection

The system intelligently chooses the best AI service based on:

| Scenario | Service Used | Reason |
|----------|-------------|---------|
| **1-4 leads** | Ollama | Fast, free, sufficient for small batches |
| **5+ leads** | RunPod | Enhanced analysis for batch processing |
| **Complex analysis** | RunPod | Detailed insights and comprehensive data extraction |
| **Service failure** | Ollama fallback | Ensures analysis always completes |

### Configuration-Driven Behavior

The system respects your configuration preferences:

- **`RUNPOD_ENABLED`**: Master switch for RunPod integration
- **`RUNPOD_AUTO_ENABLE`**: Auto-enable for batch processing
- **`RUNPOD_BATCH_THRESHOLD`**: Number of leads that triggers RunPod (default: 5)
- **`RUNPOD_COMPLEX_ANALYSIS`**: Use RunPod for detailed analysis
- **`RUNPOD_FALLBACK_TO_OLLAMA`**: Fallback to Ollama if RunPod fails

## Features

### Enhanced Analysis Capabilities
- **More Powerful Models**: Access to larger, more sophisticated AI models
- **Better Data Extraction**: Improved extraction of people, contacts, products, and company information
- **Comprehensive Analysis**: Detailed analysis with opportunities, concerns, and actionable insights
- **Faster Processing**: Cloud-based processing with dedicated GPU resources
- **Scalable**: Handle larger datasets and more complex analysis tasks

### Smart Usage Patterns
- **Cost Optimization**: Only use RunPod when needed
- **Performance Benefits**: Ollama for quick results, RunPod for comprehensive analysis
- **Reliable Fallback**: Never lose analysis capability
- **Transparent Selection**: Users see which service will be used

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
2. Navigate to the **RunPod.ai Smart Configuration** section
3. Configure the following settings:

#### Basic Configuration
- **Enable RunPod.ai Integration**: Master switch to enable/disable RunPod
- **Auto-Enable for Batch Processing**: Automatically use RunPod when analyzing 5+ leads
- **Use for Complex Analysis**: Use RunPod for detailed insights and comprehensive analysis
- **Fallback to Ollama**: Use Ollama if RunPod fails or is unavailable

#### Advanced Settings
- **Batch Processing Threshold**: Number of leads that triggers automatic RunPod usage (default: 5)
- **RunPod Timeout**: Maximum time to wait for RunPod analysis (default: 300 seconds)

#### API Configuration
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
export RUNPOD_ENABLED="True"
export RUNPOD_AUTO_ENABLE="True"
export RUNPOD_BATCH_THRESHOLD="5"
export RUNPOD_COMPLEX_ANALYSIS="True"
export RUNPOD_FALLBACK_TO_OLLAMA="True"
```

## Usage

### In the Lead Workshop
1. Navigate to the Lead Workshop (`/lead-workshop`)
2. Select leads for analysis
3. Choose a project and add context
4. **Select AI Service**: Choose between:
   - **🔄 Auto-Select (Recommended)**: Smart service selection based on workload
   - **🚀 RunPod.ai (Enhanced)**: Force RunPod usage for all analysis
5. Click "Analyze with AI"

### Smart Service Selection
- **Auto-Select**: The system automatically chooses the best service based on:
  - Number of leads selected
  - Analysis complexity (project context)
  - Your configuration settings
- **RunPod.ai**: Force enhanced analysis using cloud models

### Service Recommendations
- **Ollama**: Best for quick analysis and when internet connectivity is limited
- **RunPod.ai**: Best for comprehensive analysis requiring detailed insights
- **Auto-Select**: Best for optimal performance and cost efficiency

## Configuration Examples

### Conservative (Cost-Focused)
```bash
RUNPOD_ENABLED=True
RUNPOD_AUTO_ENABLE=True
RUNPOD_BATCH_THRESHOLD=10  # Only for large batches
RUNPOD_COMPLEX_ANALYSIS=False  # Use Ollama for most analysis
```

### Performance-Focused
```bash
RUNPOD_ENABLED=True
RUNPOD_AUTO_ENABLE=True
RUNPOD_BATCH_THRESHOLD=3  # Use RunPod for smaller batches
RUNPOD_COMPLEX_ANALYSIS=True  # Always use RunPod for detailed analysis
```

### Balanced (Default)
```bash
RUNPOD_ENABLED=True
RUNPOD_AUTO_ENABLE=True
RUNPOD_BATCH_THRESHOLD=5  # Standard batch threshold
RUNPOD_COMPLEX_ANALYSIS=True  # Enhanced analysis when needed
```

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
5. **Smart configuration**: Use conservative settings to minimize costs

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

### Smart Configuration Tips
- **Start conservative**: Use higher batch thresholds initially
- **Monitor costs**: Check RunPod dashboard regularly
- **Test thoroughly**: Verify both services work before production
- **Adjust based on usage**: Fine-tune settings based on your patterns

## Future Enhancements

### Planned Features
- **Batch processing**: Analyze multiple leads simultaneously
- **Model selection**: Choose specific models for different analysis types
- **Cost monitoring**: Real-time cost tracking and alerts
- **Performance analytics**: Detailed performance metrics and optimization suggestions
- **Advanced fallback**: Multiple fallback strategies and service combinations

### Integration Opportunities
- **Custom models**: Support for custom-trained models
- **Multi-region**: Support for different RunPod regions
- **Enterprise features**: Advanced security and compliance features
- **API extensions**: Additional RunPod API features and capabilities

## Support and Resources

### Documentation
- [RunPod.ai Documentation](https://docs.runpod.io/)
- [RunPod API Reference](https://docs.runpod.io/reference)
- [LeadFinder Documentation](https://github.com/your-repo/leadfinder)

### Community
- [RunPod Discord](https://discord.gg/runpod)
- [LeadFinder Issues](https://github.com/your-repo/leadfinder/issues)

### Getting Help
- Check the troubleshooting section above
- Review RunPod dashboard for endpoint status
- Enable debug logging for detailed error information
- Contact support with specific error messages and logs 