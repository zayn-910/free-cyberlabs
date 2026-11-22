import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class DirectoryHandler(BaseHTTPRequestHandler):
    server_version = "CedarDirectory/1.0"
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
        if self.headers.get("X-Clinic-Role") != "operations":
            self.send_json(
                403,
                {"error": "Operations role required", "author": "zayn-910"},
            )
            return
        if self.path == "/":
            self.send_json(
                200,
                {
                    "service": "Cedar Ridge Staff Directory",
                    "resources": [
                        {
                            "title": "Morning staff briefing",
                            "path": "/api/v1/staff/briefing",
                            "format": "application/json",
                        }
                    ],
                    "author": "zayn-910",
                },
            )
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
                    "author": "zayn-910",
                },
            )
            return
        self.send_json(404, {"error": "Not found", "author": "zayn-910"})

    def log_message(self, format, *args):
        print("directory: " + format % args, flush=True)


if __name__ == "__main__":
    print("Cedar Ridge directory ready | Lab by zayn-910", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8081), DirectoryHandler).serve_forever()
