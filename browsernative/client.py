"""
Browser Native Client implementation
"""

import time
import json
import threading
from typing import Dict, Any, Optional, Union, List, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import urljoin, urlencode


USER_AGENT = 'Browser Native Python Client/3.0.0'


class BrowserNativeClient:
    """
    Client for a self-hosted node-scraper API (the HTTP/WebSocket service
    built on @monostate/node-scraper). There is no hosted default: you run
    the API and point the client at it.

    Args:
        api_key (str, optional): API key sent as x-api-key, if your deployment requires one
        base_url (str): Base URL of your API, e.g. 'http://localhost:3001' (required)
        timeout (int, optional): Request timeout in seconds. Defaults to 30
        retries (int, optional): Number of retries. Defaults to 2
        verbose (bool, optional): Enable verbose logging. Defaults to False
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        retries: int = 2,
        verbose: bool = False
    ):
        if not base_url:
            raise ValueError(
                'base_url is required. The hosted Browser Native API has been retired: '
                'run your own node-scraper API and point the client at it, e.g. '
                "BrowserNativeClient(base_url='http://localhost:3001', api_key='...')"
            )
        if not str(base_url).startswith(('http://', 'https://')):
            raise ValueError(
                f"base_url must be an http(s) URL, got {base_url!r}. "
                "Note: the first positional argument is api_key; pass base_url by keyword."
            )

        self.api_key = api_key or None
        self.base_url = str(base_url).rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.verbose = verbose

        # Set up session for connection pooling
        self.session = requests.Session()
        headers = {'User-Agent': USER_AGENT}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        self.session.headers.update(headers)
    
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
    
    def create_session(
        self,
        mode: str = 'auto',
        screen_width: Optional[int] = None,
        screen_height: Optional[int] = None,
    ) -> 'BrowserSession':
        """
        Create a persistent browser session via WebSocket.

        Args:
            mode: Browser mode - 'auto', 'headless', 'visual', or 'computer-use' (default: 'auto')
            screen_width: Screen width for computer-use mode
            screen_height: Screen height for computer-use mode

        Returns:
            BrowserSession: Connected browser session
        """
        ws_url = self.base_url.replace('https://', 'wss://').replace('http://', 'ws://')
        query = {'mode': mode}
        if self.api_key:
            query['apiKey'] = self.api_key
        if screen_width is not None:
            query['screenWidth'] = str(screen_width)
        if screen_height is not None:
            query['screenHeight'] = str(screen_height)
        params = urlencode(query)
        url = f"{ws_url}/session?{params}"

        session = BrowserSession(url, verbose=self.verbose)
        session.connect()
        return session

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


class BrowserSession:
    """
    Persistent browser session over WebSocket.

    Provides real-time browser control with methods for navigation,
    interaction, screenshots, and content extraction.
    """

    def __init__(self, url: str, verbose: bool = False):
        self._url = url
        self._ws = None
        self._next_id = 1
        self._pending = {}  # id -> threading.Event, result holder
        self._verbose = verbose
        self._event_handlers = {}
        self.session_id = None
        self.backend = None
        self.vnc_url = None
        self._lock = threading.Lock()
        self._recv_thread = None

    def connect(self, timeout: float = 15.0):
        """Connect to the session WebSocket."""
        try:
            import websocket
        except ImportError:
            raise ImportError(
                'websocket-client package required for sessions. '
                'Install it: pip install websocket-client'
            )

        connected = threading.Event()
        connect_error = [None]

        self._ws = websocket.WebSocketApp(
            self._url,
            on_message=lambda ws, msg: self._on_message(msg, connected),
            on_error=lambda ws, err: self._on_error(err, connected, connect_error),
            on_close=lambda ws, code, reason: self._on_close(code, reason),
        )

        self._recv_thread = threading.Thread(
            target=self._ws.run_forever, daemon=True
        )
        self._recv_thread.start()

        if not connected.wait(timeout):
            self._ws.close()
            if connect_error[0]:
                raise ConnectionError(f"WebSocket connection failed: {connect_error[0]}")
            raise ConnectionError("WebSocket connection timed out")

        if connect_error[0]:
            raise ConnectionError(f"WebSocket connection failed: {connect_error[0]}")

    def _on_message(self, raw_data, connected_event=None):
        try:
            msg = json.loads(raw_data)
        except json.JSONDecodeError:
            return

        if msg.get('type') == 'connected':
            self.session_id = msg.get('sessionId')
            self.backend = msg.get('backend')
            self.vnc_url = msg.get('vncUrl')
            if self._verbose:
                print(f"Browser Native: Session {self.session_id} connected ({self.backend})")
            if connected_event:
                connected_event.set()
            return

        if msg.get('type') == 'fallback':
            self.backend = msg.get('to')
            if self._verbose:
                print(f"Browser Native: Fallback {msg.get('from')} -> {msg.get('to')} ({msg.get('reason')})")
            handler = self._event_handlers.get('fallback')
            if handler:
                handler(msg)
            return

        if msg.get('type') == 'closed':
            if self._verbose:
                print(f"Browser Native: Session closed ({msg.get('reason')})")
            handler = self._event_handlers.get('closed')
            if handler:
                handler(msg)
            return

        msg_id = msg.get('id')
        if msg_id is not None and msg_id in self._pending:
            entry = self._pending.pop(msg_id)
            if msg.get('backend'):
                self.backend = msg['backend']
            if msg.get('type') == 'error':
                entry['error'] = msg.get('message', 'Unknown error')
            else:
                entry['data'] = msg.get('data')
            entry['event'].set()

    def _on_error(self, error, connected_event=None, connect_error=None):
        if connect_error is not None:
            connect_error[0] = str(error)
        if connected_event:
            connected_event.set()

    def _on_close(self, code, reason):
        with self._lock:
            for entry in self._pending.values():
                entry['error'] = f"Session closed: {reason or 'unknown'}"
                entry['event'].set()
            self._pending.clear()

    def _send(self, action: str, timeout: float = 30.0, **params) -> Any:
        """Send an action and wait for the response."""
        if not self._ws or not self._recv_thread or not self._recv_thread.is_alive():
            raise ConnectionError("Session not connected")

        with self._lock:
            msg_id = self._next_id
            self._next_id += 1
            event = threading.Event()
            entry = {'event': event, 'data': None, 'error': None}
            self._pending[msg_id] = entry

        payload = {'id': msg_id, 'action': action, **params}
        self._ws.send(json.dumps(payload))

        if not event.wait(timeout):
            self._pending.pop(msg_id, None)
            raise TimeoutError(f"Action '{action}' timed out after {timeout}s")

        if entry['error']:
            raise RuntimeError(entry['error'])
        return entry['data']

    def on(self, event: str, handler: Callable):
        """Register an event handler for 'fallback' or 'closed' events."""
        self._event_handlers[event] = handler
        return self

    def goto(self, url: str) -> Any:
        return self._send('goto', url=url)

    def click(self, selector: str, **options) -> Any:
        return self._send('click', selector=selector, **options)

    def type(self, selector: str, text: str, **options) -> Any:
        return self._send('type', selector=selector, text=text, **options)

    def scroll(self, direction: str = 'down', amount: int = 500) -> Any:
        return self._send('scroll', direction=direction, amount=amount)

    def hover(self, selector: str) -> Any:
        return self._send('hover', selector=selector)

    def select(self, selector: str, *values: str) -> Any:
        return self._send('select', selector=selector, values=list(values))

    def press_key(self, key: str) -> Any:
        return self._send('pressKey', key=key)

    def go_back(self) -> Any:
        return self._send('goBack')

    def go_forward(self) -> Any:
        return self._send('goForward')

    def screenshot(self, **options) -> Any:
        return self._send('screenshot', **options)

    def get_page_state(self, **options) -> Any:
        return self._send('getPageState', **options)

    def extract_content(self) -> Any:
        return self._send('extractContent')

    def wait_for(self, selector: str, timeout: Optional[float] = None) -> Any:
        params = {'selector': selector}
        if timeout is not None:
            params['timeout'] = timeout
        return self._send('waitFor', **params)

    def evaluate(self, fn: str) -> Any:
        return self._send('evaluate', fn=fn)

    def get_cookies(self) -> Any:
        return self._send('getCookies')

    def set_cookies(self, cookies: List[Dict]) -> Any:
        return self._send('setCookies', cookies=cookies)

    # Coordinate-based actions (computer-use mode)

    def mouse_move(self, x: int, y: int) -> Any:
        return self._send('mouseMove', x=x, y=y)

    def click_at(self, x: int, y: int, button: str = 'left') -> Any:
        return self._send('clickAt', x=x, y=y, button=button)

    def double_click_at(self, x: int, y: int, button: str = 'left') -> Any:
        return self._send('doubleClickAt', x=x, y=y, button=button)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Any:
        return self._send('drag', startX=start_x, startY=start_y, endX=end_x, endY=end_y)

    def scroll_at(self, x: int, y: int, direction: str, amount: int = 3) -> Any:
        return self._send('scrollAt', x=x, y=y, direction=direction, amount=amount)

    def type_text(self, text: str) -> Any:
        return self._send('typeText', text=text)

    def get_cursor_position(self) -> Any:
        return self._send('getCursorPosition')

    def get_screen_size(self) -> Any:
        return self._send('getScreenSize')

    def close(self):
        """Close the session."""
        if self._ws:
            self._ws.close()
            self._ws = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions

def quick_scrape(url: str, api_key: Optional[str] = None, **options) -> Dict[str, Any]:
    """
    Convenience function for quick scraping without instantiating a client.
    
    Args:
        url (str): The URL to scrape
        api_key (str, optional): API key, if your deployment requires one. Pass base_url=... in options.
        **options: Additional options
        
    Returns:
        dict: Scraping result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.scrape(url, **options)


