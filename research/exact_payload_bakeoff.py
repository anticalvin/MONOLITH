#!/usr/bin/env python3
"""Exact-payload QR Portrait architecture bake-off; no QArt dependencies."""
import csv, json, shutil, subprocess
from pathlib import Path
import cv2, numpy as np, qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'exact_payload_bakeoff_outputs'; URL='https://example.com'
SRC=Path('/private/tmp/monolith-handoff.bNSsS3/monolith-v3-sprint/outputs'); SAFE=ROOT/'benchmark_outputs'
NAMES={'astronaut':'astronaut_variant_00_source.png','camera':'camera_variant_00_source.png','cat':'cat_variant_00_source.png'}
VERSION=8; BOX=12; BORDER=4; SIDE=49

def matrix():
 q=qrcode.QRCode(version=VERSION,error_correction=ERROR_CORRECT_H,box_size=1,border=0);q.add_data(URL);q.make(fit=False)
 return np.asarray(q.modules,dtype=bool),q.best_mask_pattern()
def function_cell(x,y):
 # Preserve every finder/separator, timing, alignment, format, and version cell unstyled.
 if x<9 and y<9 or x>=SIDE-8 and y<9 or x<9 and y>=SIDE-8:return True
 if x==6 or y==6:return True
 if x==8 or y==8:return True
 if x>=SIDE-11 and y<6 or x<6 and y>=SIDE-11:return True
 for cx,cy in ((24,6),(6,24),(24,24),(42,24),(24,42),(42,42)):
  if abs(x-cx)<=2 and abs(y-cy)<=2:return True
 return False
def source_gray(p):return np.asarray(Image.open(p).convert('L').resize((SIDE,SIDE),Image.Resampling.LANCZOS),dtype=np.uint8)
def mask(n):return np.asarray(Image.open(ROOT/'qart-perceptual/phase2_outputs/masks'/f'{n}_subject_mask_49x49.png').convert('L'),dtype=np.uint8)/255
def canvas(m):
 size=(SIDE+2*BORDER)*BOX;im=Image.new('RGB',(size,size),'white');d=ImageDraw.Draw(im)
 for y in range(SIDE):
  for x in range(SIDE):
   if m[y,x]:d.rectangle((BORDER*BOX+x*BOX,BORDER*BOX+y*BOX,BORDER*BOX+(x+1)*BOX-1,BORDER*BOX+(y+1)*BOX-1),fill='black')
 return im
def halftone(m,photo,weight,alpha):
 im=canvas(m);d=ImageDraw.Draw(im)
 for y in range(SIDE):
  for x in range(SIDE):
   if function_cell(x,y):continue
   tone=photo[y,x]/255; importance=0.35+0.65*weight[y,x];xx=(BORDER+x)*BOX;yy=(BORDER+y)*BOX
   if m[y,x]:
    # White micro-dot preserves a black core; more visible in important bright source regions.
    radius=max(0,int((tone*importance*alpha)*3));
    if radius:d.ellipse((xx+1,yy+1,xx+1+2*radius,yy+1+2*radius),fill=(205,205,205))
   else:
    # Gray, never-black micro-dot keeps white modules decisively light.
    radius=max(0,int(((1-tone)*importance*alpha)*4));
    if radius:d.ellipse((xx+BOX-2-radius*2,yy+BOX-2-radius*2,xx+BOX-2,yy+BOX-2),fill=(175,175,175))
 return im
def guided(m,photo,weight,coverage):
 im=Image.new('RGB',((SIDE+2*BORDER)*BOX,)*2,'white');d=ImageDraw.Draw(im)
 for y in range(SIDE):
  for x in range(SIDE):
   xx=(BORDER+x)*BOX;yy=(BORDER+y)*BOX;tone=photo[y,x]/255;imp=weight[y,x]
   if function_cell(x,y):
    if m[y,x]:d.rectangle((xx,yy,xx+BOX-1,yy+BOX-1),fill='black')
    continue
   if m[y,x]:
    # Data bit remains a black centre; photographic tone controls rounded extent.
    size=max(7,int(BOX*(coverage+0.08*(1-tone)*imp)));off=(BOX-size)//2
    d.rounded_rectangle((xx+off,yy+off,xx+off+size-1,yy+off+size-1),radius=2,fill='black')
   else:
    # White data bit has only a pale, source-guided texture.
    gray=int(228-38*(1-tone)*imp);d.ellipse((xx+4,yy+4,xx+7,yy+7),fill=(gray,gray,gray))
 return im
