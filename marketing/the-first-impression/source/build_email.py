"""Build three unsent email drafts, with HTML/text and embedded-image EML.
No recipients, credentials, external service calls, or sends.
"""
from pathlib import Path
from email.message import EmailMessage
from email.policy import SMTP
from html import escape
K=Path(__file__).resolve().parents[1]; EMAIL='JEThomasPhD@gmail.com'; BASE='https://thomasbroadside.co/'
letters=[
('origin-story','Before it was a relic, it was news.','Introducing The First Impression','The document had to leave the room.',[
 'On the night of July 4, 1776, the Declaration went to John Dunlap’s Philadelphia print shop. By the next day, printed copies could begin their journey into the world.',
 'Our new origin story follows the hands that helped public words reach the public: Franklin’s printer’s eye, Jefferson’s draft, Dunlap’s first impression, the reading Washington ordered for his troops, and Hamilton’s later arguments in the newspaper.',
 'Watch the 65-second film, with reconstructed historical scenes and the working press in our Austin shop. Then look at the surviving documents and follow the sources.',
 'Finally, find a sheet to live with. Our broadsides bring the words into the rooms where we read, think, teach, and make a life.'], 'Watch The First Impression','origins.html'),
('july-fourth','This July 4, read the words again.','A letter for Independence Day','Before the glass case, there was a press.',[
 'The Declaration’s first public life was a printed one. John Dunlap’s shop set the approved text in type on the night of July 4, 1776. Copies went out to assemblies, committees and commanders.',
 'For Independence Day, we invite you to return to that moment: to the words, the working draft, the first printing, and the sources that preserve them.',
 'Our Declaration is a contemporary composition of its celebrated passage, set in Caslon and printed in Austin. It carries the broadside tradition into a new room.',
 'Read the words. Keep the source. Make your own first impression.'], 'Discover the Declaration','documents/declaration-of-independence.html'),
('partner-introduction','A founding-document story for your space.','For libraries, museum shops and classrooms','Bring the founding into the room.',[
 'The First Impression is a visual story of public words becoming public documents: from the working draft to Dunlap’s press, the reading to Washington’s troops, and the later Federalist essays in newspapers.',
 'Thomas Broadside Co. pairs that source-led story with broadsides of founding documents and historical portraits, printed by our family shop in Austin, Texas.',
 'If you are planning a library display, classroom order, museum-shop selection or a gift collection, write us with your quantities and timing. We can help you choose from the available formats.',
 'The online story includes a short film, the original source record, and a path into the collection.'], 'Explore the origin story','origins.html')]
for slug,subject,kicker,heading,paragraphs,cta,target in letters:
    utm=f'utm_source=email&utm_medium=email&utm_campaign=the-first-impression&utm_content={slug}'
    url=BASE+target+'?'+utm;film=BASE+'origins.html?'+utm;unsub='mailto:'+EMAIL+'?subject=Unsubscribe%20from%20Thomas%20Broadside%20Co.'
    body=''.join('<p style="margin:0 0 21px;font:17px/1.75 Georgia,serif;color:#201a10">'+escape(p)+'</p>' for p in paragraphs)
    html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(subject)}</title><body style="margin:0;background:#e9e2d0"><div style="display:none;max-height:0;overflow:hidden">The First Impression. A printer’s night. A document on its way to the world.</div><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px 12px"><table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#f1ece0"><tr><td style="padding:32px;font:13px/1.5 'Courier New',monospace;letter-spacing:2px;border-bottom:1px solid #c3b8a3">THOMAS BROADSIDE CO.</td></tr><tr><td><a href="{escape(film)}"><img src="https://thomasbroadside.co/media/origin/share-card-v2.jpg" width="600" alt="Before it was a relic, it was news. Watch The First Impression." style="display:block;width:100%;height:auto;border:0"></a></td></tr><tr><td style="padding:34px 32px"><p style="font:11px/1.6 'Courier New',monospace;letter-spacing:1px;color:#9e3123;text-transform:uppercase">{escape(kicker)}</p><h1 style="font:normal 38px/1.13 Georgia,serif;color:#201a10;margin:20px 0 28px">{escape(heading)}</h1>{body}<table role="presentation" cellpadding="0" cellspacing="0"><tr><td bgcolor="#9e3123" style="padding:16px 20px"><a href="{escape(url)}" style="font:13px/1.4 'Courier New',monospace;text-decoration:none;color:#faf6ea">{escape(cta)} →</a></td></tr></table><p style="font:14px/1.7 Georgia,serif;margin:25px 0"><a href="{escape(film)}#sources" style="color:#9e3123">Read the source notes and the film transcript</a></p><p style="font:italic 16px/1.6 Georgia,serif">The Shop Desk<br>Thomas Broadside Co.</p></td></tr><tr><td style="padding:25px 32px;border-top:1px solid #c3b8a3;font:12px/1.7 Georgia,serif;color:#675b47"><strong>BUILD SOMETHING THAT LASTS</strong><br>Thomas Broadside Co. · A venture of Thomas Graphics Inc.<br>9501 N Interstate Hwy 35, Austin, TX 78753<br><a href="mailto:{EMAIL}" style="color:#675b47">{EMAIL}</a><br><br>Historical scenes are contemporary reconstructions. The shop footage records our working Austin press.<br><a href="{unsub}" style="color:#675b47">Unsubscribe by email</a></td></tr></table></td></tr></table></body></html>'''
    plain=subject+'\n'+kicker+'\n\n'+'\n\n'.join(paragraphs)+f'\n\n{cta}: {url}\n\nSources and film: {film}\n\nThe Shop Desk\nThomas Broadside Co.\n9501 N Interstate Hwy 35, Austin, TX 78753\n{EMAIL}\n\nHistorical scenes are contemporary reconstructions.\nTo unsubscribe, reply with Unsubscribe.\n'
    (K/'email'/f'{slug}.html').write_text(html,encoding='utf-8');(K/'email'/f'{slug}-preview.html').write_text(html.replace('https://thomasbroadside.co/media/origin/share-card-v2.jpg','../social/09-linkedin-share.png'),encoding='utf-8');(K/'email'/f'{slug}.txt').write_text(plain,encoding='utf-8')
    msg=EmailMessage(policy=SMTP);msg['Subject']=subject;msg['From']=f'Thomas Broadside Co. <{EMAIL}>';msg['Reply-To']=EMAIL;msg['X-Unsent']='1';msg['List-Unsubscribe']='<'+unsub+'>';msg.set_content(plain)
    msg.add_alternative(html.replace('https://thomasbroadside.co/media/origin/share-card-v2.jpg','cid:tfi-hero'),subtype='html')
    msg.get_payload()[-1].add_related((K/'source/email-header.jpg').read_bytes(),maintype='image',subtype='jpeg',cid='<tfi-hero>')
    (K/'email'/f'{slug}.eml').write_bytes(msg.as_bytes())
print('Three email sets exported: evergreen origin, July 4, partner introduction.')
