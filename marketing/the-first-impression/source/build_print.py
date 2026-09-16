"""Rebuild three print PDFs with embedded fonts and 0.125-inch bleed.
Uses ReportLab + fonttools/brotli; design bench only. No runtime dependencies.
Output remains RGB: the print shop applies its chosen press/paper ICC profile.
"""
from pathlib import Path
import json,tempfile
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from fontTools.ttLib import TTFont as Font
from PIL import Image
K=Path(__file__).resolve().parents[1]; R=K.parents[1]; OUT=K/'print';OUT.mkdir(exist_ok=True)
DATA=json.loads((K/'source/story.json').read_text(encoding='utf-8'))
for n,f in [('Display','LibreCaslonDisplay-400'),('Text','LibreCaslonText-400'),('Italic','LibreCaslonText-400i'),('Mono','IBMPlexMono-400')]:
    font=Font(K/'source/fonts'/f'{f}.woff2');font.flavor=None;p=Path(tempfile.gettempdir())/f'tfi-{f}.ttf';font.save(p);pdfmetrics.registerFont(TTFont(n,str(p)))
PAPER='#f1ece0';INK='#201a10';RED='#9e3123';SOFT='#675b47'
def text(c,s,x,y,size=10,font='Text',color=INK):
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,s)
def title(c,lines,x,y,size=44,color=INK):
    for s in lines.split('\n'):text(c,s,x,y,size,'Display',color);y-=size*1.02
    return y
def para(c,s,x,y,w,size=10,leading=16,color=INK):
    st=ParagraphStyle('body',fontName='Text',fontSize=size,leading=leading,textColor=HexColor(color))
    p=Paragraph(s,st);_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return y-h
