# Smart RunPod Configuration Guide

## Overview

LeadFinder's smart RunPod integration automatically optimizes AI service usage based on your workload and configuration preferences. This system saves RunPod power for batch processing and complex analysis while ensuring reliable fallback to local Ollama.

## 🎯 Smart Decision Making

### Automatic Service Selection

The system makes intelligent decisions based on:

1. **Lead Count**: Number of leads to analyze
2. **Analysis Type**: Standard vs complex analysis
3. **Configuration Settings**: Your preferences and thresholds
4. **Service Availability**: Current status of RunPod and Ollama

### Decision Matrix

| Scenario | Service Used | Reasoning |
|----------|-------------|-----------|
| **1-4 leads** | Ollama | Fast, free, sufficient for small batches |
| **5+ leads** | RunPod | Enhanced analysis for batch processing |
| **Complex analysis** | RunPod | Detailed insights and comprehensive data extraction |
| **Service failure** | Ollama fallback | Ensures analysis always completes |
| **User override** | User choice | Respects explicit user selection |

## ⚙️ Configuration Options

### Master Controls

#### `RUNPOD_ENABLED`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Master switch for RunPod integration
- **Usage**: Enable/disable RunPod functionality entirely

#### `RUNPOD_AUTO_ENABLE`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Auto-enable for batch processing
- **Usage**: Automatically use RunPod when analyzing multiple leads

### Threshold Settings

#### `RUNPOD_BATCH_THRESHOLD`
- **Type**: Integer
- **Default**: `5`
- **Range**: 1-20
- **Description**: Number of leads that triggers automatic RunPod usage
- **Usage**: Controls when batch processing kicks in

### Analysis Type Controls

#### `RUNPOD_COMPLEX_ANALYSIS`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Use RunPod for detailed analysis
- **Usage**: Determines if complex analysis uses RunPod

#### `RUNPOD_FALLBACK_TO_OLLAMA`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Fallback to Ollama if RunPod fails
- **Usage**: Ensures analysis completion even if RunPod fails

### Performance Settings

#### `RUNPOD_TIMEOUT`
- **Type**: Integer (seconds)
- **Default**: `300`
- **Range**: 60-600
- **Description**: Maximum time to wait for RunPod analysis
- **Usage**: Prevents hanging on slow RunPod responses

#### `RUNPOD_MAX_RETRIES`
- **Type**: Integer
- **Default**: `3`
- **Range**: 1-10
- **Description**: Maximum retry attempts for failed requests
- **Usage**: Improves reliability for network issues

#### `RUNPOD_RETRY_DELAY`
- **Type**: Integer (seconds)
- **Default**: `2`
- **Range**: 1-10
- **Description**: Delay between retry attempts
- **Usage**: Prevents overwhelming the RunPod service

## 🎛️ Configuration Profiles

### Conservative (Cost-Focused)
```bash
RUNPOD_ENABLED=True
RUNPOD_AUTO_ENABLE=True
RUNPOD_BATCH_THRESHOLD=10
RUNPOD_COMPLEX_ANALYSIS=False
RUNPOD_FALLBACK_TO_OLLAMA=True
RUNPOD_TIMEOUT=300
```

**Use Case**: Minimize RunPod costs while maintaining functionality
- Only uses RunPod for large batches (10+ leads)
- Uses Ollama for complex analysis
- Maintains fallback for reliability

### Performance-Focused
```bash
RUNPOD_ENABLED=True
RUNPOD_AUTO_ENABLE=True
RUNPOD_BATCH_THRESHOLD=3
RUNPOD_COMPLEX_ANALYSIS=True
RUNPOD_FALLBACK_TO_OLLAMA=True
RUNPOD_TIMEOUT=600
```

**Use Case**: Maximize analysis quality and insights
- Uses RunPod for smaller batches (3+ leads)
- Always uses RunPod for complex analysis
- Longer timeout for detailed processing

### Balanced (Default)
```bash
RUNPOD_ENABLED=True
RUNPOD_AUTO_ENABLE=True
RUNPOD_BATCH_THRESHOLD=5
RUNPOD_COMPLEX_ANALYSIS=True
RUNPOD_FALLBACK_TO_OLLAMA=True
RUNPOD_TIMEOUT=300
```

**Use Case**: Optimal balance of cost and performance
- Standard batch threshold (5+ leads)
- Enhanced analysis when needed
- Reliable fallback system

### Development/Testing
```bash
RUNPOD_ENABLED=False
RUNPOD_AUTO_ENABLE=False
RUNPOD_BATCH_THRESHOLD=5
RUNPOD_COMPLEX_ANALYSIS=False
RUNPOD_FALLBACK_TO_OLLAMA=True
RUNPOD_TIMEOUT=300
```

**Use Case**: Development and testing environments
- Disabled RunPod integration
- Uses only Ollama for all analysis
- Maintains fallback for testing

## 🔧 Configuration Methods

### 1. Web Interface
1. Navigate to `/config`
2. Find the **RunPod.ai Smart Configuration** section
3. Adjust settings using the form controls
4. Save changes

### 2. Environment Variables
```bash
export RUNPOD_ENABLED="True"
export RUNPOD_AUTO_ENABLE="True"
export RUNPOD_BATCH_THRESHOLD="5"
export RUNPOD_COMPLEX_ANALYSIS="True"
export RUNPOD_FALLBACK_TO_OLLAMA="True"
export RUNPOD_TIMEOUT="300"
export RUNPOD_MAX_RETRIES="3"
export RUNPOD_RETRY_DELAY="2"
```

