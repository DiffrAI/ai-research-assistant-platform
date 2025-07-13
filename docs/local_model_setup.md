# Local Model Setup Guide

This guide shows how to use your local Ollama model instead of OpenAI and DuckDuckGo instead of Tavily.

## Configuration

Add these settings to your `.env` file:

```env
# Model Configuration
USE_LOCAL_MODEL=true
LOCAL_MODEL_URL=http://127.0.0.1:11434
LOCAL_MODEL_NAME=qwen2.5:7b  # Must match the model loaded in Ollama

# Search Provider Configuration
SEARCH_PROVIDER=duckduckgo  # "duckduckgo" or "tavily"
DUCKDUCKGO_MAX_RESULTS=10
SEARCH_MAX_RETRIES=3         # Number of retries for DuckDuckGo search
SEARCH_BASE_DELAY=1.0        # Base delay (seconds) for exponential backoff
SEARCH_MAX_DELAY=10.0        # Max delay (seconds) for exponential backoff

# OpenAI Configuration (used when USE_LOCAL_MODEL=false)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily Configuration (used when SEARCH_PROVIDER=tavily)
TAVILY_API_KEY=your_tavily_api_key_here
```

## Setup Steps

### 1. Install Ollama
- **macOS/Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`
- **Windows**: Download from https://ollama.ai
- **Docker**: `docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama`

### 2. Pull and Start a Model
```bash
# Pull a recommended model
ollama pull qwen2.5:7b

# Start Ollama server (runs automatically)
ollama serve

# Verify the model is loaded
ollama list
```

### 3. Configure Environment
Create a `.env` file in the project root:

```env
# Core Settings
LOG_LEVEL=DEBUG
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8002

# Model Configuration
USE_LOCAL_MODEL=true
LOCAL_MODEL_URL=http://127.0.0.1:11434
LOCAL_MODEL_NAME=qwen2.5:7b

# Search Provider Configuration
SEARCH_PROVIDER=duckduckgo
DUCKDUCKGO_MAX_RESULTS=10
SEARCH_MAX_RETRIES=3
SEARCH_BASE_DELAY=1.0
SEARCH_MAX_DELAY=10.0

# Optional: Tavily (if you want to switch back)
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: Langfuse for observability
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

### 4. Run the Application
```bash
# Install dependencies
uv sync

# Start the application
make run-dev
```

### 5. Test the Setup
```bash
# Test web search with local model and DuckDuckGo
curl "http://localhost:8002/api/v1/chat/websearch?question=What%20is%20Python%20programming&thread_id=123"
```

## Switching Between Models and Search Providers

### Use Local Model + DuckDuckGo (Free Setup)
```env
USE_LOCAL_MODEL=true
LOCAL_MODEL_URL=http://127.0.0.1:11434
LOCAL_MODEL_NAME=qwen2.5:7b
SEARCH_PROVIDER=duckduckgo
```

### Use OpenAI + Tavily (Paid Setup)
```env
USE_LOCAL_MODEL=false
OPENAI_API_KEY=your_openai_api_key_here
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_tavily_api_key_here
```

### Mix and Match
```env
# Local model with Tavily search
USE_LOCAL_MODEL=true
LOCAL_MODEL_URL=http://127.0.0.1:11434
LOCAL_MODEL_NAME=qwen2.5:7b
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_tavily_api_key_here

# OpenAI with DuckDuckGo search
USE_LOCAL_MODEL=false
OPENAI_API_KEY=your_openai_api_key_here
SEARCH_PROVIDER=duckduckgo
```

## Recommended Models

### Fast & Efficient (Development)
- `qwen2.5:7b` - Good balance of speed and quality
- `llama3.2:3b` - Very fast, smaller size
- `mistral:7b` - Good performance, moderate speed

### High Quality (Production)
- `qwen2.5:32b` - Excellent quality, slower
- `llama3.2:70b` - Best quality, requires more RAM
- `mixtral:8x7b` - Very good quality, moderate speed

### Specialized Models
- `codellama:7b` - For code-related tasks
- `llama3.2:3b-instruct` - Optimized for instructions

## DuckDuckGo Retry Logic (Web Search)

- The system includes robust retry logic and exponential backoff for DuckDuckGo web search.
- You can configure the retry behavior in your `.env`:

```env
SEARCH_MAX_RETRIES=3         # Number of retries for DuckDuckGo search
SEARCH_BASE_DELAY=1.0        # Base delay (seconds) for exponential backoff
SEARCH_MAX_DELAY=10.0        # Max delay (seconds) for exponential backoff
```

