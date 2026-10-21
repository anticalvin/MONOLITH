#!/usr/bin/env python3
"""QArt-aware binary-target experiments: QArt Gaussian-resizes then thresholds."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageOps,ImageEnhance,ImageFilter,ImageDraw
import cv2
R=Path(__file__).resolve().parent;Q=R/"qart/target/release/qart";O=R/"subject_outputs";O.mkdir(exist_ok=True);S=Path("/private/tmp/monolith-handoff.bNSsS3/monolith-v3-sprint/outputs")
files={"astronaut":"astronaut_variant_00_source.png","camera":"camera_variant_00_source.png","cat":"cat_variant_00_source.png"}
def prep(im,kind,name):
 im=im.convert("L");w,h=im.size;side=min(w,h);im=im.crop(((w-side)//2,(h-side)//2,(w+side)//2,(h+side)//2)).resize((700,700))
 if kind=="face": im=ImageEnhance.Contrast(ImageOps.autocontrast(im,cutoff=2)).enhance(1.6)
 if kind=="silhouette": im=ImageOps.posterize(ImageOps.autocontrast(im),2).filter(ImageFilter.GaussianBlur(1))
 if kind=="focal":
  # deterministic ROI: astronaut face upper-centre, camera face centre, cat eye upper-left.
  boxes={"astronaut":(190,60,500,380),"camera":(130,90,490,430),"cat":(20,40,430,450)}; b=boxes[name]; bg=im.filter(ImageFilter.GaussianBlur(5));roi=ImageEnhance.Contrast(im.crop(b)).enhance(1.8).filter(ImageFilter.UnsharpMask(2,140,4));bg.paste(roi,b);im=bg
 return im
rows=[]
for name,f in files.items():
 base=Image.open(S/f)
 for kind in ("face","silhouette","focal"):
  t=O/f"{name}_{kind}_target.png";prep(base,kind,name).save(t);out=O/f"{name}_{kind}_qart.png"
  p=subprocess.run([str(Q),"build","8","https://example.com",str(t),str(out),"--module-size","8"],capture_output=True,text=True)
  dec=cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(out)))[0] if out.exists() else ""
  rows.append({"image":name,"strategy":kind,"png":str(out),"decoded":dec or "FAILED","returncode":p.returncode})
json.dump(rows,open(O/"results.json","w"),indent=2)
sheet=Image.new("RGB",(1200,900),"white");d=ImageDraw.Draw(sheet)
for i,name in enumerate(files):
 d.text((5,i*300+5),name,fill="black")
 for j,kind in enumerate(("face","silhouette","focal")):
  im=Image.open(O/f"{name}_{kind}_qart.png").convert("RGB");im.thumbnail((270,270));sheet.paste(im,(j*400+20,i*300+25));d.text((j*400+20,i*300+280),kind,fill="black")
sheet.save(O/"subject_strategy_contact_sheet.png")
print(json.dumps(rows,indent=2))
