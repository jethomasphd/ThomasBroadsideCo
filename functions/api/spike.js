// The spike — the order queue, named for the spindle where finished jobs
// get spiked. Token-guarded; serves the pressroom page and the tools.
//   GET  ?status=QUEUED&limit=100      → { orders: [...] }
//   POST { id, status, note?, tracking? } → { ok }
// Statuses: NEW → CONFIRMED → QUEUED → ON_PRESS → SHIPPED (+ HOLD, CANCELED) [D5].
// SHIPPED may only arrive from a human hand via the pressroom page —
// automated callers must never send it [D9]; the guard below asks for the
// human flag the pressroom page sets.

const STATUSES = ['NEW', 'CONFIRMED', 'QUEUED', 'ON_PRESS', 'SHIPPED', 'HOLD', 'CANCELED'];

function authed(request, env) {
  const h = request.headers.get('authorization') || '';
  const token = h.replace(/^Bearer\s+/i, '');
  return env.PRESS_TOKEN && token === env.PRESS_TOKEN;
}

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!authed(request, env)) return json({ error: 'the shop token is required' }, 401);
  const url = new URL(request.url);
  const want = url.searchParams.get('status');
  const limit = Math.min(parseInt(url.searchParams.get('limit'), 10) || 200, 500);

  const orders = [];
  let cursor;
  do {
    const page = await env.SHOPKV.list({ prefix: 'order:', cursor });
    for (const k of page.keys) {
      const raw = await env.SHOPKV.get(k.name);
      if (!raw) continue;
      const o = JSON.parse(raw);
      if (!want || o.status === want) orders.push(o);
      if (orders.length >= limit) break;
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor && orders.length < limit);

  orders.sort((a, b) => (a.ts < b.ts ? 1 : -1));
  return json({ orders });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!authed(request, env)) return json({ error: 'the shop token is required' }, 401);
  let data;
  try { data = await request.json(); } catch { return json({ error: 'bad request' }, 400); }

  const id = String(data.id || '').slice(0, 24);
  const status = String(data.status || '');
  if (!STATUSES.includes(status)) return json({ error: `status must be one of ${STATUSES.join(', ')}` }, 400);

  const raw = await env.SHOPKV.get(`order:${id}`);
  if (!raw) return json({ error: 'no such order on the spike' }, 404);
  const order = JSON.parse(raw);

  if (status === 'SHIPPED') {
    // The human gate [D5][D9]: the pressroom page sends by:"hand" plus a
    // tracking number. Tools and clerks do not.
    if (data.by !== 'hand') return json({ error: 'SHIPPED is set by a human at the pressroom page, never by a machine' }, 403);
    if (!data.tracking || String(data.tracking).trim().length < 6) {
      return json({ error: 'a tracking number is required to mark SHIPPED' }, 400);
    }
    order.tracking = String(data.tracking).trim().slice(0, 60);
  }

  const from = order.status;
  order.status = status;
  if (data.note) order.note = [order.note, String(data.note).slice(0, 300)].filter(Boolean).join(' · ');
  order.history = order.history || [];
  order.history.push({ ts: new Date().toISOString(), from, to: status, by: data.by === 'hand' ? 'hand' : 'clerk' });
  await env.SHOPKV.put(`order:${id}`, JSON.stringify(order));

  // Shipped note to the customer, if the mail rail is configured.
  if (status === 'SHIPPED' && env.RESEND_API_KEY && env.MAIL_FROM && order.email) {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        from: env.MAIL_FROM, to: [order.email],
        subject: `Your tube is on its way — ${order.id}`,
        text: `It shipped today from the shop in Austin, rolled and capped by hand.\n\nTracking: ${order.tracking}\n\nHang it square.\n\nThe Shop Desk\nThomas Broadside Co.\nAustin: Printed by Thomas Graphics`,
      }),
    }).catch(() => {});
  }

  return json({ ok: true, id, status });
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
}
