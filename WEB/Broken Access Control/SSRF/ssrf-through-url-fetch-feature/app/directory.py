import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class DirectoryHandler(BaseHTTPRequestHandler):
    server_version = "CedarDirectory/1.0"

    def send_json(self, status, body):
        content = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == "/":
            self.send_json(
                200,
                {
                    "service": "Cedar Ridge staff directory",
                    "resources": [
                        {
                            "name": "Morning staff briefing",
                            "path": "/api/v1/staff/briefing",
                            "format": "application/json",
                        }
                    ],
                },
            )
            return
        if self.path == "/health":
            self.send_json(200, {"status": "ok"})
            return
        if self.path == "/api/v1/staff/briefing":
            try:
                with open("/run/lab/receipt", "r", encoding="utf-8") as record:
                    code = record.read().strip()
            except OSError:
                self.send_json(503, {"error": "Briefing is not ready"})
                return
            self.send_json(
                200,
                {
                    "department": "Clinic operations",
                    "published": "08:00",
                    "note": "Morning operations briefing",
                    "access_code": code,
                },
            )
            return
        self.send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        print("directory: " + format % args, flush=True)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8081), DirectoryHandler).serve_forever()
