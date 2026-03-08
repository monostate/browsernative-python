# browsernative

> Python client for the Browser Native web scraping API

[![PyPI](https://img.shields.io/pypi/v/browsernative.svg)](https://pypi.org/project/browsernative/)
[![Python](https://img.shields.io/pypi/pyversions/browsernative.svg)](https://pypi.org/project/browsernative/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Lightweight client for scraping, screenshots, and AI analysis via the Browser Native API. Single dependency (`requests`).

## Install

```bash
pip install browsernative
```

Get an API key at [bnca.monostate.ai](https://bnca.monostate.ai).

## Usage

```python
from browsernative import BrowserNativeClient

client = BrowserNativeClient('your-api-key')

# Scrape
result = client.scrape('https://example.com')

# Force a specific scraping method
result = client.scrape('https://example.com', method='lightpanda')

# Screenshot
screenshot = client.screenshot('https://example.com')

# Quick screenshot (faster, no content extraction)
quick = client.quickshot('https://example.com')

# AI Q&A
answer = client.analyze('https://example.com', 'What is this site about?')
```

### Convenience functions

```python
from browsernative import quick_scrape, quick_shot, quick_analyze, bulk_scrape

content = quick_scrape('https://example.com', 'your-api-key')
shot = quick_shot('https://example.com', 'your-api-key')
answer = quick_analyze('https://example.com', 'What is this?', 'your-api-key')
```

### Bulk scraping

```python
urls = ['https://site1.com', 'https://site2.com', 'https://site3.com']

result = client.bulk_scrape(
    urls,
    concurrency=5,
    continue_on_error=True,
    progress_callback=lambda p: print(f"{p['percentage']:.1f}%"),
)

print(f"{result['stats']['successful']}/{result['stats']['total']} succeeded")
```

### Context manager

```python
with BrowserNativeClient('your-api-key') as client:
    result = client.scrape('https://example.com')
    # Session closed automatically
```

## API Reference

### Client options

```python
client = BrowserNativeClient(
    api_key='your-api-key',
    base_url='https://bnca-api.fly.dev',  # API endpoint
    timeout=30,                            # Seconds
    retries=2,                             # Retry attempts
    verbose=False,                         # Debug logging
)
```

### Methods

| Method | Description |
|--------|-------------|
| `scrape(url, **opts)` | Extract structured content |
| `screenshot(url, **opts)` | Screenshot with content extraction |
| `quickshot(url, **opts)` | Fast screenshot only |
| `analyze(url, question, **opts)` | AI-powered Q&A |
| `bulk_scrape(urls, **opts)` | Scrape multiple URLs concurrently |
| `get_usage(days=30)` | Account usage statistics |
| `health_check()` | API health status |

### Scrape options

Pass as keyword arguments:

- `method` -- `'auto'`, `'direct'`, `'lightpanda'`, or `'puppeteer'`
- `include_screenshot` -- Include screenshot in response
- `wait_for_selector` -- CSS selector to wait for
- `user_agent` -- Custom user agent

### Response shape

```python
{
    'success': True,
    'data': { 'title': ..., 'content': ..., ... },
    'responseTime': 1234,
    'attempt': 1,
}
```

## Requirements

- Python 3.9+
- `requests` (installed automatically)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).

## License

MIT
