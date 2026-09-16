"""Rebuild three print PDFs with embedded fonts and 0.125-inch bleed.
Uses ReportLab + fonttools/brotli; design bench only. No runtime dependencies.
Output remains RGB: the print shop applies its chosen press/paper ICC profile.
"""
from pathlib import Path
import json,tempfile,sys
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
DATA=json.loads((K/'source/campaign.json').read_text(encoding='utf-8'))
for n,f in [('Display','LibreCaslonDisplay-400'),('Text','LibreCaslonText-400'),('Italic','LibreCaslonText-400i'),('Mono','IBMPlexMono-400')]:
    font=Font(K/'source/fonts'/f'{f}.woff2');font.flavor=None;p=Path(tempfile.gettempdir())/f'wtlw-{f}.ttf';font.save(p);pdfmetrics.registerFont(TTFont(n,str(p)))
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
        jpeg=Path(tempfile.gettempdir())/f'wtlw-print-{p.stem}.jpg'
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
base='https://thomasbroadside.co/canon.html'
def tracked(source,content):return base+f'?utm_source={source}&utm_medium=print&utm_campaign=words-to-live-with&utm_content={content}'

# Twelve-page six-by-nine reading guide, single pages for imposition at the shop.
c=pdf('words-to-live-with-reading-guide.pdf');w,h=432,648
page(c,w,h,1);text(c,'THE WESTERN CANON',34,565,8,'Mono',RED);title(c,'Words to\nlive with.',34,515,68)
para(c,'Make room for the enduring.',34,345,364,16,22);image(c,K/'artwork/room.png',34,95,364,215);text(c,'A CONTEMPORARY VISUAL MEDITATION',34,71,6,'Mono',SOFT);c.showPage()
page(c,w,h,2);text(c,'AN INVITATION TO ATTEND',34,558,8,'Mono',RED);title(c,'Read slowly.\nReturn often.',34,505,52)
para(c,'A homecoming. A blessing. A question about the soul. A prayer for rest. A path through the dark.',34,345,364,16,25)
para(c,'Poetry, scripture, prayer and art speak in different ways. This room gives each work its name, its translation, and its source. The invitation is to read, to consider, and to return.',34,225,364,11,19)
para(c,'The landscapes and reading room are contemporary visual meditations. The broadsides shown are the actual designs in our collection.',34,118,364,9,15);c.showPage()
refs={s['id']:s for s in DATA['sources']}
for n,ch in enumerate(DATA['chapters'],3):
    page(c,w,h,n);text(c,ch['no']+' / '+ch['theme'].upper(),34,564,8,'Mono',RED)
    title(c,{'mercy':'Words to receive\nwith care.'}.get(ch['id'],ch['title']),34,527,35)
    image(c,K/'artwork'/f'{ch["image"]}.png',34,298,364,176)
    q=ch['quote'].replace('\n','<br/>');size=19 if ch['id']!='the-soul' else 17
    end=para(c,q,34,268,364,size,size*1.3)
    end=para(c,ch['source'],34,end-17,364,7.5,12,SOFT)
    link(c,refs[ch['ref']]['url'],'READ THE SOURCE',34,65,7)
    link(c,'https://thomasbroadside.co/documents/'+ch['slug']+'.html','EXAMINE THE SHEET',250,65,7);c.showPage()
art=[('christ-preaching-hundred-guilder','Christ Preaching','Rembrandt van Rijn / c. 1649','National Gallery of Art / Object 9969','An etching of Christ and the gathered people. The Hundred Guilder Print brings the ministry into a field of light, line and deep shadow.','rembrandt-christ'),('aristotle-with-a-bust-of-homer','Aristotle with\na Bust of Homer','Rembrandt van Rijn / 1653','The Metropolitan Museum of Art / Object 437394','A philosopher rests his hand on the poet’s bust. Rembrandt brings poetry and philosophy into the same quiet encounter.','rembrandt-homer'),('the-circle-of-the-lustful','The Circle\nof the Lustful','William Blake / 1827','National Gallery of Art / Object 797','Paolo and Francesca, from Dante’s Inferno, Canto V. Blake’s engraving is a later artist’s encounter with the poem.','blake')]
for n,(slug,head,credit,institution,body,ref) in enumerate(art,8):
    page(c,w,h,n);text(c,'THE CONVERSATION IN IMAGES',34,564,8,'Mono',RED);title(c,head,34,524,36)
    image(c,K/'source/products'/f'{slug}.jpg',34,180,364,260)
    text(c,credit,34,151,8,'Mono');text(c,institution,34,133,6.7,'Mono',SOFT)
    para(c,body,34,113,364,9,14);link(c,refs[ref]['url'],'VIEW THE MUSEUM RECORD',34,60,7);c.showPage()
