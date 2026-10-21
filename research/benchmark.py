#!/usr/bin/env python3
"""Offline evidence runner: no listeners, sockets, or shell interpolation."""
import csv,json,shutil,subprocess,time
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent; OUT=ROOT/"benchmark_outputs"; OUT.mkdir(exist_ok=True)
QART=ROOT/"qart"/"target"/"release"/"qart"; URL="https://example.com"
ARCH=Path("/private/tmp/monolith-handoff.bNSsS3/monolith-v3-sprint/outputs")
NAMES={"astronaut":"astronaut_variant_00_source.png","camera":"camera_variant_00_source.png","cat":"cat_variant_00_source.png","coffee":"coffee_variant_00_source.png","rocket":"rocket_variant_00_source.png"}
def decode(path):
    result={"zbar":"UNVERIFIED","opencv":"UNVERIFIED"}
    for binary,key in [("zbarimg","zbar")]:
        if shutil.which(binary):
            p=subprocess.run([binary,"--raw",str(path)],capture_output=True,text=True)
            result[key]=p.stdout.strip() if p.returncode==0 else "FAILED"
    try:
        import cv2
        value,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(path)))
        result["opencv"]=value or "FAILED"
    except Exception: pass
    return result
rows=[]
for name,filename in NAMES.items():
    source=ARCH/filename; safe=ARCH/(filename.replace("_source.png","_best.png"))
    # Exact existing V3 baseline output; preserved rather than re-rendered.
    if safe.exists(): shutil.copy2(safe,OUT/f"{name}_safe_core.png")
    qart=OUT/f"{name}_qart.png"; started=time.perf_counter()
    proc=subprocess.run([str(QART),"build","8",URL,str(source),str(qart),"--module-size","8"],capture_output=True,text=True)
    row={"image":name,"source":str(source),"qart_png":str(qart),"safe_core_png":str(OUT/f"{name}_safe_core.png"),"qart_returncode":proc.returncode,"qart_stdout":proc.stdout.strip(),"qart_stderr":proc.stderr.strip(),"qart_ms":round((time.perf_counter()-started)*1000,2)}
    row["qart_decode"]=decode(qart) if qart.exists() else {}
    row["safe_decode"]=decode(OUT/f"{name}_safe_core.png") if (OUT/f"{name}_safe_core.png").exists() else {}
    rows.append(row)
json.dump(rows,open(OUT/"results.json","w"),indent=2)
with open(OUT/"results.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["image","qart_returncode","qart_ms","qart_stdout","qart_stderr"],extrasaction="ignore");w.writeheader();w.writerows(rows)
# Inspection sheet: source, preserved safe-core, actual QArt output.
tiles=[]
for r in rows:
    tiles.append([Image.open(r["source"]).convert("RGB"),Image.open(r["safe_core_png"]).convert("RGB"),Image.open(r["qart_png"]).convert("RGB")])
W,H=900,5*330; sheet=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(sheet)
for i,(a,b,c) in enumerate(tiles):
    y=i*330; d.text((8,y+4),list(NAMES)[i],fill="black")
    for j,im in enumerate((a,b,c)):
        im.thumbnail((285,285));sheet.paste(im,(j*300+8,y+30))
sheet.save(OUT/"comparison_contact_sheet.png")
print(json.dumps({"outputs":str(OUT),"candidates":len(rows)},indent=2))
