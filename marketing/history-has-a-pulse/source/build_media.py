"""Local edit bench: real footage + brand typography, no synthesized motion."""
from pathlib import Path
import subprocess,sys,shutil,json,hashlib
import argparse,tempfile
from fontTools.ttLib import TTFont
ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--ffmpeg');args=ap.parse_args()
if args.ffmpeg: FF=args.ffmpeg
else:
 import imageio_ffmpeg
 FF=imageio_ffmpeg.get_ffmpeg_exe()
K=Path(__file__).resolve().parents[1];R=K.parents[1];M=R/'site/media/press'
W=R/'work/media';T=W/'video';T.mkdir(parents=True,exist_ok=True);(W/'fonts').mkdir(exist_ok=True);(W/'review').mkdir(exist_ok=True)
for p in (R/'site/fonts').glob('*.woff2'):
 f=TTFont(p);f.flavor=None;f.save(W/'fonts'/(p.stem+'.ttf'))
for p in (K/'source/endcards').glob('*.png'):shutil.copy2(p,W/'review'/p.name)
IN=args.source_dir.resolve()
GRADE='eq=contrast=1.08:brightness=-0.025:saturation=0.62:gamma=1.02,colorbalance=rs=.025:gs=.009:bs=-.02:rh=.025:bh=-.025,unsharp=5:5:0.25:3:3:0'
def run(args):
 p=subprocess.run([FF,'-y','-hide_banner','-loglevel','error',*map(str,args)],cwd=W,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-5000:])
def base(w,h):return f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30,{GRADE}'
def encode(args,out):run([*args,'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-map_metadata','-1','-movflags','+faststart',out])
for src,name,w,h,t in [('7243','wide',1280,720,5.5),('7249','portrait',720,1280,6.5)]:
 encode(['-ss','0.2','-i',IN/f'IMG_{src}.MOV','-t',str(t),'-map','0:v:0','-an','-vf',base(w,h)],M/f'press-loop-{name}.mp4')
 print('web loop',name,flush=True)
# Format conversions of the approved enhanced asset; provenance lives with the source.
for name,size in [('press-poster',1672),('press-portrait',1672)]:run(['-i',K/'artwork/press-portrait-enhanced.png','-vf',f'scale={size}:-2','-frames:v','1','-q:v','3',M/f'{name}.jpg'])
run(['-i',K/'social/pulse-linkedin.png','-frames:v','1','-q:v','2',M/'share-card.jpg'])

def clip(src,start,duration,w,h,out,title,subtitle,index):
 text=T/f'text-{index}.txt';text.write_text(title,encoding='utf-8')
 sub=T/f'sub-{index}.txt';sub.write_text(subtitle,encoding='utf-8')
 vert=h>w; size=82 if vert else 70 if w>1200 else 58
 margin=86 if vert else 80 if w>1200 else 60
 bottom=int(h*.21) if vert else 82
 # A quiet opaque caption band ensures consistent readability over moving steel.
 vf=base(w,h)+f',drawbox=x=0:y={h-bottom-160}:w=iw:h={bottom+160}:color=0x17130f@0.8:t=fill'
 vf+=f",drawtext=fontfile='fonts/LibreCaslonDisplay-400.ttf':textfile='video/text-{index}.txt':fontsize={size}:fontcolor=0xfaf6ea:x={margin}:y={h-bottom-132}"
 vf+=f",drawtext=fontfile='fonts/IBMPlexMono-400.ttf':textfile='video/sub-{index}.txt':fontsize={22 if vert else 18}:fontcolor=0xe4cfad:x={margin}:y={h-bottom-36}"
 vf+=f",drawtext=fontfile='fonts/IBMPlexMono-400.ttf':text='THOMAS BROADSIDE CO.':fontsize={22 if vert else 19}:fontcolor=0xfaf6ea:x={margin}:y={int(h*.13) if vert else 60}:box=1:boxcolor=0x17130f@0.7:boxborderw=14"
 encode(['-ss',str(start),'-i',IN/f'IMG_{src}.MOV','-t',str(duration),'-map','0:v:0','-map','0:a:0','-vf',vf,'-af',f'highpass=f=80,lowpass=f=11000,loudnorm=I=-20:TP=-2:LRA=7,afade=t=in:d=0.12,afade=t=out:st={duration-.25}:d=0.25'],out)

for name,w,h,segments in [('wide',1920,1080,[('7243',.3,5,'History has a pulse.','A WORKING PRESS / AUSTIN, TEXAS'),('7249',.5,5,'Printed here.','THOMAS GRAPHICS / THE SHOP FLOOR'),('7241',6.3,4,'A trade, carried forward.','FROM THE PRESS TO THE FINISHING ROOM')]),('vertical',1080,1920,[('7249',.5,4,'History has a pulse.','AUSTIN, TEXAS'),('7241',6.3,3,'A working shop.','A TRADE, CARRIED FORWARD'),('7243',.8,3,'Printed here.','THOMAS GRAPHICS / AUSTIN')]),('square',1080,1080,[('7243',.4,4,'History has a pulse.','AUSTIN, TEXAS'),('7249',.5,3,'A working shop.','A TRADE, CARRIED FORWARD'),('7241',6.3,3,'Printed here.','THOMAS GRAPHICS / AUSTIN')])]:
 parts=[]
 for i,(src,start,dur,title,sub) in enumerate(segments):
  out=T/f'{name}-{i}.mp4';clip(src,start,dur,w,h,out,title,sub,f'{name}-{i}');parts.append(out);print(out.name,flush=True)
 if name=='wide':
  out=T/'wide-portrait.mp4'
  encode(['-loop','1','-i',K/'artwork/press-portrait-enhanced.png','-ss','1','-i',IN/'IMG_7243.MOV','-t','5','-map','0:v:0','-map','1:a:0','-vf',f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30,drawbox=x=0:y=860:w=iw:h=220:color=0x17130f@0.85:t=fill,drawtext=fontfile=fonts/LibreCaslonDisplay-400.ttf:text=The Declaration.:fontsize=76:fontcolor=0xfaf6ea:x=100:y=898,drawtext=fontfile=fonts/IBMPlexMono-400.ttf:text=SET IN CASLON / MADE TO BE KEPT:fontsize=20:fontcolor=0xe4cfad:x=100:y=998','-af','highpass=f=80,loudnorm=I=-20:TP=-2:LRA=7,afade=t=out:st=4.6:d=0.4'],out)
  parts.append(out)
 out=T/f'{name}-end.mp4'
 encode(['-loop','1','-i',W/f'review/endcard-{name}.png','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','5','-vf',f'scale={w}:{h},setsar=1,fps=30','-map','0:v:0','-map','1:a:0'],out);parts.append(out)
 listing=T/f'{name}.txt';listing.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p in parts))
 final=K/'films'/f'history-has-a-pulse-{name}-{24 if name=="wide" else 15}s.mp4'
 run(['-f','concat','-safe','0','-i',listing,'-c','copy','-map_metadata','-1','-movflags','+faststart',final]);print('FILM',final.name,flush=True)
 if name=='wide':
  encode(['-i',final,'-vf','scale=1280:720'],M/'history-has-a-pulse-film.mp4')
  shutil.copy2(M/'shop-film.vtt',K/'films/shop-film.vtt')
  run(['-i',final,'-vn','-c:a','libmp3lame','-b:a','192k',K/'films/press-rhythm.mp3'])
for n in ['7243','7249','7248','7241']:
 p=IN/f'IMG_{n}.MOV';print(p.name,hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
print('All media exported',flush=True)
