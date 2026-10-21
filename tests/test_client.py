import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from browsernative import BrowserNativeClient, quick_scrape


class _Handler(BaseHTTPRequestHandler):
    hits = []

    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = json.loads(self.rfile.read(length) or b'{}')
        _Handler.hits.append({'path': self.path, 'headers': dict(self.headers), 'body': body})
        payload = json.dumps({'success': True, 'data': {'title': 'ok'}, 'metadata': {'contentStatus': 'usable', 'httpStatus': 200}}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


@pytest.fixture(scope='module')
def api():
    server = HTTPServer(('127.0.0.1', 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown()


def test_requires_base_url():
    with pytest.raises(ValueError, match='base_url is required'):
        BrowserNativeClient('key')
    with pytest.raises(ValueError, match='base_url is required'):
        BrowserNativeClient()


def test_rejects_non_http_base_url():
    with pytest.raises(ValueError, match='http'):
        BrowserNativeClient(base_url='key-looking-string')


def test_key_is_optional_and_header_only_when_set(api):
    _Handler.hits.clear()
    with_key = BrowserNativeClient(api_key='k1', base_url=api + '/')
    assert with_key.base_url == api
    result = with_key.scrape('https://example.test')
    assert result['success'] is True
    assert result['data']['metadata']['contentStatus'] == 'usable'
    assert _Handler.hits[0]['path'] == '/scrapeurl'
    assert _Handler.hits[0]['headers']['x-api-key'] == 'k1'
    assert '3.0.0' in _Handler.hits[0]['headers']['User-Agent']

    no_key = BrowserNativeClient(base_url=api)
    assert no_key.api_key is None
    no_key.scrape('https://example.test')
    assert 'x-api-key' not in _Handler.hits[1]['headers']


def test_convenience_function_with_base_url(api):
    _Handler.hits.clear()
    result = quick_scrape('https://example.test', 'k2', base_url=api)
    assert result['success'] is True
    assert _Handler.hits[0]['headers']['x-api-key'] == 'k2'
