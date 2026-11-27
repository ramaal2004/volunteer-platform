import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"opportunities": [], "applications": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class VolunteerRequestHandler(SimpleHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_json(200, {"status": "ok"})

    def do_GET(self):
        if self.path == "/api/opportunities":
            data = load_data()
            self._send_json(200, data["opportunities"])
        elif self.path == "/api/applications":
            data = load_data()
            self._send_json(200, data["applications"])
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/apply":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                application = json.loads(body)
                if not application.get("student_name") or not application.get("opportunity_id"):
                    self._send_json(400, {"error": "يرجى إدخال اسم الطالب ورقم الفرصة"})
                    return

                data = load_data()
                application["id"] = len(data["applications"]) + 1
                data["applications"].append(application)
                save_data(data)

                self._send_json(201, {
                    "message": "تم تسجيل طلب التطوع بنجاح",
                    "application": application
                })
            except json.JSONDecodeError:
                self._send_json(400, {"error": "بيانات غير صالحة"})
        else:
            self._send_json(404, {"error": "المسار غير موجود"})

if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("127.0.0.1", port), VolunteerRequestHandler)
    print(f"Server running on http://127.0.0.1:{port}")
    server.serve_forever()