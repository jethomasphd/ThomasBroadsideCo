if (!customElements.get('tb-living-press')) customElements.define('tb-living-press', class extends HTMLElement {
  connectedCallback() {
    this.events = new AbortController(); const opt = { signal: this.events.signal };
    const loop = this.querySelector('[data-loop]'), button = this.querySelector('[data-toggle]');
    const dialog = this.querySelector('dialog'), film = this.querySelector('[data-film]'), open = this.querySelector('[data-open]');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)'); let paused = false, visible = true;
    const start = () => { if (!loop.src) loop.src = matchMedia('(max-width:600px)').matches ? loop.dataset.mobile : loop.dataset.desktop; loop.play().catch(() => {}); };
    const resume = () => { if (loop && !paused && visible && !document.hidden && !dialog?.open && !reduced.matches && !navigator.connection?.saveData) start(); };
    if (loop && button) {
      button.hidden = false;
      const state = () => { button.textContent = loop.paused ? '▶' : 'Ⅱ'; button.setAttribute('aria-label', loop.paused ? 'Play press motion' : 'Pause press motion'); };
      loop.addEventListener('playing', () => { loop.classList.add('is-playing'); state(); }, opt);
      loop.addEventListener('pause', state, opt);
      loop.addEventListener('error', () => { loop.classList.remove('is-playing'); button.hidden = true; }, opt);
      button.addEventListener('click', () => { paused = !loop.paused; paused ? loop.pause() : start(); }, opt);
      this.observer = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; visible ? resume() : loop.pause(); }, {threshold:.08}); this.observer.observe(loop);
      document.addEventListener('visibilitychange', () => document.hidden ? loop.pause() : resume(), opt);
      reduced.addEventListener('change', () => reduced.matches ? loop.pause() : resume(), opt);
    }
    if (dialog && open && typeof dialog.showModal === 'function') {
      open.hidden = false;
      open.addEventListener('click', () => { loop?.pause(); if (!film.src) film.src = film.dataset.src; dialog.showModal(); film.play().catch(() => {}); }, opt);
      this.querySelector('[data-close]').addEventListener('click', () => dialog.close(), opt);
      dialog.addEventListener('close', () => { film.pause(); open.focus(); }, opt);
    }
  }
  disconnectedCallback() { this.events?.abort(); this.observer?.disconnect(); this.querySelectorAll('video').forEach(video => video.pause()); }
});