def rule(c,x,y,w,color=SOFT):c.setStrokeColor(HexColor(color));c.setLineWidth(.4);c.line(x,y,x+w,y)
def image(c,p,x,y,w,h):
    # Native-resolution JPEG embedding keeps photographic print masters portable.
    # The original generated PNGs remain untouched in the kit.
    p=Path(p)
    if p.suffix.lower()=='.png':
        jpeg=Path(tempfile.gettempdir())/f'tfi-print-{p.stem}.jpg'
        with Image.open(p) as im:im.convert('RGB').save(jpeg,quality=95,subsampling=0,optimize=True)
        p=jpeg
    c.drawImage(str(p),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
def page(c,w,h,no=None):
    c.setPageSize((w+18,h+18));c.setTrimBox((9,9,w+9,h+9));c.setBleedBox((0,0,w+18,h+18));c.setFillColor(HexColor(PAPER));c.rect(0,0,w+18,h+18,fill=1,stroke=0);c.translate(9,9)
    if no:
        text(c,'THOMAS BROADSIDE CO.',34,h-34,7,'Mono');text(c,f'{no:02}',w-48,24,7,'Mono',SOFT);rule(c,34,43,w-68)
def code(c,url,x,y,size=70):
    wid=qr.QrCodeWidget(url);b=wid.getBounds();d=Drawing(size,size,transform=[size/(b[2]-b[0]),0,0,size/(b[3]-b[1]),0,0]);d.add(wid);renderPDF.draw(d,c,x,y)
    c.linkURL(url,(x,y,x+size,y+size),relative=1)
def pdf(name):
    c=canvas.Canvas(str(OUT/name),pageCompression=1);c.setTitle(name.replace('-',' ').replace('.pdf',''));c.setAuthor('Thomas Broadside Co.');return c
def link(c,url,label,x,y,size=8):
    text(c,label,x,y,size,'Mono',RED);c.linkURL(url,(x,y-3,x+pdfmetrics.stringWidth(label,'Mono',size),y+size+3),relative=1)
base='https://thomasbroadside.co/origins.html'
def tracked(source,content):return base+f'?utm_source={source}&utm_medium=print&utm_campaign=the-first-impression&utm_content={content}'

# Twelve-page, six-by-nine field guide. Single reader pages, no imposed spreads.
c=pdf('the-first-impression-field-guide.pdf');w,h=432,648
page(c,w,h,1);text(c,'THE FIRST IMPRESSION',34,567,9,'Mono',RED);title(c,'Before it was\na relic,\nit was news.',34,512,61)
image(c,K/'artwork'/f"{DATA['opening']['image']}.png",34,152,364,205)
text(c,'THE PRINTER’S BENCH / RECONSTRUCTED',34,135,7,'Mono',SOFT)
para(c,'A printer’s night. A document on its way to the world.',34,109,345,12,18)
text(c,'Contemporary reconstruction',34,59,6.8,'Mono',SOFT);c.showPage()
page(c,w,h,2);text(c,'THE DOCUMENT HAD TO LEAVE THE ROOM.',34,567,8,'Mono',RED);title(c,'Public words.\nPublic life.',34,518,53)
para(c,'The Declaration did not begin behind glass. It went to a working print shop. From there, copies traveled to assemblies, committees and commanders.',34,380,351,13,22)
para(c,'This is a story about different hands and different roles: the printer’s eye, the working draft, the first impression, the public reading, and the argument in the newspaper.',34,272,351,10.5,18)
rule(c,34,173,364);title(c,'Read the words.\nKeep the source.',34,140,34)
text(c,'AN ORIGIN STORY FROM THOMAS BROADSIDE CO.',34,62,7,'Mono',RED);c.showPage()
heads={'franklin':'He knew what a\npage could do.','jefferson':'The words\nwere worked on.','dunlap':'A declaration\nneeded a printer.','washington':'The sheet\nbecame a voice.','hamilton':'The argument\nkept moving.'}
for n,ch in enumerate(DATA['chapters'],3):
    page(c,w,h,n);text(c,(ch['number']+' / '+ch['eyebrow'].split(' / ')[0]).upper(),34,567,8,'Mono',RED);title(c,heads[ch['id']],34,525,43)
    image(c,K/'artwork'/f'{ch["image"]}.png',34,238,364,205)
    text(c,ch['date'].replace('–','-').upper(),34,222,6.9,'Mono',SOFT)
    # The full chapter remains on the site; this smaller format uses one precise paragraph.
    para(c,ch['body'][0],34,201,364,10.2,17)
    note={'franklin':'He later helped revise the Declaration’s draft.','jefferson':'The surviving manuscript lets us follow the revisions.','dunlap':'The printed words could now leave the room.','washington':'A fragment of Washington’s printed copy survives.','hamilton':'A later debate. A different document. Print again.'}[ch['id']]
    para(c,note,34,105,364,10,16,color=RED)
    text(c,'Contemporary reconstruction / Sources and links on page 12',34,60,6.5,'Mono',SOFT);c.showPage()
page(c,w,h,8);text(c,'THE SURVIVING RECORD',34,567,8,'Mono',RED);title(c,'From draft\nto public sheet.',34,525,45)
image(c,K/'source/dunlap-original.jpg',45,233,150,190);image(c,K/'source/jefferson-draft.jpg',248,233,120,190)
text(c,'DUNLAP / FIRST PRINTING',34,210,6.8,'Mono',RED);text(c,'JEFFERSON / ROUGH DRAFT',226,210,6.8,'Mono',RED)
para(c,'At left: the first printing, with the printed names of Hancock and Thomson. At right: Jefferson’s working draft. The familiar signed parchment came later.',34,182,364,10.4,17)
para(c,'Reference reproductions from the Library of Congress. Follow the linked source record for the originals and their context.',34,103,364,8.7,14)
c.showPage()
page(c,w,h,9);text(c,'06 / THE WORK CONTINUES',34,567,8,'Mono',RED);title(c,'Different century.\nSame conviction.',34,525,44)
image(c,K/'source/austin.jpg',34,238,364,205);text(c,'THOMAS GRAPHICS / AUSTIN, TEXAS',34,221,7,'Mono',SOFT)
para(c,'A working press. A sheet you can hold. Words with a source you can follow. At Thomas Broadside Co., the heritage becomes something to live with, read again, and pass on.',34,192,364,11.4,19)
text(c,'Art-directed shop photograph',34,61,7,'Mono',SOFT);c.showPage()
page(c,w,h,10);text(c,'THE COLLECTION / THE DECLARATION',34,567,8,'Mono',RED);title(c,'A place for\nthe words.',34,525,47)
image(c,K/'source/products/declaration-of-independence.jpg',114,165,204,272)
para(c,'Our Declaration is a contemporary composition of its celebrated passage, set in Caslon. A new design inspired by the broadside tradition, printed in Austin.',34,142,364,10.3,16.5)
text(c,'Contemporary print; not an original artifact or Dunlap facsimile.',34,61,6.5,'Mono',SOFT);c.showPage()
page(c,w,h,11);text(c,'THE COLLECTION / THE FOUNDERS',34,567,8,'Mono',RED);title(c,'Bring the story\ninto the room.',34,525,45)
for i,ch in enumerate([c for c in DATA['chapters'] if c['id']!='dunlap']):
    x=51+(i%2)*190;y=264-(i//2)*198
    image(c,K/'source/products'/f'{ch["slug"]}.jpg',x,y,133,177)
    text(c,ch['id'].upper(),x,y-12,7,'Mono',RED)
    c.linkURL('https://thomasbroadside.co/documents/'+ch['slug']+'.html',(x,y,x+133,y+177),relative=1)
c.showPage()
page(c,w,h,12);text(c,'THE RECORD BEHIND THE STORY',34,567,8,'Mono',RED);title(c,'Keep the source.',34,526,45)
y=481
for i,s in enumerate(DATA['sources'],1):
    label=f'{i:02} / '+s['title'].replace('–','-')
    y=para(c,label,34,y,364,9.1,13)
    link(c,s['url'],s['institution'][:64],34,y-13,6.7);y-=33
para(c,'Period scenes are contemporary reconstructions, with imagined rooms, gestures and incidental people. Narration and score are modern. The Austin footage records the actual shop.',34,171,264,8,12)
code(c,tracked('field-guide','read-watch-shop'),310,94,85)
para(c,'9501 N Interstate Hwy 35<br/>Austin, TX 78753<br/>JEThomasPhD@gmail.com',34,116,265,8,13)
text(c,'thomasbroadside.co/origins',34,59,7.7,'Mono',RED);c.showPage();c.save()

# Landscape 6x9 direct mail; second page preserves recipient/postage/barcode space.
c=pdf('the-first-impression-postcard-6x9.pdf');w,h=648,432;page(c,w,h)
text(c,'THOMAS BROADSIDE CO.',32,389,10,'Mono');text(c,'THE FIRST IMPRESSION',32,357,8,'Mono',RED)
title(c,'Before it was\na relic,\nit was news.',32,300,52)
image(c,K/'artwork'/f"{DATA['opening']['image']}.png",297,147,319,180)
text(c,'THE PRINTER’S BENCH / RECONSTRUCTED',297,129,6.1,'Mono',SOFT)
rule(c,32,97,584);para(c,'A printer’s night. A document on its way to the world.<br/>Discover the story. Find your first impression.',32,77,500,10.5,16)
text(c,'thomasbroadside.co/origins',32,25,8,'Mono',RED);c.showPage();page(c,w,h)
text(c,'THOMAS BROADSIDE CO.',32,389,9,'Mono');title(c,'Give the words\na place in your life.',32,338,37)
para(c,'Follow the Declaration from Jefferson’s draft to Dunlap’s press and Washington’s troops. Then discover broadsides made to live with, printed in our Austin shop.',32,236,273,10.5,17)
para(c,'Watch the film. Read the sources.<br/>Explore the collection.',32,132,273,10.5,17)
code(c,tracked('postcard','origin-film'),27,19,77);text(c,'THE ORIGIN STORY',112,68,7,'Mono',RED);text(c,'thomasbroadside.co/origins',112,47,6.8,'Mono')
para(c,'Thomas Broadside Co.<br/>9501 N Interstate Hwy 35<br/>Austin, TX 78753',360,314,225,8.1,12)
# Right recipient and postage fields remain blank for the mail house. No fake indicia.
c.showPage();c.save()

# Library / museum-shop / classroom introduction. Letter trim, comfortable reading size.
c=pdf('the-first-impression-partner-sheet.pdf');w,h=612,792;page(c,w,h)
text(c,'THOMAS BROADSIDE CO.',38,748,10,'Mono');text(c,'LIBRARIES / MUSEUM SHOPS / CLASSROOMS',38,721,7.8,'Mono',RED)
title(c,'Bring the founding\ninto the room.',38,673,58)
image(c,K/'artwork'/f"{DATA['opening']['image']}.png",38,350,344,194);image(c,K/'source/products/declaration-of-independence.jpg',410,350,162,216)
text(c,'CONTEMPORARY RECONSTRUCTION',38,334,6.7,'Mono',SOFT);text(c,'OUR DECLARATION DESIGN',410,334,6.7,'Mono',SOFT)
para(c,'The First Impression follows the founding words from the working draft to Dunlap’s printed Declaration, Washington’s troops, and the later newspaper debate over the Constitution.',38,302,535,12,19)
para(c,'For your space',38,221,245,15,21,color=RED)
para(c,'Broadsides with the source on the sheet. Explore founding documents and historical portraits for reading rooms, classrooms, offices, and thoughtful gifts.',38,192,245,10,16)
para(c,'Start a conversation',319,221,250,15,21,color=RED)
para(c,'For a library display, classroom order, museum-shop inquiry or a gift selection, write the shop with your quantities and timing. Current formats and availability are on the site.',319,192,250,10,16)
rule(c,38,97,536);para(c,'JEThomasPhD@gmail.com<br/>9501 N Interstate Hwy 35, Austin, TX 78753<br/>thomasbroadside.co/origins',38,80,430,8.6,13)
code(c,tracked('partner-sheet','inquiry'),497,22,72);c.showPage();c.save()
print('Three PDFs exported: 12-page field guide, two-sided postcard, partner sheet.')
