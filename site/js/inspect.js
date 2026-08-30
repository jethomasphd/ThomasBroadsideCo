// The inspection view: click a framed sheet, see the full-resolution
// render, zoom to actual pixels, pan by drag or scroll. No dependencies.
(function () {
  var overlay = document.querySelector('[data-inspect]');
  if (!overlay) return;
  var img = overlay.querySelector('[data-inspect-img]');
  var scroller = overlay.querySelector('[data-inspect-scroll]');

  function open(src, alt) {
    img.src = src;
    img.alt = alt || 'The sheet, at full resolution';
    overlay.classList.remove('is-zoom');
    overlay.hidden = false;
    document.body.style.overflow = 'hidden';
  }
  function close() {
    overlay.hidden = true;
    document.body.style.overflow = '';
    img.src = '';
  }

  document.querySelectorAll('[data-inspect-open]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      var sheet = el.querySelector('.sheet__img');
      if (!sheet) return;
      e.preventDefault();
      // the src already carries its cache stamp; load the same full file
      open(sheet.getAttribute('src'), sheet.getAttribute('alt'));
    });
  });

  img.addEventListener('click', function (e) {
    var zoomed = overlay.classList.toggle('is-zoom');
    if (zoomed) {
      // center the zoom near where the reader clicked
      var rx = (e.offsetX || 0) / (img.clientWidth || 1);
      var ry = (e.offsetY || 0) / (img.clientHeight || 1);
      requestAnimationFrame(function () {
        scroller.scrollLeft = img.clientWidth * rx - scroller.clientWidth / 2;
        scroller.scrollTop = img.clientHeight * ry - scroller.clientHeight / 2;
      });
    }
  });

  // drag to pan while zoomed (mouse; touch pans natively)
  var drag = null;
  scroller.addEventListener('mousedown', function (e) {
    if (!overlay.classList.contains('is-zoom')) return;
    drag = { x: e.clientX, y: e.clientY, left: scroller.scrollLeft, top: scroller.scrollTop, moved: false };
  });
  window.addEventListener('mousemove', function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
    scroller.scrollLeft = drag.left - dx;
    scroller.scrollTop = drag.top - dy;
  });
  window.addEventListener('mouseup', function (e) {
    if (drag && drag.moved) {
      // a drag is not a click: swallow the zoom toggle it would fire
      img.addEventListener('click', function stop(ev) {
        ev.stopImmediatePropagation();
        img.removeEventListener('click', stop, true);
      }, true);
    }
    drag = null;
  });

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay || e.target === scroller) close();
  });
  overlay.querySelector('[data-inspect-close]').addEventListener('click', close);
  window.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !overlay.hidden) close();
  });
})();
