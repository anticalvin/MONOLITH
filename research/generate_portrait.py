#!/usr/bin/env python3
import argparse, base64, html, json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent; QART=ROOT/"qart"/"target"/"release"/"qart"; TYPES={".jpg",".jpeg",".png",".webp"}
def fail(s): print("Error: "+s,file=sys.stderr); raise SystemExit(2)
def main():
 p=argparse.ArgumentParser();p.add_argument("image",type=Path);p.add_argument("url");p.add_argument("output",type=Path);p.add_argument("--confirm-fragment-modification",action="store_true");p.add_argument("--version",type=int,default=8);a=p.parse_args()
 if not QART.is_file(): fail("QArt binary missing")
 if not a.image.is_file() or a.image.suffix.lower() not in TYPES or a.image.stat().st_size>8*1024*1024: fail("Use an existing JPEG, PNG, or WebP under 8 MB")
 if not a.url.startswith(("http://","https://")) or "#" in a.url: fail("Use an HTTP(S) URL without a fragment")
 if not a.confirm_fragment_modification: fail("QArt modifies URLs with a fragment; re-run with --confirm-fragment-modification")
 if not 1<=a.version<=40: fail("version must be 1-40")
 a.output.mkdir(parents=True,exist_ok=True);out=a.output/"qart_portrait.png";start=time.perf_counter()
 r=subprocess.run([str(QART),"build",str(a.version),a.url,str(a.image),str(out),"--module-size","8"],capture_output=True,text=True,timeout=30)
 if r.returncode: fail(r.stderr[-500:])
 try:
  import cv2; decoded=cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(out)))[0] or None
 except Exception: decoded=None
 status="DECODE FAILED" if not decoded else ("EXACT MATCH" if decoded==a.url else "DECODED / URL MODIFIED")
 report={"requested_url":a.url,"decoded_url":decoded,"status":status,"processing_ms":round((time.perf_counter()-start)*1000,2),"png":str(out),"returncode":r.returncode,"stdout":r.stdout,"stderr":r.stderr}
 (a.output/"report.json").write_text(json.dumps(report,indent=2))
 src="data:image/"+("png" if a.image.suffix.lower()==".png" else "jpeg")+";base64,"+base64.b64encode(a.image.read_bytes()).decode()
 page="<html><body style='font-family:Arial;background:#f3f2ee;padding:30px'><h1>MONOLITH / QART EXPERIMENTAL</h1><h2>"+html.escape(status)+"</h2><p>QArt appends a URL fragment; this is not byte-identical payload verification.</p><p>Requested: <code>"+html.escape(a.url)+"</code></p><p>Decoded: <code>"+html.escape(decoded or "UNVERIFIED")+"</code></p><p>Processing: "+str(report["processing_ms"])+" ms · <a href='qart_portrait.png'>PNG</a></p><div style='display:flex;gap:24px'><figure><img width=420 src='"+src+"'><figcaption>Source</figcaption></figure><figure><img width=420 src='qart_portrait.png'><figcaption>QArt output</figcaption></figure></div></body></html>"
 (a.output/"index.html").write_text(page);print(json.dumps(report,indent=2))
if __name__=="__main__":main()
