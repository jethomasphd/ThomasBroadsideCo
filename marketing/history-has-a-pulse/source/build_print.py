"""Rebuild print pieces: Python + ReportLab + fonttools/brotli (design bench only).
Run from any directory. Optional --address 'approved return address'.
The canonical catalog/art stays in the factory; no prices are copied here.
"""
from pathlib import Path
import argparse,json,tempfile
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from fontTools.ttLib import TTFont as Font

K=Path(__file__).resolve().parents[1]; R=K.parents[1];OUT=K/'print'
ap=argparse.ArgumentParser();ap.add_argument('--address',default='9501 N Interstate Hwy 35\nAustin, TX 78753');args=ap.parse_args()
for name,file in [('Display','LibreCaslonDisplay-400'),('Text','LibreCaslonText-400'),('Italic','LibreCaslonText-400i'),('Bold','LibreCaslonText-700'),('Mono','IBMPlexMono-400')]:
 f=Font(R/'site/fonts'/f'{file}.woff2');f.flavor=None
 tmp=Path(tempfile.gettempdir())/f'tb-{file}.ttf';f.save(tmp);pdfmetrics.registerFont(TTFont(name,str(tmp)))
PAPER='#f1ece0';INK='#201a10';RED='#9e3123';SOFT='#675b47';WHITE='#faf6ea'
photo=K/'artwork/press-portrait-enhanced.png';cat=json.loads((R/'data/catalog/catalog.json').read_text(encoding='utf-8'))
by={d['slug']:d for d in cat['designs']};base='https://thomasbroadside.co/'
def text(c,s,x,y,size=10,font='Text',color=INK):
 c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,s)
def title(c,lines,x,y,size=42,color=INK):
 for line in lines.split('\n'):text(c,line,x,y,size,'Display',color);y-=size*1.03
 return y
def para(c,s,x,y,w,size=10.5,leading=17,color=INK):
 st=ParagraphStyle('body',fontName='Text',fontSize=size,leading=leading,textColor=HexColor(color))
 p=Paragraph(s,st);_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return y-h
