# Browser Native Python Client - Usage Guide

## Installation

```bash
pip install browsernative
```

## Quick Start

```python
from browsernative import BrowserNativeClient

# Point the client at your own node-scraper API (the hosted service was retired)
client = BrowserNativeClient(base_url='http://localhost:3001', api_key=None)

# Scrape a webpage
result = client.scrape('https://example.com')
print(result['data'])

# Ask questions with AI
answer = client.analyze('https://example.com', 'What is this website about?')
print(answer['data']['answer'])
```

## Configuration

There is no hosted API: deploy your own service built on `@monostate/node-scraper`
(see README "Hosting the API") and point the client at it. If your deployment
checks an API key, pass `api_key=...` (sent as `x-api-key`).

```bash
export SCRAPER_API_URL=http://localhost:3001
export SCRAPER_API_KEY=your-key   # only if your API requires one
```

## Complete Example

See `example.py` for a complete working example with multiple use cases.

## Integration with Playground Agent Manager

The client is designed to work seamlessly with agent managers:

```python
from browsernative import BrowserNativeClient

class WebScrapingAgent:
    def __init__(self, base_url, api_key=None):
        self.client = BrowserNativeClient(base_url=base_url, api_key=api_key)
    
    def research_topic(self, url, question):
        """Research a topic by scraping and analyzing a webpage"""
        result = self.client.analyze(url, question)
        if result['success']:
            return result['data']['answer']
        else:
            raise Exception(f"Failed to analyze: {result['error']}")
    
    def batch_scrape(self, urls):
        """Scrape multiple URLs in batch"""
        results = []
        for url in urls:
            result = self.client.scrape(url)
            if result['success']:
                results.append(result['data'])
        return results

# Usage
agent = WebScrapingAgent('your-api-key')
answer = agent.research_topic('https://example.com', 'What services are offered?')
```

## Error Handling

The client includes automatic retries and comprehensive error handling:

```python
try:
    result = client.scrape('https://example.com')
    if result['success']:
        # Process data
        data = result['data']
    else:
        # Handle API error
        print(f"Error: {result['error']}")
except Exception as e:
    # Handle connection/network errors
    print(f"Connection error: {e}")
```

## Performance

- 11x faster than traditional scrapers
- Automatic fallback system
- Built-in retries with exponential backoff
- Connection pooling for better performance

## Support

- Documentation: https://github.com/monostate/browsernative-python#readme
- Issues: https://github.com/monostate/browsernative-python/issues
- API Status: https://status.bnca.dev