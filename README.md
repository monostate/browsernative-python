# browsernative

> Python client for a self-hosted node-scraper API

[![PyPI](https://img.shields.io/pypi/v/browsernative.svg)](https://pypi.org/project/browsernative/)
[![Python](https://img.shields.io/pypi/pyversions/browsernative.svg)](https://pypi.org/project/browsernative/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Lightweight client for scraping, screenshots, AI analysis and persistent
browser sessions, talking to an API **you host** that is built on
[`@monostate/node-scraper`](https://www.npmjs.com/package/@monostate/node-scraper).
Single dependency (`requests`).

> **v3:** the hosted Browser Native API (bnca-api.fly.dev / bnca.monostate.ai)
> has been retired. There is no default endpoint any more: `base_url` is
> required and the API key is optional (only if your deployment checks one).
> See [Migrating from 2.x](#migrating-from-2x).

## Install

```bash
pip install browsernative
```

## Usage

```python
import os
from browsernative import BrowserNativeClient

client = BrowserNativeClient(
    base_url='http://localhost:3001',          # your node-scraper API
    api_key=os.environ.get('SCRAPER_API_KEY'),  # optional: sent as x-api-key when set
)

# Scrape
result = client.scrape('https://example.com')
result['data']['metadata']['contentStatus']  # 'usable' | 'browser_required_shell' | 'blocked' | 'empty' | 'navigation_error'

# Force a specific scraping method
result = client.scrape('https://example.com', method='lightpanda')

# Screenshot / quick screenshot
client.screenshot('https://example.com')
client.quickshot('https://example.com')

# AI Q&A (the API must be configured with a model provider)
client.analyze('https://example.com', 'What is this site about?')
```

### Convenience functions

```python
from browsernative import quick_scrape, quick_shot, quick_analyze, bulk_scrape

api = dict(base_url='http://localhost:3001', api_key=None)
content = quick_scrape('https://example.com', **api)
shot = quick_shot('https://example.com', **api)
answer = quick_analyze('https://example.com', 'What is this?', **api)
```

### Bulk scraping

```python
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
with BrowserNativeClient(base_url='http://localhost:3001') as client:
    result = client.scrape('https://example.com')
```

## Hosting the API

The client speaks to an HTTP/WebSocket service with these routes, all
`POST` with a JSON body unless noted:

| Route | Body | Purpose |
|---|---|---|
| `/scrapeurl` | `{ url, method?, screenshot? }` | Scrape; response `{ success, data, metadata: { method, contentStatus, httpStatus, finalUrl, … } }` |
| `/quickshot` | `{ url }` | Fast screenshot |
| `/aireply` | `{ url, question }` | AI answer about a page |
| `/bulk-scrape` | `{ urls, … }` | Bulk scrape (optional) |
| `GET /health` | | Health check |
| `GET /stats` | | Usage statistics (optional) |
| `WS /session?mode=…&apiKey=…` | | Persistent browser session (optional) |

Authentication, when enabled, is the `x-api-key` header (and the `apiKey`
query parameter for the WebSocket). Build the service on
`@monostate/node-scraper`, which provides the engines, outcomes and
sessions; the service only adds HTTP, auth and limits of your choosing.

## API Reference

### Client options

```python
client = BrowserNativeClient(
    base_url='http://localhost:3001',  # required
    api_key=None,                      # optional
    timeout=30,                        # seconds
    retries=2,                         # retry attempts
    verbose=False,                     # debug logging
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
| `get_usage(days=30)` | Usage statistics (if your API implements `/stats`) |
| `health_check()` | API health status |
| `create_session(mode=…)` | Persistent browser session over WebSocket |

### Scrape options

- `method` -- `'auto'`, `'direct'`, `'lightpanda'`, or `'puppeteer'`
- `include_screenshot` -- Include screenshot in response
- `wait_for_selector` -- CSS selector to wait for
- `user_agent` -- Custom user agent

### Response shape

```python
{
    'success': True,                 # the request succeeded
    'data': {                        # the API's JSON body
        'data': {'title': ..., 'content': ..., ...},
        'metadata': {'method': ..., 'contentStatus': ..., 'httpStatus': ..., 'finalUrl': ..., ...},
    },
    'responseTime': 1234,
    'attempt': 1,
}
```

Check `data['metadata']['contentStatus']` to know whether the content is
usable: node-scraper v3 reports empty bodies, SPA shells and block pages
honestly instead of calling them successes.

### Browser sessions

```python
session = client.create_session(mode='auto')
session.goto('https://example.com')
session.click('#login')
session.type('#email', 'user@example.com')
state = session.get_page_state(includeScreenshot=True)
session.on('fallback', lambda e: print(f"{e['from']} -> {e['to']}: {e['reason']}"))
session.close()
```

Modes: `auto` (LightPanda with Chrome fallback), `headless`, `visual`, `computer-use`.

#### Computer use mode

```python
session = client.create_session(mode='computer-use', screen_width=1280, screen_height=800)
session.goto('https://example.com')
session.click_at(640, 400)
session.type_text('hello world')
session.drag(10, 20, 300, 400)
screenshot = session.screenshot()
print(session.vnc_url)
session.close()
```

Requires `websocket-client`: `pip install websocket-client`

## Migrating from 2.x

| 2.x | 3.x |
|---|---|
| `BrowserNativeClient('key')` used the hosted API | `BrowserNativeClient(base_url=..., api_key=...)` against your own API |
| API key required | optional; sent only when set |
| `quick_scrape(url, 'key')` | `quick_scrape(url, 'key', base_url=...)` or `quick_scrape(url, base_url=...)` |
| results had `method` only | plus `metadata.contentStatus`, `httpStatus`, `finalUrl` |

## Requirements

- Python 3.9+
- `requests` (installed automatically)
- `websocket-client` (for browser sessions)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).

## License

MIT
