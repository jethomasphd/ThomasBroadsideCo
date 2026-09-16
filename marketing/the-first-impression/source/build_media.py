"""Rebuild the campaign films from included Runway clips, narration and artwork.
Design bench dependencies only: imageio-ffmpeg, fonttools, brotli, Pillow.
No network calls or model spending. Generated master clips are kept unchanged.
"""
from pathlib import Path
import subprocess,json,shutil,tempfile,os,hashlib
import imageio_ffmpeg
from fontTools.ttLib import TTFont
from PIL import Image
K=Path(__file__).resolve().parents[1]; R=K.parents[1]; W=R/'work/origin-edit'; W.mkdir(parents=True,exist_ok=True)
FF=os.environ.get('FFMPEG_BINARY') or imageio_ffmpeg.get_ffmpeg_exe()
for font,base in [('Display','LibreCaslonDisplay-400'),('Mono','IBMPlexMono-400')]:
    f=TTFont(K/'source/fonts'/f'{base}.woff2');f.flavor=None;f.save(W/f'{font}.ttf')
def run(args):
    p=subprocess.run([FF,'-hide_banner','-y',*map(str,args)],cwd=W,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-6000:])
def draw(text,size,x,y,font='Display',color='0xf1ece0',key='label'):
    if '\n' in text:
        return ','.join(draw(line,size,x,y+round(size*1.06)*i,font,color,key+f'-line{i}') for i,line in enumerate(text.split('\n')))
    name=f'text-{key}.txt';(W/name).write_text(text,encoding='utf-8')
    return f"drawtext=fontfile={font}.ttf:textfile={name}:fontsize={size}:fontcolor={color}:x={x}:y={y}:line_spacing=10"
assignments=json.loads((K/'source/scene-assignments.json').read_text(encoding='utf-8'))
clips={s['id']:K/s['clip'] for s in assignments['scenes']}
clip_hashes={scene:hashlib.sha256(path.read_bytes()).hexdigest() for scene,path in clips.items()}
if len(set(clip_hashes.values())) != len(clips):
    raise ValueError('Every narrative scene must use a distinct source clip')
clip_lengths={}
for scene,path in clips.items():
    reader=imageio_ffmpeg.read_frames(str(path));clip_lengths[scene]=next(reader)['duration'];reader.close()
