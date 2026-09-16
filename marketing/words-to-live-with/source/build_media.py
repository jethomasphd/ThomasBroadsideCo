"""Rebuild finished films locally. No API calls or new model charges.
Requires imageio-ffmpeg, Pillow, fonttools and brotli (design bench only).
Export the three endcard PNGs from campaign-art.html before running.
"""
from pathlib import Path
import subprocess,json,os,shutil,re
import imageio_ffmpeg
from fontTools.ttLib import TTFont
from PIL import Image
K=Path(__file__).resolve().parents[1];R=K.parents[1];W=K/'source/.render';W.mkdir(parents=True,exist_ok=True)
FF=os.environ.get('FFMPEG_BINARY') or imageio_ffmpeg.get_ffmpeg_exe()
for family,base in [('Display','LibreCaslonDisplay-400'),('Mono','IBMPlexMono-400')]:
    f=TTFont(K/'source/fonts'/f'{base}.woff2');f.flavor=None;f.save(W/f'{family}.ttf')
def run(args):
    r=subprocess.run([FF,'-hide_banner','-y',*map(str,args)],cwd=W,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-6000:])
def draw(text,size,x,y,font='Display',color='0xfaf6ea',key='label'):
    if '\n' in text:return ','.join(draw(t,size,x,y+round(size*1.08)*i,font,color,key+str(i)) for i,t in enumerate(text.split('\n')))
    name=key+'.txt';(W/name).write_text(text,encoding='utf-8');return f'drawtext=fontfile={font}.ttf:textfile={name}:fontsize={size}:fontcolor={color}:x={x}:y={y}'
data=json.loads((K/'source/campaign.json').read_text(encoding='utf-8'));script=dict(data['narration'])
voice_duration={'room':7.059,'sea':8.731,'hill':8.220,'soul':5.295,'rest':7.198,'wood':4.644,'art':7.106,'closing':8.685}
titles={'room':'Words to live with.','sea':'A long way home.','hill':'The Beatitudes','soul':'The question remains.','rest':'A prayer on the page.','wood':'At the edge of the wood.','art':'Look a little longer.'}
labels={'room':'THE WESTERN CANON','sea':'HOMER / THE ODYSSEY / BOOK I','hill':'MATTHEW 5:7 / AUTHORIZED VERSION','soul':'MATTHEW 16:26 / AUTHORIZED VERSION','rest':'AUGUSTINE / CONFESSIONS / BOOK I','wood':'DANTE / INFERNO / CANTO I','art':'THE COLLECTION / REMBRANDT & BLAKE'}

def clip_duration(src):
    result=subprocess.run([FF,'-hide_banner','-i',str(src)],capture_output=True)
    match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',result.stderr.decode(errors='replace'))
    if not match:raise ValueError(f'Cannot measure {src}')
    hh,mm,ss=map(float,match.groups());return hh*3600+mm*60+ss
