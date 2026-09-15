/* Optional reading orientation. All story content and links work without JS. */
(() => {
  'use strict';
  const links = [...document.querySelectorAll('.origin-chapter-nav a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a,b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      links.forEach(link => { if (link.hash === '#' + visible.target.id) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current'); });
    }, { rootMargin: '-12% 0px -40% 0px', threshold: [0, .25, .5] });
    links.forEach(link => { const section = document.getElementById(link.hash.slice(1)); if (section) observer.observe(section); });
  }
  document.querySelector('[data-origin-collection]')?.addEventListener('click', () => document.querySelector('[data-press-film]')?.close());
})();
