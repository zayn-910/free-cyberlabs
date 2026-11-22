import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HandbookHandler(BaseHTTPRequestHandler):
    server_version = "CedarHandbook/1.0"
    sys_version = "Lab by zayn-910"

    def end_headers(self):
        self.send_header("X-Lab-Author", "zayn-910")
        super().end_headers()

    def send_json(self, status, body):
        content = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "author": "zayn-910"})
            return
        if self.path == "/":
            self.send_json(
                200,
                {
                    "service": "Cedar Ridge Handbook",
                    "resources": [
                        {
                            "title": "Current clinic bulletin",
                            "path": "/bulletins/current",
                            "format": "application/json",
                        },
                        {
                            "title": "Patient privacy guide",
                            "path": "/policies/privacy",
                            "format": "text/plain",
                        },
                    ],
                    "author": "zayn-910",
                },
            )
            return
        if self.path == "/bulletins/current":
            self.send_json(
                200,
                {
                    "title": "Current clinic bulletin",
                    "updated": "08:00",
                    "items": ["Pharmacy opens at 08:30", "Staff meeting at noon"],
                    "author": "zayn-910",
                },
            )
            return
        if self.path == "/policies/privacy":
            self.send_json(
                200,
                {
                    "title": "Patient privacy guide",
                    "updated": "2026-06-17",
                    "summary": "Keep printed records in approved clinic storage.",
                    "author": "zayn-910",
                },
            )
            return
        self.send_json(404, {"error": "Not found", "author": "zayn-910"})

    def log_message(self, format, *args):
        print("handbook: " + format % args, flush=True)


if __name__ == "__main__":
    print("Cedar Ridge handbook ready | Lab by zayn-910", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8082), HandbookHandler).serve_forever()
