/* Behavioural checks for media consent, fallbacks and keyboard-dialog lifecycle. */
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../site/js/living-press.js'), 'utf8');
function setup({reduced=false,saveData=false,mobile=false,blocked=false}={}) {
 const media={matches:reduced,addEventListener(type,fn){this.change=fn;}};
 const element=()=>({hidden:true,listeners:{},attrs:{},classList:{add(){},remove(){}},addEventListener(t,f){this.listeners[t]=f;},setAttribute(k,v){this.attrs[k]=v;},getAttribute(k){return this.attrs[k]||null;},focus(){this.focused=true;}});
 const video=()=>({...element(),paused:true,dataset:{desktop:'wide.mp4',mobile:'portrait.mp4',src:'film.mp4'},loads:0,load(){this.loads++;},play(){if(blocked)return Promise.reject(Error('blocked'));this.paused=false;this.listeners.playing?.();return Promise.resolve();},pause(){this.paused=true;this.listeners.pause?.();},set src(v){this.attrs.src=v;},get src(){return this.attrs.src||'';}});
 const hero=video(),film=video(),toggle=element(),open=element(),close=element(),dialog=Object.assign(element(),{open:false,showModal(){this.open=true;},close(){this.open=false;this.listeners.close?.();},querySelector(s){return s==='video'?film:close;}});
 const map={'[data-press-loop]':hero,'[data-motion-toggle]':toggle,'[data-press-film]':dialog};
 const document={hidden:false,listeners:{},querySelector(s){return map[s];},querySelectorAll(){return [open];},addEventListener(t,f){this.listeners[t]=f;}};
 let intersection;
 const context={document,navigator:{connection:{saveData}},matchMedia(q){return q.includes('reduce')?media:{matches:mobile};},IntersectionObserver:class{constructor(fn){intersection=fn;}observe(){intersection([{isIntersecting:true}]);}},window:{IntersectionObserver:true}};
 vm.runInNewContext(source,context);
 return {hero,film,toggle,open,close,dialog,document,media,view(v){intersection([{isIntersecting:v}]);}};
}
(async()=>{
 let s=setup();assert.equal(s.hero.src,'wide.mp4');assert.equal(s.hero.paused,false);assert.equal(s.film.src,'');
 s.toggle.listeners.click();assert.equal(s.hero.paused,true);s.view(false);s.view(true);assert.equal(s.hero.paused,true,'manual pause survives visibility changes');
 s.toggle.listeners.click();assert.equal(s.hero.paused,false);s.open.listeners.click();assert.equal(s.dialog.open,true);assert.equal(s.hero.paused,true);assert.equal(s.film.src,'film.mp4');
 s.close.listeners.click();assert.equal(s.dialog.open,false);assert.equal(s.film.paused,true);assert.equal(s.open.focused,true);
 s.open.listeners.click();s.open.focused=false;s.dialog.listeners.click({target:{closest(){return {href:'/#documents'};}}});assert.equal(s.dialog.open,false,'collection and transcript links close the modal');assert.equal(s.film.paused,true);assert.equal(s.open.focused,false,'navigation does not restore focus to the film trigger');
 s=setup({reduced:true});assert.equal(s.hero.src,'','reduced motion prevents fetch');s.toggle.listeners.click();assert.equal(s.hero.paused,false,'explicit play remains possible');
 s=setup({saveData:true});assert.equal(s.hero.src,'','data saving prevents fetch');
 s=setup({mobile:true});assert.equal(s.hero.src,'portrait.mp4');s.view(false);assert.equal(s.hero.paused,true);s.view(true);assert.equal(s.hero.paused,false);
 s.document.hidden=true;s.document.listeners.visibilitychange();assert.equal(s.hero.paused,true);
 s=setup({blocked:true});await Promise.resolve();assert.equal(s.hero.paused,true);s.hero.listeners.error();assert.equal(s.toggle.hidden,true,'failed media leaves the static poster');
 console.log('PASS: lazy film, wide/portrait choice, manual pause, offscreen/background pause, reduced motion, data saving, blocked autoplay, error fallback, and dialog focus.');
})();