## Benefits of Free Setup (Local Model + DuckDuckGo)

1. **No API Costs**: Completely free to use
2. **Privacy**: All processing happens locally
3. **No Rate Limits**: DuckDuckGo has no API limits
4. **Customizable**: Use any model supported by Ollama
5. **Offline**: Works without internet connection (except for web search)
6. **Fast**: No network latency for model inference

## Search Provider Comparison

| Feature | DuckDuckGo | Tavily |
|---------|------------|--------|
| Cost | Free | Free tier + paid |
| Rate Limits | None | 1,000/month free |
| API Key Required | No | Yes |
| Search Quality | Good | Excellent |
| Structured Results | Basic | Advanced |
| Content Extraction | Limited | Full |

## 🚨 Troubleshooting

### Ollama Connection Issues

**Problem**: `Connection refused` or `Model not found`
```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Start Ollama if not running
ollama serve

# Check available models
ollama list

# Pull the model if not available
ollama pull qwen2.5:7b
```

**Problem**: Wrong model name
```bash
# List all available models
ollama list

# Update your .env to match the exact model name
LOCAL_MODEL_NAME=qwen2.5:7b  # Must match exactly
```

### Model Performance Issues

**Problem**: Slow response times
```bash
# Check system resources
htop  # or top

# Use a smaller model for development
ollama pull llama3.2:3b
# Update LOCAL_MODEL_NAME=llama3.2:3b

# Increase Ollama memory allocation
export OLLAMA_HOST=0.0.0.0
export OLLAMA_ORIGINS=*
```

**Problem**: Out of memory errors
```bash
# Use a smaller model
ollama pull qwen2.5:3b

# Or increase system memory
# For Docker: docker run -d --gpus all -v ollama:/root/.ollama -p 11434:11434 ollama/ollama
```

### Search Issues

**Problem**: DuckDuckGo rate limiting
```bash
# Increase retry delays in .env
SEARCH_MAX_RETRIES=5
SEARCH_BASE_DELAY=2.0
SEARCH_MAX_DELAY=15.0

# Or switch to Tavily
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_key_here
```

**Problem**: No search results
```bash
# Test DuckDuckGo directly
curl "https://api.duckduckgo.com/?q=test&format=json"

# Check internet connection
ping 8.8.8.8

# Try a different search query
```

### Application Issues

**Problem**: Model validation errors
```bash
# Check your .env configuration
cat .env | grep LOCAL_MODEL

# Ensure model name matches exactly
ollama list | grep qwen2.5:7b

# Restart the application
pkill -f "python main.py"
python main.py
```

**Problem**: Import errors
```bash
# Install dependencies
uv sync

# Check Python version (requires 3.9+)
python --version

# Reinstall virtual environment
rm -rf .venv
uv sync
```

### Docker Issues

**Problem**: Ollama not accessible from Docker
```bash
# Run Ollama with host networking
docker run -d --network host -v ollama:/root/.ollama ollama/ollama

# Or update LOCAL_MODEL_URL in .env
LOCAL_MODEL_URL=http://host.docker.internal:11434
```

### Performance Optimization

**For Better Performance**:
```bash
# Use GPU acceleration (if available)
ollama run qwen2.5:7b --gpu

# Increase system memory
# Add to /etc/systemd/system/ollama.service
# Environment="OLLAMA_HOST=0.0.0.0"
# Environment="OLLAMA_ORIGINS=*"

# Use a smaller model for development
ollama pull llama3.2:3b
```

### Debug Mode

**Enable detailed logging**:
```env
LOG_LEVEL=TRACE
```

**Check Ollama logs**:
```bash
# View Ollama logs
journalctl -u ollama -f

# Or if running manually
ollama serve --verbose
```

### Common Error Messages

| Error | Solution |
|-------|----------|
| `Connection refused` | Start Ollama: `ollama serve` |
| `Model not found` | Pull model: `ollama pull qwen2.5:7b` |
| `Out of memory` | Use smaller model or increase RAM |
| `Rate limit exceeded` | Increase retry delays or switch to Tavily |
| `Invalid model name` | Check exact model name with `ollama list` |

## Getting Help

1. **Check Ollama logs**: `journalctl -u ollama -f`
2. **Test Ollama directly**: `ollama run qwen2.5:7b "Hello"`
3. **Check application logs**: Look for error messages in your app logs
4. **Verify configuration**: Ensure all environment variables are set correctly
5. **Community support**: [Ollama Discord](https://discord.gg/ollama) or [GitHub Issues](https://github.com/ollama/ollama/issues) 