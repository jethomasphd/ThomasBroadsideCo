// The paid counter — Stripe's checkout.session.completed lands here and
// becomes a CONFIRMED order in the book. Signature is verified with
// STRIPE_WEBHOOK_SECRET (docs/COMMERCE.md). Digital orders get a parcel
// token; physical orders wait for the Foreman's morning tickets [D5].

async function verifySignature(payload, header, secret) {
  const parts = Object.fromEntries(header.split(',').map((p) => p.split('=')));
  const t = parts.t;
  const v1 = parts.v1;
  if (!t || !v1) return false;
  if (Math.abs(Date.now() / 1000 - Number(t)) > 300) return false; // 5 min tolerance
  const key = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${t}.${payload}`));
  const hex = [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
  if (hex.length !== v1.length) return false;
  let diff = 0;
  for (let i = 0; i < hex.length; i++) diff |= hex.charCodeAt(i) ^ v1.charCodeAt(i);
  return diff === 0;
}

function orderId() {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const r = Array.from(crypto.getRandomValues(new Uint8Array(3)))
    .map((b) => 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'[b % 31]).join('');
  return `TB-${d}-${r}9`.slice(0, 16);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const payload = await request.text();

  if (env.STRIPE_WEBHOOK_SECRET) {
    const header = request.headers.get('stripe-signature') || '';
    if (!(await verifySignature(payload, header, env.STRIPE_WEBHOOK_SECRET))) {
      return new Response('bad signature', { status: 400 });
    }
  } else {
    // Refuse unsigned traffic rather than book phantom revenue.
    return new Response('webhook secret not configured', { status: 503 });
  }

  let event;
  try { event = JSON.parse(payload); } catch { return new Response('bad payload', { status: 400 }); }
  if (event.type !== 'checkout.session.completed') return new Response('ignored', { status: 200 });

  const s = event.data.object;
  const meta = s.metadata || {};
  const sku = String(meta.sku || 'UNKNOWN').slice(0, 24);
  const tier = String(meta.tier || 'unknown').slice(0, 12);
  const qty = 1; // payment links carry quantity in line items; default 1, Shopkeeper reconciles weekly
  const physical = tier !== 'digital';

  const addr = s.shipping_details || s.customer_details || {};
  const a = addr.address || {};
  const addressLine = physical
    ? [addr.name, a.line1, a.line2, `${a.city || ''} ${a.state || ''} ${a.postal_code || ''}`.trim(), a.country]
        .filter(Boolean).join(', ')
    : '';

  const id = orderId();
  const order = {
    id, ts: new Date().toISOString(),
    status: 'CONFIRMED', kind: 'order',
    name: (s.customer_details && s.customer_details.name) || 'Stripe customer',
    email: (s.customer_details && s.customer_details.email) || '',
    items: `${sku}:${tier}:${qty}`,
    amount_usd: Math.round((s.amount_total || 0) / 100),
    source: 'stripe',
    address: addressLine,
    note: `stripe session ${String(s.id || '').slice(0, 40)}`,
    history: [{ ts: new Date().toISOString(), to: 'CONFIRMED', by: 'stripe' }],
  };
  if (!physical) {
    order.parcel_token = crypto.randomUUID();
    order.downloads = 0;
  }
  await env.SHOPKV.put(`order:${id}`, JSON.stringify(order));

  // Digital fulfillment letter, if the mail rail is configured.
  if (!physical && order.email && env.RESEND_API_KEY && env.MAIL_FROM && env.PARCEL_BASE_URL) {
    const site = new URL(request.url).origin;
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        from: env.MAIL_FROM, to: [order.email],
        subject: `Your download — ${order.id}`,
        text: `Thank you. Your file is ready, sized for home printing at 8.5 x 11, 11 x 17, and 18 x 24:\n\n${site}/api/parcel?o=${id}&t=${order.parcel_token}\n\nThe link is yours and allows five downloads. Print it tonight; the source and citation are set on the sheet, as on everything we print.\n\nThe Shop Desk\nThomas Broadside Co.\nAustin: Printed by Thomas Graphics`,
      }),
    }).catch(() => {});
  }

  return new Response('booked', { status: 200 });
}
