# 🚀 LeadFinder Quick Start Guide

## Prerequisites
- Python 3.8+
- Ollama (for AI features)
- SerpAPI key (for web search)

## ⚡ Super Quick Start (3 steps)

1. **Clone and configure:**
```bash
git clone <repository-url>
cd leadfinder
cp env.example env.development
# Edit env.development with your API keys
```

2. **Start Ollama:**
```bash
ollama serve
ollama pull mistral:latest
```

3. **Start the application:**
```bash
./start_app.sh development
```

That's it! The application will be available at `http://localhost:5051`

## 🔧 What the startup script does automatically

The `./start_app.sh development` command automatically:

- ✅ Creates Python virtual environment if missing
- ✅ Installs all required dependencies
- ✅ Validates your configuration
- ✅ Starts the Flask development server
- ✅ Shows you the access URLs

## 🌐 Access URLs

Once started, you can access:

- **Main Application:** http://localhost:5051
- **Health Check:** http://localhost:5051/health
- **AutoGPT Status:** http://localhost:5051/autogpt/status

## 🛠️ Troubleshooting

### If startup fails:

1. **Check Python version:**
```bash
python3 --version  # Should be 3.8+
```

2. **Check Ollama:**
```bash
ollama list  # Should show mistral:latest
```

3. **Check configuration:**
```bash
./start_app.sh development  # Will show specific errors
```

### Common issues:

- **"No module named 'flask'"** - The script will install dependencies automatically
- **"Configuration validation failed"** - Check your API keys in `env.development`
- **"Ollama not available"** - Make sure Ollama is running: `ollama serve`

## 📋 Required API Keys

Edit `env.development` and add your API keys:

```bash
SERPAPI_KEY=your_serpapi_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

Get free API keys:
- **SerpAPI:** https://serpapi.com/ (free tier available)
- **Flask Secret Key:** Any random string (for development)

## 🎯 Next Steps

1. Visit http://localhost:5051
2. Try the search functionality
3. Explore the AutoGPT Control Panel
4. Check out the Research Funding features

## 📚 More Information

- [Full Documentation](README.md)
- [Development Guide](DEVELOPMENT.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Configuration Guide](CONFIGURATION.md) 