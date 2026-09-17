/* Native media, explicit sound, no third-party player or tracking. */
(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const hero = document.querySelector('[data-press-loop]');
  const toggle = document.querySelector('[data-motion-toggle]');
  const dialog = document.querySelector('[data-press-film]');
  let manualPause = false;
  let inView = true;
  let returnFocus = null;
  const saveData = navigator.connection?.saveData === true;
  const loadLoop = () => {
    if (!hero || hero.getAttribute('src')) return;
    hero.src = matchMedia('(max-width: 600px)').matches ? hero.dataset.mobile : hero.dataset.desktop;
    hero.load();
  };
  const syncButton = () => {
    if (!toggle || !hero) return;
    const playing = !hero.paused;
    toggle.textContent = playing ? 'Ⅱ' : '▶';
    const label = toggle.dataset?.motionLabel || 'press motion';
    toggle.setAttribute('aria-label', `${playing ? 'Pause' : 'Play'} ${label}`);
  };
  const play = () => {
    loadLoop();
    const promise = hero?.play();
    if (promise) promise.catch(syncButton);
  };
  if (hero && toggle) {
    toggle.hidden = false;
    hero.addEventListener('playing', () => { hero.classList.add('is-playing'); syncButton(); });
    hero.addEventListener('pause', syncButton);
    hero.addEventListener('error', () => { hero.classList.remove('is-playing'); toggle.hidden = true; });
    toggle.addEventListener('click', () => {
      if (hero.paused) { manualPause = false; play(); }
      else { manualPause = true; hero.pause(); }
    });
    const resume = () => {
      if (!manualPause && !reduced.matches && !saveData && inView && !document.hidden && !dialog?.open) play();
    };
    if ('IntersectionObserver' in window) new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      if (inView) resume(); else hero.pause();
    }, { threshold: .08 }).observe(hero);
    else resume();
    document.addEventListener('visibilitychange', () => document.hidden ? hero.pause() : resume());
    reduced.addEventListener('change', () => reduced.matches ? hero.pause() : resume());
  }
  if (dialog && typeof dialog.showModal === 'function') {
    const film = dialog.querySelector('video');
    document.querySelectorAll('[data-film-open]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => {
        returnFocus = button;
        hero?.pause();
        if (!film.getAttribute('src')) film.src = film.dataset.src;
        dialog.showModal();
        film.play().catch(() => {});
      });
    });
    dialog.querySelector('[data-film-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      // A same-page collection or transcript link must leave the modal as it navigates.
      if (event.target.closest?.('a[href]')) { returnFocus = null; dialog.close(); return; }
      if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); }
    });
    dialog.addEventListener('close', () => { film.pause(); returnFocus?.focus(); });
  }
})();
