// The parcel window — hands a paid digital customer their file.
//   GET /api/parcel?o=<order id>&t=<token> → 302 to <PARCEL_BASE_URL>/<sku>.pdf
// Five downloads per order; tokens live on the order in KV. Print-ready
// PDFs are never in the public site tree (docs/COMMERCE.md).

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const id = String(url.searchParams.get('o') || '').slice(0, 24);
  const token = String(url.searchParams.get('t') || '').slice(0, 64);
  if (!id || !token) return plain('This parcel window needs the link from your email.', 400);

  const raw = await env.SHOPKV.get(`order:${id}`);
  if (!raw) return plain('No such order. Write the shop desk and we will make it right.', 404);
  const order = JSON.parse(raw);

  if (!order.parcel_token || order.parcel_token !== token) {
    return plain('That link does not match the order. Write the shop desk.', 403);
  }
  if ((order.downloads || 0) >= 5) {
    return plain('This link has reached its five downloads. Write the shop desk and we will re-cut it.', 410);
  }
  if (!env.PARCEL_BASE_URL) {
    return plain('Digital delivery is being stocked. Write the shop desk and we will send the file by hand.', 503);
  }

  const sku = String(order.items || '').split(':')[0].replace(/[^A-Z0-9-]/g, '');
  if (!sku) return plain('This order carries no digital item. Write the shop desk.', 400);

  order.downloads = (order.downloads || 0) + 1;
  await env.SHOPKV.put(`order:${id}`, JSON.stringify(order));

  return Response.redirect(`${env.PARCEL_BASE_URL.replace(/\/$/, '')}/${sku}.pdf`, 302);
}

function plain(text, status) {
  return new Response(`${text}\n\n— Thomas Broadside Co.\n`, {
    status, headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}