def clock(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
def film(name,fmt,segments,narrate=True):
    scenes=[scene for scene,_ in segments]
    if len(scenes)!=len(set(scenes)):raise ValueError('A narrative scene cannot appear twice in a film.')
    w,h={'wide':(1920,1080),'vertical':(1080,1920),'square':(1080,1080)}[fmt];position=0;parts=[];timeline=[]
    for i,(scene,duration) in enumerate(segments):
        dest=W/f'{name}-{i}.mp4';end=scene=='closing';still=end or scene=='art'
        src=K/'source'/f'endcard-{fmt}.png' if end else K/'source/products/aristotle-with-a-bust-of-homer.jpg' if still else K/'source/clips'/f'{scene}.mp4'
        if still:
            vf=[f'scale={w-180 if not end else w}:{h-340 if not end else h}:force_original_aspect_ratio=decrease',f'pad={w}:{h}:(ow-iw)/2:{100 if not end else "(oh-ih)/2"}:color=0xf1ece0','setsar=1','fps=24'];ink='0x201a10'
        elif fmt=='vertical':
            vf=['scale=1920:1080','crop=1080:1080:420:0','pad=1080:1920:0:300:color=0xf1ece0','setsar=1','fps=24'];ink='0x201a10'
        else:
            vf=[f'scale={w}:{h}:force_original_aspect_ratio=increase',f'crop={w}:{h}','setsar=1','fps=24',f'drawbox=x=0:y={h-260}:w=iw:h=260:color=black@0.5:t=fill'];ink='0xfaf6ea'
        if not end:
            x=100 if fmt=='wide' else 65;y= h-210 if fmt!='vertical' else 1450
            if fmt=='vertical':vf+=[draw('THOMAS BROADSIDE CO.',20,65,175,'Mono',ink,key=f'{fmt}-brand')]
            vf+=[draw(labels[scene],22 if fmt=='wide' else 18,x,y,'Mono',ink,key=f'{fmt}-{scene}-label'),draw(titles[scene],70 if fmt=='wide' else 64,x,y+55,'Display',ink,key=f'{fmt}-{scene}-title')]
            note='CONTEMPORARY VISUAL MEDITATION' if not still else 'CONTEMPORARY BROADSIDE / SOURCE ON THE SHEET'
            vf+=[draw(note,17 if fmt=='wide' else 14,x,h-65 if fmt!='vertical' else 1700,'Mono',ink,key=f'{fmt}-{scene}-note')]
        # Use every moving shot once. Gently slow longer holds instead of replaying
        # the beginning of a ten-second clip. The tiny pad covers frame rounding.
        if not still:vf.insert(0,f'setpts={max(1,duration/clip_duration(src)):.8f}*(PTS-STARTPTS)')
        vf += ['tpad=stop_mode=clone:stop_duration=0.1',f'fade=t=in:st=0:d=0.35',f'fade=t=out:st={duration-.35}:d=0.35']
        run((['-loop','1'] if still else [])+['-i',src,'-t',duration,'-an','-vf',','.join(vf),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',dest]);parts.append(dest);timeline.append((scene,position,duration));position+=duration;print(name,scene,flush=True)
    listing=W/f'{name}.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in parts));silent=W/f'{name}-silent.mp4';run(['-f','concat','-safe','0','-i',listing,'-c','copy',silent])
    args=['-i',silent,'-i',K/'audio/music_score.mp3'];fc=[f'[1:a]atrim=0:{position},asetpts=PTS-STARTPTS,loudnorm=I={-29 if narrate else -18}:TP=-3:LRA=8,afade=t=in:d=2,afade=t=out:st={position-4}:d=4[m]'];voices=[];cues=[]
    if narrate:
        for i,(scene,start,dur) in enumerate(timeline):
            delay=.5;assert dur>=voice_duration[scene]+delay,f'{scene} voice would be cut'
            args+=['-i',K/'audio'/f'speech_{scene}.mp3'];fc.append(f'[{i+2}:a]loudnorm=I=-18:TP=-2:LRA=7,adelay={round((start+delay)*1000)}:all=1[v{i}]');voices.append(f'[v{i}]');cues.append((start+delay,start+delay+voice_duration[scene],script[scene]))
    fc+=['[m]'+''.join(voices)+f'amix=inputs={1+len(voices)}:duration=longest:normalize=0,alimiter=limit=0.92:level=false,atrim=0:{position}[mix]']
    out=K/'films'/f'{name}.mp4';run(args+['-filter_complex',';'.join(fc),'-map','0:v','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','160k','-ar','48000','-t',position,'-movflags','+faststart',out])
    if narrate:(K/'films'/f'{name}.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f'{clock(s)} --> {clock(e)}\n{t}' for s,e,t in cues)+'\n',encoding='utf-8',newline='\n')
    (K/'source'/f'{name}-timeline.json').write_text(json.dumps({'format':fmt,'duration':position,'segments':timeline,'captions_default':'off'},indent=2)+'\n',encoding='utf-8',newline='\n');print('FINISHED',name,out.stat().st_size,flush=True)
film('words-to-live-with-80s','wide',[('room',9),('sea',11),('hill',12),('soul',10),('rest',10),('wood',8),('art',10),('closing',10)])
for fmt in ['vertical','square']:film(f'make-room-30s-{fmt}',fmt,[('room',9),('sea',11),('closing',10)])
film('words-to-live-with-15s-teaser','vertical',[('room',5),('sea',5),('closing',5)],False)
M=R/'site/media/canon'
if M.exists():
    run(['-i',K/'films/words-to-live-with-80s.mp4','-vf','scale=1280:720','-c:v','libx264','-preset','fast','-crf','24','-c:a','aac','-b:a','128k','-movflags','+faststart',M/data['film']['file']])
    shutil.copy2(K/'films/words-to-live-with-80s.vtt',M/data['film']['captions'])
    for fmt,vf in [('wide','scale=1280:720'),('portrait','scale=1280:720,crop=404:720:630:0,scale=540:960')]:
        run(['-i',K/'source/clips/room.mp4','-filter_complex',f'[0:v]trim=start=0:end=4,setpts=PTS-STARTPTS,{vf},fps=24,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0[v]','-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',M/f'canon-loop-{fmt}.mp4'])
    Image.open(K/'social/11-share.png').convert('RGB').save(M/'share-card.jpg',quality=91,optimize=True)
print('Films and website media complete.')
