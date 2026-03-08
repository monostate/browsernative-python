"""
Browser Native Python Client SDK

A lightweight Python client for the Browser Native web scraping API.
"""

from .client import (
    BrowserNativeClient,
    quick_scrape,
    quick_screenshot,
    quick_analyze,
    quick_shot,
    bulk_scrape,
)

__version__ = "2.0.0"
__all__ = [
    "BrowserNativeClient",
    "quick_scrape",
    "quick_screenshot",
    "quick_analyze",
    "quick_shot",
    "bulk_scrape",
]