web=json.loads((K/'source/story.json').read_text(encoding='utf-8'))['media']
titles={'opening':'Before it was a relic,\nit was news.','franklin':'He knew what a page could do.','jefferson':'The words were worked on.','dunlap':'A declaration needed a printer.','washington':'The sheet became a voice.','hamilton':'The argument kept moving.','austin':'Different century. Same conviction.'}
labels={'opening':'THE FIRST IMPRESSION','franklin':'BENJAMIN FRANKLIN / THE PRINTER’S EYE','jefferson':'THOMAS JEFFERSON / THE WORKING DRAFT','dunlap':'JOHN DUNLAP / JULY 4–5, 1776','washington':'GEORGE WASHINGTON / JULY 9, 1776','hamilton':'ALEXANDER HAMILTON / 1787–1788','austin':'THOMAS GRAPHICS / AUSTIN, TEXAS'}
durations=dict(opening=4.133,franklin=4.783,jefferson=5.016,dunlap=7.384,washington=7.152,hamilton=6.084,austin=10.356,closing=4.458)
script=dict(json.loads((K/'source/video-prompts.json').read_text(encoding='utf-8'))['narration']['lines'])
def clock(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
def film(name,fmt,segments,narrate=True):
    scene_ids=[scene for scene,_ in segments]
    if len(set(scene_ids)) != len(scene_ids):raise ValueError(f'Repeated scene in {name}')
    w,h={'wide':(1920,1080),'vertical':(1080,1920),'square':(1080,1080)}[fmt]
    exports=[];timeline=[];position=0
    for n,(scene,duration) in enumerate(segments):
        dest=W/f'{name}-{n}.mp4';is_end=scene=='closing'
        src=K/'source'/f'endcard-{fmt}.png' if is_end else clips[scene]
        if not is_end and clip_lengths[scene] + 1/24 < duration:
            raise ValueError(f'{scene} is too short for {duration}s; supply enough unique footage')
        delay=.25 if is_end else .65
        if narrate and delay+durations[scene] > duration:
            raise ValueError(f'Narration overruns the {scene} scene')
        filters=[f'scale={w}:{h}:force_original_aspect_ratio=increase',f'crop={w}:{h}','setsar=1','fps=24']
        if not is_end:
            if fmt=='vertical':
                # A moving square image within a portrait composition preserves both readers.
                crop_x=260 if scene=='washington' else 420
                filters=['scale=1920:1080',f'crop=1080:1080:{crop_x}:0','pad=1080:1920:0:260:color=0x201a10','setsar=1','fps=24']
                filters+=[draw('THOMAS BROADSIDE CO.',20,80,160,'Mono',key=f'{fmt}-brand')]
                short= titles[scene].replace('A declaration needed a printer.','A declaration\nneeded a printer.').replace('The sheet became a voice.','The sheet\nbecame a voice.')
                filters+=[draw(labels[scene],19,80,1395,'Mono',key=f'{fmt}-{scene}-label'),draw(short,83,80,1450,key=f'{fmt}-{scene}-title'),draw('CONTEMPORARY RECONSTRUCTION',16,80,1680,'Mono',key=f'{fmt}-note')]
            else:
                if fmt=='square' and scene=='washington':filters=['scale=1920:1080','crop=1080:1080:260:0','setsar=1','fps=24']
                filters += [f'drawbox=x=0:y={h-300}:w=iw:h=300:color=black@0.52:t=fill']
                if scene=='opening':
                    filters += [draw(labels[scene],24 if fmt=='wide' else 20,100 if fmt=='wide' else 65,h-300,'Mono',key=f'{fmt}-{scene}-label'),draw(titles[scene],92 if fmt=='wide' else 70,100 if fmt=='wide' else 65,h-260,key=f'{fmt}-{scene}-title')]
                else:
                    filters += [draw(labels[scene],23 if fmt=='wide' else 18,100 if fmt=='wide' else 65,h-220,'Mono',key=f'{fmt}-{scene}-label'),draw(titles[scene],65 if fmt=='wide' else 57,100 if fmt=='wide' else 65,h-170,key=f'{fmt}-{scene}-title')]
                note='ACTUAL SHOP FOOTAGE / AUSTIN, TEXAS' if scene=='austin' else 'CONTEMPORARY RECONSTRUCTION'
                filters += [draw(note,17 if fmt=='wide' else 14,100 if fmt=='wide' else 65,h-62,'Mono',key=f'{fmt}-{scene}-note'),draw('THOMAS BROADSIDE CO.',18,100 if fmt=='wide' else 65,60,'Mono',key=f'{fmt}-brand')]
        filters += [f'fade=t=in:st=0:d=0.25',f'fade=t=out:st={duration-.25}:d=0.25']
        run((['-loop','1'] if is_end else [])+['-i',src,'-t',duration,'-an','-vf',','.join(filters),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',dest])
        exports.append(dest);timeline.append((scene,position,duration));position+=duration
        print(name,scene,flush=True)
    listing=W/f'{name}-concat.txt';listing.write_text('\n'.join("file '"+p.as_posix()+"'" for p in exports))
    silent=W/f'{name}-silent.mp4';run(['-f','concat','-safe','0','-i',listing,'-c','copy',silent])
    args=['-i',silent,'-i',K/'audio/music_score.mp3'];audio=[];cues=[]
    music_target = -29 if narrate else -18
    fc=[f'[1:a]atrim=0:{position},asetpts=PTS-STARTPTS,loudnorm=I={music_target}:TP=-3:LRA=8,afade=t=in:d=2,afade=t=out:st={position-4}:d=4[music]']
    if narrate:
        for i,(scene,start,duration) in enumerate(timeline):
            args+=['-i',K/'audio'/f'speech_{scene}.mp3'];delay=.25 if scene=='closing' else .65
            fc.append(f'[{i+2}:a]loudnorm=I=-18:TP=-2:LRA=7,adelay={round((start+delay)*1000)}:all=1[v{i}]');audio.append(f'[v{i}]')
            cues.append((start+delay,min(start+duration,start+delay+durations[scene]),script[scene]))
    fc.append('[music]'+''.join(audio)+f'amix=inputs={len(audio)+1}:duration=longest:normalize=0,alimiter=limit=0.92:level=false,atrim=0:{position}[mix]')
    dest=K/'films'/f'{name}.mp4';run(args+['-filter_complex',';'.join(fc),'-map','0:v','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart','-t',position,dest])
    vtt='WEBVTT\n\n'+'\n\n'.join(f'{clock(s)} --> {clock(e)}\n{t}' for s,e,t in cues)+'\n'
    if narrate:(K/'films'/f'{name}.vtt').write_text(vtt,encoding='utf-8')
    source_edits={scene:{'path':clips[scene].relative_to(K).as_posix(),'sha256':clip_hashes[scene],'start_seconds':0,'duration_seconds':duration,'repeat':False} for scene,_,duration in timeline if scene!='closing'}
    (K/'source'/f'{name}-timeline.json').write_text(json.dumps({'format':fmt,'duration':position,'segments':timeline,'source_edits':source_edits,'captions_default':'off'},indent=2)+'\n')
    print('FINISHED',name,dest.stat().st_size,flush=True)
film('the-first-impression-65s','wide',[('opening',6),('franklin',7),('jefferson',7),('dunlap',9),('washington',9),('hamilton',8),('austin',12),('closing',7)])
for fmt in ['vertical','square']:film(f'the-printers-night-30s-{fmt}',fmt,[('opening',6),('dunlap',10),('washington',9),('closing',5)])
film('the-first-impression-15s-teaser','vertical',[('opening',6),('dunlap',4),('closing',5)],False)
M=R/'site/media/origin'
run(['-i',K/'films/the-first-impression-65s.mp4','-vf','scale=1280:720','-c:v','libx264','-preset','fast','-crf','23','-c:a','aac','-b:a','128k','-movflags','+faststart',M/web['film']])
shutil.copy2(K/'films/the-first-impression-65s.vtt',M/web['captions'])
# A forward/reverse ambient loop: no voice, no sudden reset, no automatic sound.
for suffix,vf in [('wide','scale=1280:720'),('portrait','scale=1280:720,crop=404:720:670:0,scale=540:960')]:
    run(['-i',clips['opening'],'-filter_complex',f'[0:v]trim=start=1:end=5,setpts=PTS-STARTPTS,{vf},fps=24,split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0[v]','-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',M/web['loop_'+suffix]])
Image.open(K/'social/09-linkedin-share.png').convert('RGB').save(M/web['share'],quality=91,optimize=True)
shutil.copy2(M/web['share'],K/'source/email-header.jpg')
print('Website films, ambient loops and share artwork exported.')
