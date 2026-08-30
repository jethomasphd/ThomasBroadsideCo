/* The cart: your tube. LocalStorage until checkout; prices are display-only —
   the checkout worker re-prices every line from the catalog server-side.
   With Stripe unwired the checkout hands the order to the shop desk instead,
   so the store sells either way [D12]. */
(function () {
  var KEY = 'tb_cart';
  var CAT = window.TB_CATALOG || {};

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; }
  }
  function write(items) {
    try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) {}
    badge();
  }
  function count() {
    return read().reduce(function (n, it) { return n + (it.qty || 1); }, 0);
  }
  function badge() {
    document.querySelectorAll('[data-cart-count]').forEach(function (b) {
      var n = count();
      b.textContent = n || '';
      if (n) { b.removeAttribute('data-zero'); } else { b.setAttribute('data-zero', ''); }
    });
  }
  function toast(html) {
    var t = document.querySelector('[data-toast]');
    if (!t) return;
    t.innerHTML = html;
    t.classList.add('show');
    clearTimeout(t._h);
    t._h = setTimeout(function () { t.classList.remove('show'); }, 3200);
  }
  function priceOf(sku, tier) {
    var e = CAT[sku];
    return e && e.tiers && e.tiers[tier] ? e.tiers[tier].price : null;
  }
  function titleOf(sku) {
    return (CAT[sku] && CAT[sku].title) || sku;
  }

  // add-to-cart buttons: data-add="SKU:tier"
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-add]');
    if (!b) return;
    var parts = b.getAttribute('data-add').split(':');
    var sku = parts[0], tier = parts[1];
    if (priceOf(sku, tier) == null) return;
    var items = read();
    var hit = items.find(function (it) { return it.sku === sku && it.tier === tier; });
    if (hit) { hit.qty = Math.min((hit.qty || 1) + 1, 25); } else { items.push({ sku: sku, tier: tier, qty: 1 }); }
    write(items);
    toast('In the tube — <a href="/cart.html">view your cart</a>');
  });

  // the cart page
  var root = document.querySelector('[data-cart-root]');
  if (root) {
    var render = function () {
      var items = read();
      if (!items.length) {
        root.innerHTML = '<p class="lede">Your tube is empty.</p>' +
          '<p><a class="btn btn--solid" href="/#documents">See the collection</a></p>';
        return;
      }
      var subtotal = 0;
      var lines = items.map(function (it, i) {
        var price = priceOf(it.sku, it.tier) || 0;
        subtotal += price * it.qty;
        return '<div class="cart-line">' +
          '<div><p class="cart-line__title">' + titleOf(it.sku) + '</p>' +
          '<p class="cart-line__meta">' + it.tier + ' · ' + it.sku + '</p></div>' +
          '<div class="qty"><button data-dec="' + i + '" aria-label="fewer">−</button>' +
          '<span>' + it.qty + '</span>' +
          '<button data-inc="' + i + '" aria-label="more">+</button></div>' +
          '<span class="cart-line__price">$' + (price * it.qty).toLocaleString() + '</span>' +
          '<button class="remove" data-rm="' + i + '">Remove</button>' +
          '</div>';
      }).join('');
      root.innerHTML =
        '<div class="cart-lines">' + lines + '</div>' +
        '<div class="cart-total"><span>Subtotal — shipping and any tax at checkout.<br>' +
        '<span class="form-note">Free U.S. shipping on prints over $75. Everything ships in one tube.</span></span>' +
        '<span class="sum">$' + subtotal.toLocaleString() + '</span></div>' +
        '<p style="display:flex;gap:1rem;flex-wrap:wrap;">' +
        '<button class="btn btn--solid" data-checkout style="font-size:.8rem;padding:1.1em 2.4em;">Check out</button>' +
        '<a class="btn btn--quiet" href="/#documents">Keep looking</a></p>' +
        '<p class="form-note" data-cart-word></p>';
    };
    root.addEventListener('click', function (ev) {
      var items = read();
      var t = ev.target;
      if (t.hasAttribute('data-inc')) { items[+t.getAttribute('data-inc')].qty = Math.min(items[+t.getAttribute('data-inc')].qty + 1, 25); write(items); render(); }
      else if (t.hasAttribute('data-dec')) { var i = +t.getAttribute('data-dec'); items[i].qty -= 1; if (items[i].qty < 1) items.splice(i, 1); write(items); render(); }
      else if (t.hasAttribute('data-rm')) { items.splice(+t.getAttribute('data-rm'), 1); write(items); render(); }
      else if (t.hasAttribute('data-checkout')) { checkout(t); }
    });
    var checkout = function (btn) {
      var word = root.querySelector('[data-cart-word]');
      btn.disabled = true;
      word.textContent = 'Opening the register…';
      fetch('/api/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ items: read() }),
      }).then(function (r) { return r.json().then(function (j) { return { s: r.status, j: j }; }); })
        .then(function (res) {
          if (res.j.url) { location.href = res.j.url; return; }
          btn.disabled = false;
          if (res.j.desk) {
            word.textContent = 'The register is being wired. Leave your details and the shop desk will reply with a payment link:';
            document.querySelector('[data-desk-fallback]').hidden = false;
            var form = document.querySelector('[data-desk-fallback] form');
            if (form) form.setAttribute('data-items', read().map(function (it) { return it.sku + ':' + it.tier + ':' + it.qty; }).join('|'));
          } else {
            word.textContent = res.j.error || 'Something slipped. Try again, or write the desk from The Press page.';
          }
        })
        .catch(function () { btn.disabled = false; word.textContent = 'The register is unreachable. Write the desk from The Press page and we will make it right.'; });
    };
    render();
  }

  // the thanks page clears the tube
  if (location.pathname.indexOf('/thanks') === 0 && location.search.indexOf('paid=1') > -1) {
    write([]);
  }

  badge();
})();
