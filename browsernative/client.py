"""
Browser Native Client implementation
"""

import time
import json
from typing import Dict, Any, Optional, Union, List, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import urljoin


class BrowserNativeClient:
    """
    Browser Native Client for web scraping with intelligent fallback system.
    
    Args:
        api_key (str): Your Browser Native API key
        base_url (str, optional): API base URL. Defaults to 'https://bnca-api.fly.dev'
        timeout (int, optional): Request timeout in seconds. Defaults to 30
        retries (int, optional): Number of retries. Defaults to 2
        verbose (bool, optional): Enable verbose logging. Defaults to False
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://bnca-api.fly.dev',
        timeout: int = 30,
        retries: int = 2,
        verbose: bool = False
    ):
        if not api_key:
            raise ValueError('API key is required. Get one at https://bnca.monostate.ai')
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.verbose = verbose
        
        # Set up session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key,
            'User-Agent': 'Browser Native Python Client/2.0.0'
        })
    
    def scrape(self, url: str, **options) -> Dict[str, Any]:
        """
        Scrape a webpage and extract structured content.
        
        Args:
            url (str): The URL to scrape
            **options: Additional options (e.g., include_screenshot=True)
            
        Returns:
            dict: Scraping result with data, method, and performance metrics
        """
        payload = {
            'url': url,
            'screenshot': options.get('include_screenshot', False),
            **options
        }
        
        result = self._make_request('/scrapeurl', payload)
        
        # Normalize the response structure
        if result['success'] and 'data' in result:
            api_response = result['data']
            # Check if method is nested in the data
            if 'data' in api_response and isinstance(api_response['data'], dict):
                if 'method' not in api_response and 'method' in api_response['data']:
                    api_response['method'] = api_response['data']['method']
        
        return result
    
    def screenshot(self, url: str, **options) -> Dict[str, Any]:
        """
        Scrape a webpage and take a screenshot.
        
        Args:
            url (str): The URL to scrape
            **options: Screenshot options
            
        Returns:
            dict: Screenshot result with base64 image
        """
        payload = {
            'url': url,
            'screenshot': True,
            **options
        }
        
        return self._make_request('/scrapeurl', payload)
    
    def quickshot(self, url: str, **options) -> Dict[str, Any]:
        """
        Quick screenshot capture - optimized for speed.
        
        Args:
            url (str): The URL to capture
            **options: Screenshot options
            
        Returns:
            dict: Screenshot result
        """
        payload = {
            'url': url,
            **options
        }
        
        return self._make_request('/quickshot', payload)
    
    def analyze(self, url: str, question: str, **options) -> Dict[str, Any]:
        """
        Extract content and answer questions using AI.
        
        Args:
            url (str): The URL to analyze
            question (str): The question to answer
            **options: Analysis options (e.g., include_screenshot=True)
            
        Returns:
            dict: AI analysis result
        """
        payload = {
            'url': url,
            'question': question,
            'screenshot': options.get('include_screenshot', False),
            **options
        }
        
        return self._make_request('/aireply', payload)
    
    def bulk_scrape(
        self,
        urls: List[str],
        concurrency: int = 5,
        continue_on_error: bool = True,
        progress_callback: Optional[Callable] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            concurrency: Max concurrent requests (default: 5)
            continue_on_error: Keep going on failures (default: True)
            progress_callback: Called with {'processed', 'total', 'percentage'}
            **options: Passed through to scrape()

        Returns:
            dict with 'results' list and 'stats' summary
        """
        results = []
        start_time = time.time()
        processed = 0

        def _scrape_one(url):
            try:
                result = self.scrape(url, **options)
                return {'url': url, **result}
            except Exception as e:
                return {'url': url, 'success': False, 'error': str(e)}

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(_scrape_one, url): url for url in urls}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                processed += 1
                if progress_callback:
                    progress_callback({
                        'processed': processed,
                        'total': len(urls),
                        'percentage': (processed / len(urls)) * 100,
                    })
                if not continue_on_error and not result.get('success'):
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

        successful = sum(1 for r in results if r.get('success'))
        total_time = int((time.time() - start_time) * 1000)
        return {
            'results': results,
            'stats': {
                'total': len(urls),
                'successful': successful,
                'failed': len(results) - successful,
                'totalTime': total_time,
                'averageTime': total_time // max(len(results), 1),
            },
        }

    def get_usage(self, days: int = 30) -> Dict[str, Any]:
        """
        Get account usage statistics.
        
        Args:
            days (int): Number of days to fetch (max 30)
            
        Returns:
            dict: Usage statistics
        """
        return self._make_request('/stats', method='GET')
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health and your account status.
        
        Returns:
            dict: Health check result
        """
        return self._make_request('/health', method='GET')
    
    def _make_request(
        self, 
        endpoint: str, 
        payload: Optional[Dict] = None,
        method: str = 'POST'
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the API.
        
        Args:
            endpoint (str): API endpoint
            payload (dict, optional): Request payload
            method (str): HTTP method
            
        Returns:
            dict: API response
        """
        url = urljoin(self.base_url, endpoint)
        start_time = time.time()
        
        last_error = None
        
        for attempt in range(1, self.retries + 2):
            try:
                if self.verbose:
                    print(f"Browser Native: {method} {url} (attempt {attempt})")
                
                if method == 'GET':
                    response = self.session.get(url, timeout=self.timeout)
                else:
                    response = self.session.post(
                        url, 
                        json=payload,
                        timeout=self.timeout
                    )
                
                response_time = int((time.time() - start_time) * 1000)
                
                if response.ok:
                    data = response.json()
                    
                    if self.verbose:
                        print(f"Browser Native: Request completed in {response_time}ms")
                    
                    # Check if API returned an error in the response body
                    if isinstance(data, dict) and data.get('error'):
                        return {
                            'success': False,
                            'error': data['error'],
                            'responseTime': response_time
                        }
                    
                    return {
                        'success': True,
                        'data': data,
                        'responseTime': response_time,
                        'attempt': attempt
                    }
                else:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    error_message = error_data.get('error', response.reason)
                    raise Exception(f"API Error ({response.status_code}): {error_message}")
                    
            except requests.Timeout:
                last_error = "Request timeout"
            except Exception as e:
                last_error = str(e)
                
            # Retry logic
            if attempt <= self.retries:
                delay = 2 ** (attempt - 1)  # Exponential backoff
                if self.verbose:
                    print(f"Browser Native: Attempt {attempt} failed, retrying in {delay}s...")
                time.sleep(delay)
            else:
                break
        
        # All retries failed
        response_time = int((time.time() - start_time) * 1000)
        return {
            'success': False,
            'error': last_error or 'Request failed',
            'responseTime': response_time
        }
    
    def close(self):
        """Close the session to free up resources."""
        self.session.close()
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up on context exit."""
        self.close()


# Convenience functions

def quick_scrape(url: str, api_key: str, **options) -> Dict[str, Any]:
    """
    Convenience function for quick scraping without instantiating a client.
    
    Args:
        url (str): The URL to scrape
        api_key (str): Your API key
        **options: Additional options
        
    Returns:
        dict: Scraping result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.scrape(url, **options)