### 3. Configuration File
Add to your `env.development` or `env.production`:
```bash
# RunPod Smart Configuration
RUNPOD_ENABLED=True
RUNPOD_AUTO_ENABLE=True
RUNPOD_BATCH_THRESHOLD=5
RUNPOD_COMPLEX_ANALYSIS=True
RUNPOD_FALLBACK_TO_OLLAMA=True
RUNPOD_TIMEOUT=300
RUNPOD_MAX_RETRIES=3
RUNPOD_RETRY_DELAY=2
```

## 📊 Usage Scenarios

### Single Lead Analysis
- **Service**: Ollama
- **Time**: 5-30 seconds
- **Cost**: Free
- **Quality**: Good for basic analysis
- **Configuration**: No special settings needed

### Small Batch (2-4 leads)
- **Service**: Ollama
- **Time**: 10-120 seconds total
- **Cost**: Free
- **Quality**: Good for standard analysis
- **Configuration**: `RUNPOD_BATCH_THRESHOLD=5`

### Medium Batch (5-9 leads)
- **Service**: RunPod (if auto-enabled)
- **Time**: 150-600 seconds total
- **Cost**: Pay-per-use
- **Quality**: Excellent with detailed insights
- **Configuration**: `RUNPOD_AUTO_ENABLE=True`

### Large Batch (10+ leads)
- **Service**: RunPod
- **Time**: 300-1200 seconds total
- **Cost**: Pay-per-use
- **Quality**: Comprehensive analysis
- **Configuration**: `RUNPOD_BATCH_THRESHOLD=5`

### Complex Analysis
- **Service**: RunPod (if enabled)
- **Time**: 60-180 seconds
- **Cost**: Pay-per-use
- **Quality**: Detailed insights and structured data
- **Configuration**: `RUNPOD_COMPLEX_ANALYSIS=True`

## 🔍 Monitoring and Debugging

### Service Status
Check service availability:
```bash
curl http://localhost:5051/health
```

### Configuration Verification
Verify current settings:
```bash
curl http://localhost:5051/config
```

### Debug Logging
Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
```

### RunPod Dashboard
Monitor usage and costs:
- Visit [RunPod Dashboard](https://runpod.io/console)
- Check endpoint status
- Monitor API usage and costs

## 🚨 Troubleshooting

### Common Issues

#### RunPod Not Being Used
**Symptoms**: Always uses Ollama even for large batches
**Solutions**:
1. Check `RUNPOD_ENABLED=True`
2. Verify `RUNPOD_AUTO_ENABLE=True`
3. Confirm `RUNPOD_BATCH_THRESHOLD` is appropriate
4. Check RunPod API key and endpoint ID

#### RunPod Always Being Used
**Symptoms**: Uses RunPod even for single leads
**Solutions**:
1. Increase `RUNPOD_BATCH_THRESHOLD`
2. Set `RUNPOD_AUTO_ENABLE=False`
3. Check lead count logic

#### Analysis Failures
**Symptoms**: Analysis fails with no fallback
**Solutions**:
1. Ensure `RUNPOD_FALLBACK_TO_OLLAMA=True`
2. Check Ollama service availability
3. Verify network connectivity

#### Timeout Issues
**Symptoms**: Analysis times out frequently
**Solutions**:
1. Increase `RUNPOD_TIMEOUT`
2. Check RunPod endpoint performance
3. Consider using faster models

### Performance Optimization

#### Cost Optimization
1. **Increase batch threshold**: Use higher values for `RUNPOD_BATCH_THRESHOLD`
2. **Disable complex analysis**: Set `RUNPOD_COMPLEX_ANALYSIS=False`
3. **Monitor usage**: Check RunPod dashboard regularly
4. **Use conservative timeouts**: Lower `RUNPOD_TIMEOUT` values

#### Performance Optimization
1. **Decrease batch threshold**: Use lower values for `RUNPOD_BATCH_THRESHOLD`
2. **Enable complex analysis**: Set `RUNPOD_COMPLEX_ANALYSIS=True`
3. **Increase timeouts**: Higher `RUNPOD_TIMEOUT` for detailed analysis
4. **Use faster models**: Choose optimized RunPod endpoints

## 🔮 Future Enhancements

### Planned Features
- **Dynamic thresholds**: Automatic adjustment based on usage patterns
- **Cost monitoring**: Real-time cost tracking and alerts
- **Performance analytics**: Detailed metrics and optimization suggestions
- **Advanced fallback**: Multiple fallback strategies
- **Custom models**: Support for user-trained models

### Integration Opportunities
- **Multi-region support**: Different RunPod regions
- **Enterprise features**: Advanced security and compliance
- **API extensions**: Additional RunPod API capabilities
- **Custom prompts**: User-defined analysis templates

## 📚 Best Practices

### Configuration
1. **Start conservative**: Use higher thresholds initially
2. **Monitor costs**: Check RunPod dashboard regularly
3. **Test thoroughly**: Verify both services work
4. **Adjust gradually**: Fine-tune based on usage patterns

### Usage
1. **Batch when possible**: Group leads for efficient processing
2. **Use project context**: Enable complex analysis when needed
3. **Monitor performance**: Track analysis times and quality
4. **Plan for failures**: Ensure fallback systems work

### Maintenance
1. **Regular monitoring**: Check service status and costs
2. **Update configurations**: Adjust based on changing needs
3. **Test fallbacks**: Verify Ollama works when RunPod fails
4. **Document changes**: Keep track of configuration modifications

## 🆘 Support

### Getting Help
1. Check the troubleshooting section above
2. Review RunPod dashboard for endpoint status
3. Enable debug logging for detailed information
4. Contact support with specific error messages

### Resources
- [RunPod Documentation](https://docs.runpod.io/)
- [LeadFinder Issues](https://github.com/your-repo/leadfinder/issues)
- [RunPod Discord](https://discord.gg/runpod)
- [Configuration Examples](RUNPOD_INTEGRATION.md)