"""
Portfolio Web Server - Pure Python Backend
Serves the portfolio website using HTML, CSS, and Server-Side Python.
Zero client-side JavaScript required.
"""

import http.server
import socketserver
import os
import mimetypes
from datetime import datetime, timezone, timedelta

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')

# Indian Standard Time (UTC+5:30) for Pune, India
IST = timezone(timedelta(hours=5, minutes=30))

mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("video/webm", ".webm")
mimetypes.add_type("text/css", ".css")

def get_pune_time_str():
    """Returns the current formatted time in Pune (IST)."""
    now = datetime.now(IST)
    return now.strftime("%I:%M %p")

def render_template():
    """Reads index.html and dynamically injects server-side computed variables."""
    if not os.path.exists(INDEX_PATH):
        return b"<h1>404 - index.html not found</h1>"
    
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pune_time = get_pune_time_str()
    # Inject live server-side variables
    content = content.replace("{{ LIVE_TIME }}", pune_time)
    
    return content.encode('utf-8')

class PortfolioHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP Request Handler for Portfolio Website."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Add caching, media streaming, and security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def do_GET(self):
        # Normalize route
        path = self.path.split('?')[0].split('#')[0]

        if path in ('/', '/index.html'):
            try:
                body = render_template()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as e:
                self.send_error(500, f"Template rendering error: {str(e)}")
                return
        
        # Handle time API if requested
        if path == '/api/time':
            time_str = get_pune_time_str()
            body = f'{{"city":"Pune","timezone":"IST","time":"{time_str}"}}'.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Serve static files (CSS, images, etc.)
        return super().do_GET()

def run_server(port=PORT):
    """Starts the Python Portfolio HTTP Server."""
    socketserver.TCPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("", port), PortfolioHTTPRequestHandler) as httpd:
        print(f"==================================================")
        print(f"  Portfolio Server (Pure HTML/CSS/Python) Running")
        print(f"  Local URL : http://localhost:{port}/")
        print(f"  Live Time : Pune (IST) • {get_pune_time_str()}")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully...")
            httpd.shutdown()

if __name__ == '__main__':
    run_server()
