#!/usr/bin/env python3
"""Controlled QArt target preprocessing experiment (offline)."""
from pathlib import Path
import json, subprocess, time
from PIL import Image,ImageEnhance,ImageFilter,ImageOps,ImageDraw,ImageStat
import cv2
ROOT=Path(__file__).resolve().parent; QART=ROOT/"qart"/"target"/"release"/"qart"; OUT=ROOT/"quality_outputs"; OUT.mkdir(exist_ok=True)
SRC=Path("/private/tmp/monolith-handoff.bNSsS3/monolith-v3-sprint/outputs")
items={"astronaut":"astronaut_variant_00_source.png","camera":"camera_variant_00_source.png","cat":"cat_variant_00_source.png"}
def improve(src,dst):
 im=Image.open(src).convert("RGB"); w,h=im.size; side=min(w,h); # center-biased crop, preserving original file
 left=max(0,(w-side)//2); top=max(0,(h-side)//2); im=im.crop((left,top,left+side,top+side)).resize((700,700),Image.Resampling.LANCZOS)
 im=ImageOps.autocontrast(im,cutoff=1); im=ImageEnhance.Contrast(im).enhance(1.25); im=im.filter(ImageFilter.UnsharpMask(radius=2,percent=135,threshold=4)); im.save(dst)
def decode(p):
 v,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(p))); return v or "FAILED"
rows=[]
for name,f in items.items():
 original=SRC/f; target=OUT/(name+"_target.png"); improve(original,target)
 baseline=ROOT/"user_results"/name/"qart_portrait.png"; enhanced=OUT/(name+"_improved_qart.png"); st=time.perf_counter()
 r=subprocess.run([str(QART),"build","8","https://example.com",str(target),str(enhanced),"--module-size","8"],capture_output=True,text=True)
 rows.append({"image":name,"baseline":str(baseline),"target":str(target),"improved":str(enhanced),"ms":round((time.perf_counter()-st)*1000,2),"returncode":r.returncode,"decoded":decode(enhanced) if enhanced.exists() else "FAILED"})
json.dump(rows,open(OUT/"results.json","w"),indent=2)
sheet=Image.new("RGB",(1200,900),"white");d=ImageDraw.Draw(sheet)
for row,(name,f) in zip(rows,items.items()):
 y=300*list(items).index(name);d.text((8,y+6),name,fill="black")
 for x,p,label in [(0,SRC/f,"source"),(300,row["baseline"],"baseline"),(600,row["target"],"processed target"),(900,row["improved"],"improved QArt")]:
  im=Image.open(p).convert("RGB");im.thumbnail((280,260));sheet.paste(im,(x+10,y+30));d.text((x+10,y+285),label,fill="black")
sheet.save(OUT/"before_after_contact_sheet.png")
print(json.dumps(rows,indent=2))
