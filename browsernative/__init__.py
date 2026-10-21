"""
Browser Native Python Client SDK

A lightweight Python client for a self-hosted node-scraper API.
"""

from .client import (
    BrowserNativeClient,
    BrowserSession,
    quick_scrape,
    quick_screenshot,
    quick_analyze,
    quick_shot,
    bulk_scrape,
)

__version__ = "3.0.0"
__all__ = [
    "BrowserNativeClient",
    "BrowserSession",
    "quick_scrape",
    "quick_screenshot",
    "quick_analyze",
    "quick_shot",
    "bulk_scrape",
]