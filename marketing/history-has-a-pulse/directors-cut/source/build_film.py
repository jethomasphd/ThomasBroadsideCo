"""Render the 75-second director's cut from the included sources. No API calls.

python source/build_film.py [--format wide|vertical|square] [--web-root PATH]
Requires imageio-ffmpeg, Pillow, fonttools and brotli on the design bench.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, textwrap
import imageio_ffmpeg
from fontTools.ttLib import TTFont

K=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--format',choices=['wide','vertical','square'])
parser.add_argument('--web-root',type=Path)
args=parser.parse_args()
W=K/'source/.render';W.mkdir(parents=True,exist_ok=True)
FF=os.environ.get('FFMPEG_BINARY') or imageio_ffmpeg.get_ffmpeg_exe()
D=json.loads((K/'source/edit.json').read_text(encoding='utf-8'))
LENGTH=D['duration']
assert sum(s['duration'] for s in D['scenes'])==LENGTH==75
assert len({s['id'] for s in D['scenes']})==len(D['scenes'])
for s in D['scenes']:
    if s['id']!='closing':assert hashlib.sha256((K/s['clip']).read_bytes()).hexdigest()==s['sha256']
for family,base in [('Display','LibreCaslonDisplay-400'),('Mono','IBMPlexMono-400')]:
    font=TTFont(K/'source/fonts'/f'{base}.woff2');font.flavor=None;font.save(W/f'{family}.ttf')

def run(values):
    p=subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*map(str,values)],cwd=W,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-6000:])

def duration(path):
    p=subprocess.run([FF,'-hide_banner','-i',str(path)],capture_output=True)
    m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',p.stderr.decode(errors='replace'))
    if not m:raise ValueError(f'Cannot measure {path}')
    h,m,s=map(float,m.groups());return h*3600+m*60+s

def draw(text,size,x,y,key,font='Mono',color='0xf1ece0',enable=None):
    if '\n' in text:
        return ','.join(draw(line,size,x,float(y)+i*(size*1.13+10),f'{key}-{i}',font,color,enable) for i,line in enumerate(text.splitlines()))
    p=W/(key+'.txt');p.write_text(text,encoding='utf-8')
    result=f'drawtext=fontfile={font}.ttf:textfile={p.name}:fontsize={size}:fontcolor={color}:x={x}:y={y}:line_spacing=10'
    if enable:result+=f":enable='{enable}'"
    return result

def clock(t,comma=False):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{"," if comma else "."}{ms%1000:03}'

def mix_audio():
    inputs=['-i',K/'audio/score.mp3'];fc=[];voices=[];shop=[]
    score_duration=duration(K/'audio/score.mp3')
    # Join the opening arc to the score's own resolving ending, with a one-second blend.
    fc += ['[0:a]asplit=2[ma][mb]', f'[ma]atrim=0:{LENGTH-8},asetpts=PTS-STARTPTS[ma1]',f'[mb]atrim=start={score_duration-9}:end={score_duration},asetpts=PTS-STARTPTS[mb1]', f'[ma1][mb1]acrossfade=d=1:c1=tri:c2=tri,loudnorm=I=-24:TP=-4:LRA=8,afade=t=in:st=9:d=2,afade=t=out:st={LENGTH-1.5}:d=1.5[music]']
    for i,v in enumerate(D['narration'],1):
        src=K/v['file'];actual=duration(src)/v['tempo'];assert v['at']+actual<=LENGTH
        if i<len(D['narration']):assert v['at']+actual<=D['narration'][i]['at']
        inputs+=['-i',src]
        fc.append(f'[{i}:a]atempo={v["tempo"]},highpass=f=65,loudnorm=I=-17.5:TP=-2:LRA=7,afade=t=in:d=0.012,afade=t=out:st={actual-.04}:d=0.04,aformat=sample_rates=48000:channel_layouts=stereo,adelay={round(v["at"]*1000)}:all=1[v{i}]')
        voices.append(f'[v{i}]')
    fc.append(''.join(voices)+f'amix=inputs={len(voices)}:normalize=0,apad=whole_dur={LENGTH},asplit=3[voice][key1][key2]')
    for j,s in enumerate([s for s in D['scenes'] if s['kind']=='shop'],len(D['narration'])+1):
        inputs+=['-i',K/s['clip']]
        fc.append(f'[{j}:a]atrim=0:{s["duration"]},asetpts=PTS-STARTPTS,highpass=f=90,lowpass=f=10000,loudnorm=I=-22:TP=-3:LRA=8,afade=t=in:d=0.08,afade=t=out:st={s["duration"]-.20}:d=0.20,adelay={round(s["at"]*1000)}:all=1[p{j}]')
        shop.append(f'[p{j}]')
    fc.append(''.join(shop)+f'amix=inputs={len(shop)}:normalize=0,apad=whole_dur={LENGTH}[shop]')
    fc += ['[music][key1]sidechaincompress=threshold=0.028:ratio=5:attack=30:release=450[mduck]', '[shop][key2]sidechaincompress=threshold=0.032:ratio=4:attack=20:release=300[pduck]', f'[voice][mduck][pduck]amix=inputs=3:normalize=0,alimiter=limit=0.89:level=false,atrim=0:{LENGTH},aformat=sample_rates=48000:channel_layouts=stereo[out]']
    run(inputs+['-filter_complex',';'.join(fc),'-map','[out]','-c:a','aac','-b:a','256k','-t',LENGTH,W/'soundtrack.m4a'])
    print('Narration, original score and real machinery mixed.',flush=True)

def render(fmt):
    w,h={'wide':(1920,1080),'vertical':(1080,1920),'square':(1080,1080)}[fmt]
    parts=[];audit=[]
    for i,s in enumerate(D['scenes']):
        end=s['id']=='closing';dest=W/f'{fmt}-{i:02}.mp4'
        src=K/'source'/f'endcard-{fmt}.png' if end else K/s['clip']
        if not end:assert duration(src)+.05>=s['source_start']+s['duration'],s['id']
        ih=1080 if fmt=='vertical' and not end else h
        vf=[f'scale={w}:{ih}:force_original_aspect_ratio=increase',f'crop={w}:{ih}:(iw-ow)*{s["crop_x"]}:(ih-oh)*{s["crop_y"]}','setsar=1','fps=24']
        if s['kind']=='shop':vf+=['eq=contrast=1.08:brightness=-0.025:saturation=0.62:gamma=1.02','colorbalance=rs=.025:gs=.009:bs=-.02:rh=.025:bh=-.025','unsharp=5:5:0.25:3:3:0']
        if not end:
            note={'shop':'ACTUAL SHOP FOOTAGE','history':'CONTEMPORARY RECONSTRUCTION','canon':'CONTEMPORARY VISUAL MEDITATION'}[s['kind']]
            if fmt=='vertical':
                vf += ['pad=1080:1920:0:230:color=0x201a10',draw('THOMAS BROADSIDE CO.',22,80,132,f'{fmt}-brand'),draw(s['label'],18,80,1380,f'{fmt}-{i}-label'),draw('\n'.join(textwrap.wrap(s['title'],25)),94 if i==0 else 78,80,1440,f'{fmt}-{i}-title',font='Display'),draw(note,15,80,1660,f'{fmt}-{i}-note')]
            else:
                # A graduated veil keeps small curatorial labels legible without a caption card.
                for band in range(12):vf.append(f'drawbox=x=0:y={h-300+band*25}:w=iw:h=25:color=black@{.025+band*.035:.3f}:t=fill')
                x=85 if fmt=='wide' else 55
                vf += [draw(s['label'],18 if fmt=='wide' else 14,x,h-76,f'{fmt}-{i}-label'),draw(note,14 if fmt=='wide' else 11,'w-tw-'+str(x),h-39,f'{fmt}-{i}-note')]
                if i==0:
                    vf += [draw('THOMAS BROADSIDE CO.',22 if fmt=='wide' else 18,x,65,f'{fmt}-brand'),draw('History has a pulse.' if fmt=='wide' else 'History has\na pulse.',130 if fmt=='wide' else 104,x,745 if fmt=='wide' else 635,f'{fmt}-opening',font='Display',enable='gte(t,0.7)')]
                elif s['id']=='room':vf += [draw('Words to live with.',108 if fmt=='wide' else 85,x,780,f'{fmt}-room',font='Display')]
        if i==0:vf+=['fade=t=in:st=0:d=0.20']
        if end:vf+=['fade=t=in:st=0:d=0.20']
        vf+=['tpad=stop_mode=clone:stop_duration=0.1']
        input_args=['-loop','1','-i',src] if end else ['-ss',s['source_start'],'-i',src]
        filters=['-vf',','.join(vf)]
        if s.get('book_cover'):
            cw={'wide':270,'vertical':240,'square':210}[fmt];ch=round(cw*860/600)
            bx=w-cw-(85 if fmt=='wide' else 70 if fmt=='vertical' else 55)
            by=1310-ch-55 if fmt=='vertical' else h-ch-155
            input_args+=['-loop','1','-i',K/s['book_cover']]
            graph=f'[0:v]{",".join(vf)}[base];[1:v]scale={cw}:{ch},fps=24,format=rgba,colorchannelmixer=aa=0.84,fade=t=in:st=0.7:d=0.7:alpha=1,fade=t=out:st={s["duration"]-.7}:d=0.6:alpha=1[book];[base][book]overlay={bx}:{by}:shortest=1:format=auto,format=yuv420p[out]'
            filters=['-filter_complex',graph,'-map','[out]']
        run(input_args+['-t',s['duration'],'-an',*filters,'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-map_metadata','-1','-movflags','+faststart',dest])
        parts.append(dest);audit.append(dict(id=s['id'],at=s['at'],duration=s['duration'],source=s.get('clip'),source_start=s['source_start'],source_sha256=s.get('sha256'),kind=s['kind']))
        print(fmt,s['id'],flush=True)
    listing=W/f'{fmt}-concat.txt';listing.write_text('\n'.join(f"file '{p.as_posix()}'" for p in parts),encoding='utf-8')
    silent=W/f'{fmt}-silent.mp4';run(['-f','concat','-safe','0','-i',listing,'-c','copy',silent])
    film=K/'films'/f'history-has-a-pulse-directors-cut-{LENGTH}s-{fmt}.mp4'
    run(['-i',silent,'-i',W/'soundtrack.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-t',LENGTH,'-map_metadata','-1','-movflags','+faststart',film])
    assert abs(duration(film)-LENGTH)<.05
    run(['-ss','3','-i',film,'-frames:v','1','-q:v','2',K/'artwork'/f'poster-{fmt}.jpg'])
    (K/'source'/f'timeline-{fmt}.json').write_text(json.dumps({'format':fmt,'duration':LENGTH,'shop_seconds':25.5,'captions_default':'off','shots':audit,'narration':D['narration'],'book_covers':D['book_covers'],'listening_window':D['listening_window']},indent=2)+'\n',encoding='utf-8')
    print('FINISHED',film.name,film.stat().st_size,flush=True)

mix_audio()
for fmt in ([args.format] if args.format else ['wide','vertical','square']):render(fmt)
cues=sorted([(0,.5,'[Press machinery]'),(D['listening_window']['start'],9.0,'[Press machinery, unaccompanied]')]+[(v['at'],v['at']+v['duration'],v['text']) for v in D['narration']])
vtt='WEBVTT\n\n'+'\n\n'.join(f'{clock(a)} --> {clock(b)}\n'+ '\n'.join(textwrap.wrap(t,64)) for a,b,t in cues)+'\n'
srt='\n\n'.join(f'{i}\n{clock(a,True)} --> {clock(b,True)}\n'+ '\n'.join(textwrap.wrap(t,64)) for i,(a,b,t) in enumerate(cues,1))+'\n'
(K/f'films/directors-cut-{LENGTH}s.vtt').write_text(vtt,encoding='utf-8')
(K/f'films/directors-cut-{LENGTH}s.srt').write_text(srt,encoding='utf-8')
if args.web_root:
    m=args.web_root.resolve();m.mkdir(exist_ok=True,parents=True)
    run(['-i',K/f'films/history-has-a-pulse-directors-cut-{LENGTH}s-wide.mp4','-vf','scale=1280:720','-c:v','libx264','-preset','fast','-crf','23','-c:a','aac','-b:a','160k','-map_metadata','-1','-movflags','+faststart',m/D['media']['film']])
    shutil.copy2(K/f'films/directors-cut-{LENGTH}s.vtt',m/D['media']['captions'])
    shutil.copy2(K/'artwork/poster-wide.jpg',m/D['media']['poster'])
    run(['-i',K/'artwork/poster-wide.jpg','-vf','scale=1200:630:force_original_aspect_ratio=increase,crop=1200:630','-frames:v','1','-q:v','2',m/D['media']['share']])
    assert (m/D['media']['film']).stat().st_size<25*1024*1024