page(c,w,h,11);text(c,'FROM THE PAGE TO YOUR PLACE',34,562,8,'Mono',RED);title(c,'Give the words\na home.',34,516,51)
para(c,'The Western Canon Set',34,365,364,20,27)
para(c,'Five texts: The Odyssey, The Beatitudes, What is a man profited?, Our heart is restless, and Midway upon the journey.',34,322,364,11,19)
para(c,'The three art reproductions are available separately. Explore each product page for its source, paper, size and available formats.',34,225,364,10,17)
code(c,tracked('reading-guide','collection'),32,64,92);para(c,'Explore the room and watch the film.\nPrinted in Austin, Texas.',142,136,230,11,18)
text(c,'thomasbroadside.co/canon',142,72,8,'Mono');c.showPage()
page(c,w,h,12);text(c,'THE RECORD STAYS WITH THE WORK',34,562,7.5,'Mono',RED);title(c,'Keep the source.',34,520,43)
y=458
for s in DATA['sources']:
    y=para(c,s['title'],34,y,364,10,14);y=para(c,s['credit'],34,y-3,364,7.3,11,SOFT)
    c.linkURL(s['url'],(34,y,398,y+28),relative=1);y-=14
para(c,'Source texts: public domain in the United States. Museum images: the open-access records linked above. Imagined landscapes and room: contemporary campaign artwork. Readings retain the translation named on each sheet.',34,159,364,8,13)
text(c,'THOMAS BROADSIDE CO.',34,86,8,'Mono');text(c,'9501 N Interstate Hwy 35, Austin, TX 78753',34,70,7);text(c,'JEThomasPhD@gmail.com',34,56,7);c.showPage();c.save()
if '--guide-only' in sys.argv:
    print('Reading guide exported.');sys.exit(0)
# 9 x 6 inch two-sided mailer with return address and a clear addressing panel.
c=pdf('words-to-live-with-postcard.pdf');w,h=648,432
page(c,w,h);image(c,K/'artwork/room.png',314,0,334,432);text(c,'THOMAS BROADSIDE CO.',32,390,8,'Mono');text(c,'THE WESTERN CANON',32,321,8,'Mono',RED);title(c,'Words to\nlive with.',32,273,57)
para(c,'Make room for the enduring.',32,128,245,14,21);text(c,'A CONTEMPORARY VISUAL MEDITATION',32,32,5.5,'Mono',SOFT);c.showPage()
page(c,w,h);text(c,'THOMAS BROADSIDE CO.',32,393,8,'Mono');text(c,'9501 N Interstate Hwy 35',32,377,7);text(c,'Austin, TX 78753',32,365,7)
rule(c,338,36,0);c.setStrokeColor(HexColor(SOFT));c.line(338,35,338,330)
title(c,'Read slowly.\nReturn often.',32,309,34);para(c,'Homer. Matthew. Augustine. Dante. Rembrandt. Blake. Explore the Western Canon: contemporary broadsides and art reproductions, printed in Austin.',32,219,280,10.5,17)
code(c,tracked('direct-mail','postcard'),27,46,83);para(c,'Enter the reading room.\nWatch the film.',122,106,190,10,16);text(c,'thomasbroadside.co/canon',122,49,7,'Mono');text(c,'JEThomasPhD@gmail.com',32,24,7)
c.setStrokeColor(HexColor('#c4b99f'));c.rect(576,351,44,51,fill=0,stroke=1);text(c,'POSTAGE',580,371,5,'Mono',SOFT)
c.showPage();c.save()
# Letter-size partner introduction sheet.
c=pdf('words-to-live-with-partner-sheet.pdf');w,h=612,792
page(c,w,h);text(c,'THOMAS BROADSIDE CO. / AUSTIN, TEXAS',42,749,9,'Mono');rule(c,42,727,528)
text(c,'FOR LIBRARIES, CLASSROOMS & READING ROOMS',42,687,8,'Mono',RED);title(c,'A place for\nlasting words.',42,643,57)
image(c,K/'artwork/room.png',42,314,528,216)
para(c,'The Western Canon',42,282,528,24,30);para(c,'Eight works: Homer’s invocation, two passages from Matthew, Augustine’s prayer, Dante’s opening tercet, and art after Rembrandt and Blake. Sources and translations accompany the collection.',42,242,528,11,18)
para(c,'For a display, a reading space, or a considered gift: tell us your quantities, preferred formats and timing. We will help you select from the collection.',42,172,406,10,17)
code(c,tracked('partner-sheet','room'),484,79,86);text(c,'JEThomasPhD@gmail.com',42,102,10,'Mono');text(c,'9501 N Interstate Hwy 35, Austin, TX 78753',42,79,8);text(c,'thomasbroadside.co/canon',42,59,8,'Mono');text(c,'Room shown: contemporary visual meditation',42,29,6,'Mono',SOFT)
c.showPage();c.save();print('Three print masters exported.')
