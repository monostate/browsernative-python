# Browser Native Python Client

> **Lightning-fast web scraping Python SDK - 11x faster than traditional scrapers**

[![PyPI version](https://img.shields.io/pypi/v/browsernative.svg)](https://pypi.org/project/browsernative/)
[![Python](https://img.shields.io/pypi/pyversions/browsernative.svg)](https://pypi.org/project/browsernative/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Official Python client for the Browser Native web scraping API. Extract content, take screenshots, and analyze websites with AI - all with intelligent fallback mechanisms.

## 🚀 Quick Start

### Installation

```bash
pip install browsernative
```

### Basic Usage

```python
from browsernative import BrowserNativeClient

# Initialize client
client = BrowserNativeClient('your-api-key')

# Scrape a webpage
result = client.scrape('https://example.com')
print(result['data'])  # Extracted content

# Take a screenshot
screenshot = client.screenshot('https://example.com')
print(screenshot['data']['screenshot'])  # Base64 image

# AI-powered Q&A
answer = client.analyze('https://example.com', 'What is this website about?')
print(answer['data']['answer'])  # AI response
```

### One-liner Convenience Functions

```python
from browsernative import quick_scrape, quick_analyze, quick_shot

# Quick scraping
data = quick_scrape('https://example.com', 'your-api-key')

# Quick AI analysis
result = quick_analyze(
    'https://example.com', 
    'What services do they offer?',
    'your-api-key'
)

# Quick screenshot
screenshot = quick_shot('https://example.com', 'your-api-key')
```

## 📖 Features

- **🚀 Lightning Fast**: 11x faster than traditional scrapers
- **🔄 Intelligent Fallback**: Multi-tier system (Direct → Lightpanda → Puppeteer)
- **🤖 AI Integration**: Built-in Q&A capabilities with OpenRouter/OpenAI
- **📸 Screenshots**: Full page captures with optimization
- **📄 PDF Support**: Automatic PDF parsing and text extraction
- **🔒 Type Safe**: Full type hints for better IDE support
- **♻️ Context Manager**: Automatic resource cleanup

## 🛠️ API Reference

### Client Initialization

```python
client = BrowserNativeClient(
    api_key='your-api-key',
    base_url='https://bnca-api.fly.dev',  # Optional
    timeout=30,                           # Request timeout in seconds
    retries=2,                           # Number of retries
    verbose=False                        # Enable debug logging
)
```

### Methods

#### `scrape(url, **options)`
Extract structured content from any webpage.

```python
result = client.scrape(
    'https://example.com',
    include_screenshot=True  # Optional: include screenshot
)

# Response includes:
# - data: Extracted content (title, text, meta, etc.)
# - method: Extraction method used
# - performance: Timing metrics
```

#### `analyze(url, question, **options)`
Ask questions about any webpage using AI.

```python
result = client.analyze(
    'https://news.site.com',
    'What are the top 3 stories?',
    include_screenshot=False
)

# Response includes:
# - answer: AI-generated response
# - metadata: Performance and method info
```

#### `screenshot(url, **options)`
Capture full-page screenshots.

```python
result = client.screenshot('https://example.com')
base64_image = result['data']['screenshot']
```

#### `quickshot(url, **options)`
Optimized screenshot capture for speed.

```python
result = client.quickshot('https://example.com')
```

#### `get_usage(days=30)`
Get your API usage statistics.

```python
usage = client.get_usage(days=7)
print(usage['data'])
```

#### `health_check()`
Check API status and your account.

```python
health = client.health_check()
print(health['data']['status'])
```

## 🔄 Context Manager Support

Automatically clean up resources:

```python
with BrowserNativeClient('your-api-key') as client:
    result = client.scrape('https://example.com')
    # Resources are automatically cleaned up
```

## 🎯 Advanced Examples

### Batch Processing

```python
urls = ['https://site1.com', 'https://site2.com', 'https://site3.com']

with BrowserNativeClient('your-api-key') as client:
    for url in urls:
        try:
            result = client.scrape(url)
            print(f"✓ {url}: {result['data']['title']}")
        except Exception as e:
            print(f"✗ {url}: {e}")
```

### Error Handling

```python
from browsernative import BrowserNativeClient

client = BrowserNativeClient('your-api-key', verbose=True)

try:
    result = client.scrape('https://invalid-url')
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"API error: {e}")
```

### AI Analysis with Context

```python
# Analyze multiple aspects of a page
questions = [
    "What is the main topic?",
    "Is there pricing information?",
    "What features are highlighted?"
]

with BrowserNativeClient('your-api-key') as client:
    for question in questions:
        result = client.analyze('https://product.com', question)
        print(f"Q: {question}")
        print(f"A: {result['data']['answer']}\n")
```

## 🔑 Getting an API Key

1. Visit [https://bnca.monostate.ai](https://bnca.monostate.ai)
2. Sign up for an account
3. Generate your API key from the dashboard

## 📋 Requirements

- Python 3.7+
- `requests` library (automatically installed)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [API Documentation](https://docs.bnca.dev)
- [GitHub Repository](https://github.com/monostate/browsernative-python)
- [PyPI Package](https://pypi.org/project/browsernative/)
- [Report Issues](https://github.com/monostate/browsernative-python/issues)