def line(c,x,y,w,color=SOFT):c.setStrokeColor(HexColor(color));c.setLineWidth(.4);c.line(x,y,x+w,y)
def image(c,p,x,y,w,h):c.drawImage(str(p),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
def page(c,w,h,no=None):
 c.setPageSize((w+18,h+18));c.setTrimBox((9,9,w+9,h+9));c.setBleedBox((0,0,w+18,h+18));c.setFillColor(HexColor(PAPER));c.rect(0,0,w+18,h+18,fill=1,stroke=0);c.translate(9,9)
 if no:
  text(c,'THOMAS BROADSIDE CO.',30,h-32,7,'Mono');text(c,f'{no:02}',w-43,24,7,'Mono',SOFT);line(c,30,42,w-60)
def code(c,url,x,y,size=65):
 widget=qr.QrCodeWidget(url);b=widget.getBounds();d=Drawing(size,size,transform=[size/(b[2]-b[0]),0,0,size/(b[3]-b[1]),0,0]);d.add(widget);renderPDF.draw(d,c,x,y)
def pdf(name):
 c=canvas.Canvas(str(OUT/name),pageCompression=1);c.setTitle(name.replace('-',' ').replace('.pdf',''));c.setAuthor('Thomas Broadside Co.');return c

# Six by nine postcard. Photography sits at >300 effective dpi, never stretched full-bleed.
c=pdf('postcard-6x9.pdf');w,h=648,432;page(c,w,h)
text(c,'THOMAS BROADSIDE CO.',32,389,10,'Mono');text(c,'AUSTIN, TEXAS / PRINTED HERE',32,363,7.5,'Mono',RED)
title(c,'History\nhas a\npulse.',32,284,68)
image(c,photo,287,143,329,185)
text(c,'PLATE 01 / A WORKING PRESS',288,128,6.8,'Mono',SOFT)
line(c,32,89,584)
para(c,'Founding documents. A family press.<br/>Something worth keeping.',32,69,360,11,17)
text(c,'thomasbroadside.co',448,45,9,'Mono');c.showPage()
page(c,w,h);text(c,'THOMAS BROADSIDE CO.',30,390,9,'Mono');title(c,'Give history a place\non your wall.',30,338,38)
para(c,'The Declaration of Independence, set in Caslon. The Preamble. The Bill of Rights. Broadsides for the rooms where we live, learn, and work.',30,239,278,11,18)
para(c,'Discover the collection and meet the family shop behind the paper.',30,157,264,10.5,17)
url=base+'?utm_source=pc-mail&utm_medium=direct-mail&utm_campaign=history-has-a-pulse&utm_content=postcard'
code(c,url,26,30,74);text(c,'STEP INTO THE SHOP',111,75,7.5,'Mono',RED);text(c,'thomasbroadside.co',111,55,9,'Mono');c.linkURL(url,(26,30,292,109),relative=1)
line(c,336,104,280)
text(c,'THOMAS BROADSIDE CO.',354,298,7.5,'Mono')
if args.address:para(c,args.address.replace('\n','<br/>'),354,279,245,8.5,13)
# Address/postage zone intentionally has no decorative rules or simulated postal marks.
c.showPage();c.save()

c=pdf('collectors-lookbook.pdf');w,h=396,612
page(c,w,h,1);text(c,'THE FIRST IMPRESSION',30,548,8,'Mono',RED);title(c,'History has\na pulse.',30,488,66)
image(c,photo,30,158,336,189);line(c,30,137,336)
para(c,'Founding documents. A family press.<br/>Something worth keeping.',30,116,300,12,19);c.showPage()
page(c,w,h,2);text(c,'01 / THE PLACE',30,548,8,'Mono',RED);title(c,'The place\nbehind the paper.',30,498,43)
image(c,photo,30,254,336,189)
para(c,'A broadside starts with words. Ours also starts with a working shop in Austin, Texas.',30,228,327,13,20)
para(c,'Thomas Broadside Co. is a venture of Thomas Graphics Inc. We bring the founding documents of America and the Western canon into the rooms where we live, learn, and work. The catalog, the paper, and the press belong to the same story.',30,163,327,10.5,17);c.showPage()
for num,slug,kicker in [(3,'declaration-of-independence','02 / THE FIRST IMPRESSION'),(4,'preamble-to-the-constitution','03 / A COMMON BEGINNING'),(5,'bill-of-rights','04 / WORDS WITH WEIGHT')]:
 d=by[slug];page(c,w,h,num);text(c,kicker,30,548,8,'Mono',RED)
 heading={'declaration-of-independence':'The Declaration.','preamble-to-the-constitution':'We the People.','bill-of-rights':'The Bill of Rights.'}[slug]
 title(c,heading,30,506,36)
 image(c,R/'site/art'/f'{slug}.jpg',58,133,280,353)
 text(c,'SOURCE / '+d['label']['source'].upper(),30,104,6.8,'Mono')
 text(c,'TYPE / CASLON     PRESS / AUSTIN, TEXAS',30,85,6.8,'Mono',SOFT)
 url=base+'documents/'+slug+'.html?utm_source=cat-mail&utm_medium=direct-mail&utm_campaign=history-has-a-pulse'
 c.linkURL(url,(58,133,338,486),relative=1);c.showPage()
page(c,w,h,6);text(c,'05 / CHOOSE YOUR IMPRESSION',30,548,8,'Mono',RED);title(c,'A way in.\nA work to keep.',30,495,49)
for y,num,head,body in [(347,'I','The digital broadside','The catalog\'s own typesetting, as a file you can print. A beginning for a wall, a lesson, or a gift.'),(239,'II','The press print','Printed on heavy cream cover in Austin. The physical sheet, made on our own press.'),(131,'III','The numbered edition','The Declaration on cotton paper, numbered of 250, with an embossed maker\'s mark. A work to keep.')]:
 line(c,30,y+22,336);text(c,num,30,y-1,12,'Mono',RED);text(c,head,65,y,19,'Display');para(c,body,65,y-18,298,10,16)
c.showPage()
page(c,w,h,7);text(c,'06 / FOR THE ROOMS THAT SHAPE US',30,548,7.5,'Mono',RED);title(c,'A classroom.\nA study.\nA place of work.',30,491,48)
para(c,'A document on a wall can begin a conversation that a screen never will. Give people something to stop before, read, and return to.',30,313,327,13,21)
para(c,'For school orders, collections, business gifts, and wholesale inquiries, write the shop desk. Tell us the room, the quantity, and the occasion. We will talk through the right sheets with you.',30,218,327,10.5,18)
text(c,'JEThomasPhD@gmail.com',30,117,10,'Mono',RED);text(c,'THOMAS GRAPHICS INC. / AUSTIN, TEXAS',30,86,7,'Mono');c.linkURL('mailto:JEThomasPhD@gmail.com',(30,104,345,133),relative=1);c.showPage()
page(c,w,h,8);text(c,'THE SHOP / THE SHEET / THE STORY',30,548,7.5,'Mono',RED);title(c,'Build\nsomething\nthat lasts.',30,477,64)
image(c,photo,30,157,240,135);code(c,base+'?utm_source=cat-mail&utm_medium=direct-mail&utm_campaign=history-has-a-pulse',285,183,75)
text(c,'THOMAS BROADSIDE CO.',30,122,10,'Mono');text(c,'thomasbroadside.co',30,99,10,'Mono',RED)
text(c,'A venture of Thomas Graphics Inc., Austin, Texas.',30,66,7,'Text',SOFT);c.showPage();c.save()

c=pdf('business-introduction-letter.pdf');w,h=612,792;page(c,w,h)
text(c,'THOMAS BROADSIDE CO.',45,741,11,'Mono');text(c,'AUSTIN, TEXAS / THE SHOP DESK',45,716,8,'Mono',RED);line(c,45,694,522)
title(c,'Give the room\nsomething worth reading.',45,637,51)
para(c,'For schools, law offices, libraries, museum shops, and people who give thoughtful gifts.',45,517,491,12.5,20)
image(c,R/'site/art/declaration-of-independence.jpg',367,225,195,260)
para(c,'The Declaration. The Preamble. The Bill of Rights. Founding documents set in Caslon, printed by a family shop in Austin, Texas.',45,445,280,11,19)
para(c,'We make broadsides that put the words themselves at the center of a room. Every design carries its source on the sheet. The physical work comes from our own press.',45,339,280,11,19)
para(c,'Planning a classroom wall, a business gift, or a shop collection? Write with the quantity, occasion, and date. We will help you choose the right sheets and confirm the details.',45,219,491,11,19)
text(c,'The Shop Desk, Thomas Broadside Co.',45,124,11,'Italic');text(c,'JEThomasPhD@gmail.com',45,98,10,'Mono',RED)
line(c,45,72,522);text(c,'BUILD SOMETHING THAT LASTS',45,49,8,'Mono');text(c,'thomasbroadside.co',429,49,8,'Mono');c.showPage();c.save()
print('Created postcard, 8-page lookbook, and business introduction letter.')
