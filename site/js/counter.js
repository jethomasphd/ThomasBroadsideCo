/* The counter form: posts inquiries and no-payment-link orders to /api/counter.
   The shop desk answers by letter; a human confirms every order [D9]. */
(function () {
  document.querySelectorAll('form[data-counter]').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var out = form.querySelector('[data-counter-result]');
      var btn = form.querySelector('button[type=submit]');
      var data = {
        kind: form.getAttribute('data-kind') || 'order',
        items: form.getAttribute('data-items') || '',
        name: (form.name && form.name.value) || '',
        email: (form.email && form.email.value) || '',
        address: (form.address && form.address.value) || '',
        message: (form.message && form.message.value) || '',
      };
      btn.disabled = true;
      fetch('/api/counter', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(data),
      })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.ok) {
            out.textContent = res.word + ' Your order number is ' + res.id + '.';
            form.querySelectorAll('input,textarea').forEach(function (el) { el.value = ''; });
          } else {
            out.textContent = res.error || 'Something slipped. Write us at the address in the footer.';
            btn.disabled = false;
          }
        })
        .catch(function () {
          out.textContent = 'The counter is unreachable. Write us directly and we will make it right.';
          btn.disabled = false;
        });
    });
  });
})();
