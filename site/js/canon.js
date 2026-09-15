/* Preserve native document navigation when leaving the film for the collection. */
document.querySelector('[data-canon-collection]')?.addEventListener('click', () => {
  document.querySelector('[data-press-film]')?.close();
});
