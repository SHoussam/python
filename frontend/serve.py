"""
Single-origin dev server for the StageLink frontend.

Serves the static files in this folder AND transparently forwards every
request beginning with /api/ to the Django backend at http://127.0.0.1:8000.

Because the browser only ever talks to ONE origin (this server), there is no
CORS problem and the Django session / CSRF cookies work normally.

Run it from the frontend/ folder:

    python serve.py

Then open:  http://127.0.0.1:8080/login.html

Change the ports below if needed. Nothing in the Django backend is modified.
"""

import http.server
import socketserver
import urllib.request
import urllib.error

FRONTEND_PORT = 8080
DJANGO_ORIGIN = "http://127.0.0.1:8000"

# Headers we must not copy back verbatim (hop-by-hop / handled by the server).
HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    # Serve static files relative to this script's directory.
    def __init__(self, *args, **kwargs):
        import os
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy("POST")
        else:
            self.send_error(404)

    def proxy(self, method):
        url = DJANGO_ORIGIN + self.path

        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else None

        # Forward the headers Django cares about (cookies, content-type, csrf).
        fwd = {}
        for h in ("Content-Type", "Cookie", "X-CSRFToken", "X-Requested-With", "Accept"):
            if self.headers.get(h):
                fwd[h] = self.headers.get(h)

        req = urllib.request.Request(url, data=body, headers=fwd, method=method)
        try:
            resp = urllib.request.urlopen(req)
            status = resp.status
            headers = resp.getheaders()
            payload = resp.read()
        except urllib.error.HTTPError as e:
            # Relay error responses (400/401/403/404...) including their body.
            status = e.code
            headers = e.headers.items()
            payload = e.read()
        except urllib.error.URLError:
            self.send_error(502, "Cannot reach Django at " + DJANGO_ORIGIN)
            return

        self.send_response(status)
        for k, v in headers:
            if k.lower() in HOP_BY_HOP:
                continue
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    with ThreadingServer(("127.0.0.1", FRONTEND_PORT), Handler) as httpd:
        print("StageLink frontend on  http://127.0.0.1:%d/login.html" % FRONTEND_PORT)
        print("Proxying /api/  ->  " + DJANGO_ORIGIN)
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()