def quick_screenshot(url: str, api_key: Optional[str] = None, **options) -> Dict[str, Any]:
    """
    Convenience function for taking screenshots.
    
    Args:
        url (str): The URL to capture
        api_key (str, optional): API key, if your deployment requires one. Pass base_url=... in options.
        **options: Additional options
        
    Returns:
        dict: Screenshot result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.screenshot(url, **options)


def quick_analyze(url: str, question: str, api_key: Optional[str] = None, **options) -> Dict[str, Any]:
    """
    Convenience function for AI analysis.
    
    Args:
        url (str): The URL to analyze
        question (str): The question to answer
        api_key (str, optional): API key, if your deployment requires one. Pass base_url=... in options.
        **options: Additional options
        
    Returns:
        dict: Analysis result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.analyze(url, question, **options)


def quick_shot(url: str, api_key: Optional[str] = None, **options) -> Dict[str, Any]:
    """
    Convenience function for quick screenshot capture.

    Args:
        url (str): The URL to capture
        api_key (str, optional): API key, if your deployment requires one. Pass base_url=... in options.
        **options: Additional options

    Returns:
        dict: Screenshot result
    """
    with BrowserNativeClient(api_key, **options) as client:
        return client.quickshot(url, **options)


def bulk_scrape(
    urls: List[str],
    api_key: Optional[str] = None,
    concurrency: int = 5,
    continue_on_error: bool = True,
    progress_callback: Optional[Callable] = None,
    **options
) -> Dict[str, Any]:
    """
    Convenience function for bulk scraping multiple URLs.

    Args:
        urls: List of URLs to scrape
        api_key: API key, if your deployment requires one. Pass base_url=... in options.
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