def decode(path):
 im=cv2.imread(str(path));det=cv2.QRCodeDetector();found,points=det.detect(im);val=det.decode(im,points)[0] if found and points is not None else ''
 if not val:val=det.detectAndDecode(im)[0]
 zbar=subprocess.run(['zbarimg','--raw',str(path)],capture_output=True,text=True)
 zbar_value=zbar.stdout.strip() if zbar.returncode==0 else ''
 return {'detected':bool(found),'decoded':val,'exact_payload':val==URL,'zbar_decoded':zbar_value,'zbar_exact_payload':zbar_value==URL}
def variants(im):
 w,h=im.size
 return {'original':im,'half_scale':im.resize((w//2,h//2),Image.Resampling.LANCZOS),'blur_1px':im.filter(ImageFilter.GaussianBlur(1)),
  'rotate_3deg':im.rotate(3,resample=Image.Resampling.BICUBIC,fillcolor='white'),
  'perspective':im.transform((w,h),Image.Transform.PERSPECTIVE,(1,0,-7,0,1,-5,.00005,.00004),Image.Resampling.BICUBIC,fillcolor='white')}
def gate(path):
 tests={}
 for k,im in variants(Image.open(path).convert('RGB')).items():
  p=OUT/'_probe.png';im.save(p);tests[k]=decode(p);p.unlink(missing_ok=True)
 passes=sum(x['exact_payload'] and x['zbar_exact_payload'] for x in tests.values());return {'tests':tests,'passes':passes,'accepted':passes>=4}
def visual_metric(im,photo,weight):
 # Module-scale luminance correlation to the target; supporting rather than substituting visual review.
 a=np.asarray(im.convert('L')); crop=a[BORDER*BOX:(BORDER+SIDE)*BOX,BORDER*BOX:(BORDER+SIDE)*BOX].reshape(SIDE,BOX,SIDE,BOX).mean((1,3))
 return {'photo_luminance_correlation':round(float(np.corrcoef(crop.ravel(),photo.ravel())[0,1]),4),'weighted_tone_error':round(float(np.mean(np.abs(crop-photo)*(0.35+weight))),2)}
def sheet(chosen):
 out=Image.new('RGB',(4*250,3*275),'white');d=ImageDraw.Draw(out)
 for r,n in enumerate(NAMES):
  files=[OUT/NAMES[n],OUT/f'{n}_safe_core.png',Path(chosen[n]['halftone']['png']),Path(chosen[n]['guided']['png'])]
  titles=['source','safe core','halftone','guided']
  for c,(p,t) in enumerate(zip(files,titles)):
   im=Image.open(p).convert('RGB');im.thumbnail((240,240));out.paste(im,(c*250+(240-im.width)//2,r*275));d.text((c*250+4,r*275+244),f'{n} / {t}',fill='black')
 out.save(OUT/'architecture_bakeoff_sheet.png')
def main():
 OUT.mkdir(exist_ok=True);m,mask_pattern=matrix();all_rows=[];chosen={}
 for n,f in NAMES.items():
  src=SRC/f
  if not src.exists():src=OUT/f
  shutil.copy2(src,OUT/f);shutil.copy2(SAFE/f'{n}_safe_core.png',OUT/f'{n}_safe_core.png')
  photo=source_gray(src);w=mask(n);candidates={'halftone':[],'guided':[]}
  for kind,values in [('halftone',(0.45,0.8)),('guided',(0.82,0.92))]:
   for value in values:
    im=halftone(m,photo,w,value) if kind=='halftone' else guided(m,photo,w,value)
    p=OUT/f'{n}_{kind}_{str(value).replace(".","_")}.png';im.save(p);g=gate(p)
    record={'png':str(p),'parameter':value,'gate':g,'visual':visual_metric(im,photo,w)};candidates[kind].append(record);all_rows.append({'image':n,'experiment':kind,'parameter':value,'passes':g['passes'],'accepted':g['accepted'],**record['visual']})
  def best(k):
   passing=[x for x in candidates[k] if x['gate']['accepted']];return min(passing,key=lambda x:x['visual']['weighted_tone_error']) if passing else candidates[k][0]
  chosen[n]={'safe_core':{'png':str(OUT/f'{n}_safe_core.png'),'decode':decode(OUT/f'{n}_safe_core.png')},'halftone':best('halftone'),'guided':best('guided'),'candidates':candidates}
 result={'configuration':{'encoder':'python-qrcode','payload':URL,'version':VERSION,'error_correction':'H','mask_pattern':mask_pattern,'module_dimensions':SIDE,'module_px':BOX,'quiet_zone_modules':BORDER},'results':chosen}
 json.dump(result,open(OUT/'results.json','w'),indent=2)
 with open(OUT/'results.csv','w',newline='') as h:
  fields=list(all_rows[0]);cw=csv.DictWriter(h,fieldnames=fields);cw.writeheader();cw.writerows(all_rows)
 sheet(chosen);print(json.dumps({'output':str(OUT),'matrix_mask':mask_pattern},indent=2))
if __name__=='__main__':main()
