(() => {
  'use strict';
  const all = (s, el=document) => Array.from(el.querySelectorAll(s));
  const one = (s, el=document) => el.querySelector(s);
  const quote = one('#quote'), design = one('#design'), format = one('#format');
  const cards = all('.plate'), plateDialog = one('#plate-dialog'), filmDialog = one('#film-dialog');
  const video = one('video',filmDialog), image = one('#view-image');
  let selected = cards[0], mode = 'door';
  const title = () => one('h3',selected).textContent;
  const views = {door:'Illustrated placement on a double garage door.', wide:'Double-door composition · 2:1 artwork study.', single:'Single-door composition · 6:5 artwork study.'};
  function view(next) {
    mode = next;
    const no = selected.dataset.no;
    image.alt = title() + ' — ' + views[mode];
    image.src = mode === 'door' ? '/media/christmas/door-'+no+'.jpg' : '/media/christmas/plate-'+no+'-'+mode+'.webp';
    one('#study-type').textContent = views[mode];
    all('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === mode)));
  }
  if (typeof plateDialog.showModal === 'function') {
    cards.forEach(card => {
      const link = one('.plate-open',card);
      link.setAttribute('aria-haspopup','dialog');
      link.addEventListener('click',e => {
        if (e.ctrlKey||e.metaKey||e.shiftKey||e.altKey) return;
        e.preventDefault(); selected=card;
        one('#plate-title').textContent = title();
        one('#dialog-folio').textContent = 'The plate book / No. '+card.dataset.roman;
        view('door'); plateDialog.showModal();
      });
    });
    all('[data-view]').forEach(b => b.addEventListener('click', () => view(b.dataset.view)));
    one('#select-plate').addEventListener('click',e => {
      e.preventDefault(); design.selectedIndex = cards.indexOf(selected);
      if(mode==='single') format.value='Single door';
      if(mode==='wide') format.value='Double door';
      plateDialog.close(); location.hash='fitting'; design.focus({preventScroll:true});
    });
    one('[data-film]').addEventListener('click', e => {
      if (e.ctrlKey||e.metaKey||e.shiftKey||e.altKey) return;
      e.preventDefault(); if(!video.getAttribute('src')) video.src=e.currentTarget.href;
      filmDialog.showModal(); video.play().catch(()=>{});
    });
    filmDialog.addEventListener('close',()=>video.pause());
    [plateDialog,filmDialog].forEach(d => {
      one('.close',d).addEventListener('click',()=>d.close());
      d.addEventListener('click',e=>{
        if(e.target!==d) return;
        const r=d.getBoundingClientRect(); if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom) d.close();
      });
    });
  }
  quote.addEventListener('submit',() => {
    const w=one('#width').value,h=one('#height').value;
    const summary=['Thomas Broadside Co. / The Christmas Door',design.value,'Door layout: '+format.value,
      'Door face: '+(w?w+' in wide':'width to confirm')+' × '+(h?h+' in high':'height to confirm'),
      'Please quote the fitted covering, material, attachment, and timing.'];
    const incoming=new URLSearchParams(location.search);
    const tags=['utm_source','utm_medium','utm_campaign','utm_content','utm_term'].flatMap(k=>{
      const v=incoming.get(k); return v?[k+'='+v.replace(/[^a-zA-Z0-9._ -]/g,'').slice(0,80)]:[];
    });
    if(tags.length) summary.push('Campaign: '+tags.join('; '));
    one('#brief').value=summary.join('\n');
  });
})();
