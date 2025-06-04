# Changelog

All notable changes to the Browser Native Python Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-04

### Added
- Initial release of Browser Native Python Client
- Full API compatibility with JavaScript client
- `BrowserNativeClient` class with all API methods:
  - `scrape()` - Extract structured content from webpages
  - `analyze()` - AI-powered Q&A about webpage content
  - `screenshot()` - Full page screenshots
  - `quickshot()` - Optimized screenshot capture
  - `get_usage()` - Account usage statistics
  - `health_check()` - API health status
- Convenience functions for quick operations:
  - `quick_scrape()`
  - `quick_analyze()`
  - `quick_screenshot()`
  - `quick_shot()`
- Automatic retry logic with exponential backoff
- Connection pooling for improved performance
- Context manager support for resource cleanup
- Comprehensive error handling
- Full type hints for better IDE support
- Example scripts and documentation
- Support for Python 3.7+

### Performance
- 11x faster than traditional scrapers
- Intelligent fallback system (Direct → Lightpanda → Puppeteer)
- Optimized for high-throughput operations

[1.0.0]: https://github.com/monostate/browsernative-python/releases/tag/v1.0.0