def quick_screenshot(url: str, api_key: str, **options) -> Dict[str, Any]:
    """
    Convenience function for taking screenshots.
    
    Args:
        url (str): The URL to capture
        api_key (str): Your API key
        **options: Additional options
        
    Returns:
        dict: Screenshot result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.screenshot(url, **options)


def quick_analyze(url: str, question: str, api_key: str, **options) -> Dict[str, Any]:
    """
    Convenience function for AI analysis.
    
    Args:
        url (str): The URL to analyze
        question (str): The question to answer
        api_key (str): Your API key
        **options: Additional options
        
    Returns:
        dict: Analysis result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.analyze(url, question, **options)


def quick_shot(url: str, api_key: str, **options) -> Dict[str, Any]:
    """
    Convenience function for quick screenshot capture.

    Args:
        url (str): The URL to capture
        api_key (str): Your API key
        **options: Additional options

    Returns:
        dict: Screenshot result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.quickshot(url, **options)


def bulk_scrape(
    urls: List[str],
    api_key: str,
    concurrency: int = 5,
    continue_on_error: bool = True,
    progress_callback: Optional[Callable] = None,
    **options
) -> Dict[str, Any]:
    """
    Convenience function for bulk scraping multiple URLs.

    Args:
        urls: List of URLs to scrape
        api_key: Your API key
        concurrency: Max concurrent requests (default: 5)
        continue_on_error: Keep going on failures (default: True)
        progress_callback: Called with progress dict
        **options: Passed through to scrape()

    Returns:
        dict with 'results' list and 'stats' summary
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.bulk_scrape(
            urls,
            concurrency=concurrency,
            continue_on_error=continue_on_error,
            progress_callback=progress_callback,
            **options,
        )