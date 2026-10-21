#!/usr/bin/env python3
"""Local-only QArt bridge. Never interpolates user input into a shell."""
import base64, json, os, subprocess, tempfile, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QART = ROOT / "qart" / "target" / "release" / "qart"
MAX_IMAGE = 8 * 1024 * 1024
MAX_BODY = MAX_IMAGE + 64 * 1024

class Handler(BaseHTTPRequestHandler):
    def _reply(self, status, payload):
        raw = json.dumps(payload).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.send_header("Access-Control-Allow-Headers", "Content-Type"); self.end_headers()
    def do_POST(self):
        if self.path != "/qart": return self._reply(404, {"error":"unknown endpoint"})
        if int(self.headers.get("Content-Length","0")) > MAX_BODY: return self._reply(413, {"error":"request too large"})
        try:
            data=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            url=data["url"]
            if not isinstance(url,str) or not url.startswith(("http://","https://")) or "?" in url or "#" in url: raise ValueError("QArt accepts a base http(s) URL without query or fragment")
            version=int(data.get("version",8))
            if not 1 <= version <= 40: raise ValueError("version must be 1-40")
            raw=base64.b64decode(data["image_base64"], validate=True)
            if len(raw)>MAX_IMAGE: raise ValueError("image exceeds 8 MB")
            if not QART.is_file(): raise RuntimeError("QArt binary missing; run cargo build --release in research/qart")
            with tempfile.TemporaryDirectory() as d:
                source=Path(d)/"source.png"; out=Path(d)/"qart.png"; source.write_bytes(raw)
                started=time.perf_counter()
                subprocess.run([str(QART),"build",str(version),url,str(source),str(out),"--module-size","8"],check=True,timeout=15,capture_output=True)
                encoded=base64.b64encode(out.read_bytes()).decode()
            self._reply(200,{"image_png_base64":encoded,"requested_url":url,"version":version,"processing_ms":round((time.perf_counter()-started)*1000,2),"verification":"UNVERIFIED","warning":"QArt appends a fragment to create encoding freedom; raw decoded content is not byte-identical to requested_url."})
        except subprocess.TimeoutExpired: self._reply(504,{"error":"QArt generation timed out"})
        except (ValueError,KeyError,base64.binascii.Error) as e: self._reply(400,{"error":str(e)})
        except subprocess.CalledProcessError as e: self._reply(500,{"error":"QArt failed","detail":e.stderr.decode(errors="replace")[-500:]})
        except Exception as e: self._reply(500,{"error":str(e)})

if __name__=="__main__":
    print("QArt local service: http://127.0.0.1:8766/qart")
    ThreadingHTTPServer(("127.0.0.1",8766),Handler).serve_forever()
