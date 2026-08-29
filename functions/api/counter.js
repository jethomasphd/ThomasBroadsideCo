// The counter — where the store takes an order or a wholesale inquiry when
// no payment link is involved. Writes a NEW order to KV; the Shopkeeper
// letters the customer and a human confirms [D9]. If Resend is configured,
// the shop inbox gets a note immediately.

const MAX = { name: 120, email: 160, address: 400, message: 1200, items: 600 };

function orderId() {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const r = Array.from(crypto.getRandomValues(new Uint8Array(3)))
    .map((b) => 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'[b % 31]).join('');
  return `TB-${d}-${r}0`.slice(0, 16);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  let data;
  try { data = await request.json(); } catch { return json({ ok: false, error: 'bad request' }, 400); }

  const kind = data.kind === 'wholesale' ? 'wholesale' : 'order';
  const name = clip(data.name, MAX.name);
  const email = clip(data.email, MAX.email);
  const address = clip(data.address, MAX.address);
  const message = clip(data.message, MAX.message);
  const items = clip(data.items, MAX.items); // "SKU:tier:qty|SKU:tier:qty"

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ ok: false, error: 'a working email is required so the shop can reply' }, 400);
  }
  if (!name) return json({ ok: false, error: 'a name is required' }, 400);

  const id = orderId();
  const order = {
    id, ts: new Date().toISOString(), status: 'NEW', kind,
    name, email, items, amount_usd: 0, source: 'site', address,
    note: message, history: [{ ts: new Date().toISOString(), to: 'NEW', by: 'counter' }],
  };
  await env.SHOPKV.put(`order:${id}`, JSON.stringify(order));

  if (env.RESEND_API_KEY && env.MAIL_FROM) {
    // A note to the shop desk only. Customer letters are drafted and
    // human-approved before sending [D9] — no auto-reply to the customer here.
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        from: env.MAIL_FROM,
        to: [env.MAIL_FROM.replace(/^.*</, '').replace(/>$/, '')],
        subject: `[counter] ${kind} ${id} — ${name}`,
        text: `${kind.toUpperCase()} at the counter\n\n${id}\n${name} <${email}>\n${items || '(no items listed)'}\n${address || ''}\n\n${message || ''}\n\nThe order book has it as NEW. — the counter`,
      }),
    }).catch(() => {});
  }

  return json({ ok: true, id, word: 'The shop has your note and will reply by letter within two working days.' });
}

function clip(v, n) { return typeof v === 'string' ? v.trim().slice(0, n) : ''; }
function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
}
