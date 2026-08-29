/* The bell: our own door counter. Aggregate counts only, no cookies, no
   fingerprinting, honors Do Not Track [D2][D7]. */
(function () {
  try {
    if (navigator.doNotTrack === '1' || window.doNotTrack === '1') return;
    var p = location.pathname;
    if (p.indexOf('/pressroom') === 0 || p.indexOf('/ledger') === 0) return;
    var ref = '';
    try { ref = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) {}
    if (ref === location.hostname) ref = '';
    var body = JSON.stringify({ p: p, r: ref });
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/bell', new Blob([body], { type: 'application/json' }));
    } else {
      fetch('/api/bell', { method: 'POST', body: body, keepalive: true, headers: { 'content-type': 'application/json' } });
    }
  } catch (e) { /* the bell never breaks the store */ }
})();
