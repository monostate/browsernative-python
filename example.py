#!/usr/bin/env python3
"""
Example usage of Browser Native Python Client
"""

import os
from browsernative import BrowserNativeClient, quick_analyze

# Get your API key from https://bnca.monostate.ai
API_KEY = os.environ.get('BNCA_API_KEY', 'your-api-key-here')

def main():
    print("🌐 Browser Native Python Client Examples\n")
    
    # Example 1: Basic scraping
    print("Example 1: Basic Web Scraping")
    print("-" * 40)
    
    with BrowserNativeClient(API_KEY) as client:
        result = client.scrape('https://example.com')
        
        if result['success']:
            data = result['data']['data']
            print(f"Title: {data['title']}")
            print(f"Content length: {len(data.get('content', ''))} chars")
            print(f"Meta description: {data.get('metaDescription', 'N/A')}")
        else:
            print(f"Error: {result['error']}")
    
    # Example 2: AI-powered Q&A
    print("\n\nExample 2: AI-Powered Q&A")
    print("-" * 40)
    
    with BrowserNativeClient(API_KEY) as client:
        result = client.analyze(
            'https://news.ycombinator.com',
            'What are the top 3 stories on the homepage?'
        )
        
        if result['success']:
            print(f"Answer: {result['data']['answer']}")
        else:
            print(f"Error: {result['error']}")
    
    # Example 3: One-liner convenience function
    print("\n\nExample 3: Quick Analysis (One-liner)")
    print("-" * 40)
    
    result = quick_analyze(
        'https://github.com/anthropics/claude-code',
        'What is this repository about?',
        API_KEY
    )
    
    if result['success']:
        print(f"Answer: {result['data']['answer'][:200]}...")
    else:
        print(f"Error: {result['error']}")
    
    # Example 4: Batch processing
    print("\n\nExample 4: Batch Processing Multiple URLs")
    print("-" * 40)
    
    urls = [
        'https://python.org',
        'https://nodejs.org',
        'https://rust-lang.org'
    ]
    
    with BrowserNativeClient(API_KEY) as client:
        for url in urls:
            print(f"\nAnalyzing {url}...")
            result = client.analyze(url, 'What programming language is this about?')
            
            if result['success']:
                answer = result['data']['answer']
                print(f"→ {answer[:100]}...")
            else:
                print(f"→ Error: {result['error']}")

if __name__ == "__main__":
    main()