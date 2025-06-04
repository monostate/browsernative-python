"""
Browser Native Python Client SDK

A lightweight Python client for the Browser Native web scraping API.
Works with Python 3.7+ and supports async/await.
"""

from .client import (
    BrowserNativeClient,
    quick_scrape,
    quick_screenshot,
    quick_analyze,
    quick_shot
)

__version__ = "1.0.0"
__all__ = [
    "BrowserNativeClient",
    "quick_scrape",
    "quick_screenshot", 
    "quick_analyze",
    "quick_shot"
]