#!/usr/bin/env python3
"""Local preview with a same-origin live API; no third-party dependencies."""
import http.server, json, pathlib, sys, time, threading
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from collect import collect, DATA, ROOT
lock=threading.Lock()
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'web'),**kwargs)
    def do_GET(self):
        if self.path.split('?')[0]=='/api/state':
            try:
                with lock:
                    path=DATA/'realtime.json'
                    if not path.exists() or time.time()-path.stat().st_mtime>20: collect()
                    payload=path.read_bytes()
                self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(payload)
            except Exception as exc:
                self.send_error(502,str(exc))
        else: super().do_GET()
if __name__=='__main__':
    print('Vista previa: http://127.0.0.1:8080',flush=True)
    http.server.ThreadingHTTPServer(('127.0.0.1',8080),Handler).serve_forever()
