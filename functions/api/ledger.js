// The ledger tap — token-guarded read of the bell counters for a month,
// so tools/pull_ledger.py can mirror KV into the CSV book of record [D7].
//   GET ?month=YYYY-MM → { bell: {date: n}, paths: {date: {path: n}}, refs: {date: {host: n}} }

function authed(request, env) {
  const h = request.headers.get('authorization') || '';
  return env.PRESS_TOKEN && h.replace(/^Bearer\s+/i, '') === env.PRESS_TOKEN;
}

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!authed(request, env)) return json({ error: 'the shop token is required' }, 401);
  const url = new URL(request.url);
  const month = url.searchParams.get('month') || new Date().toISOString().slice(0, 7);
  if (!/^\d{4}-\d{2}$/.test(month)) return json({ error: 'month must be YYYY-MM' }, 400);

  const out = { month, bell: {}, paths: {}, refs: {} };
  for (const [prefix, sink] of [
    [`bell:t:${month}-`, 'bell'],
    [`bell:d:${month}-`, 'paths'],
    [`bell:r:${month}-`, 'refs'],
  ]) {
    let cursor;
    do {
      const page = await env.SHOPKV.list({ prefix, cursor, limit: 1000 });
      for (const k of page.keys) {
        const val = parseInt(await env.SHOPKV.get(k.name), 10) || 0;
        const rest = k.name.slice(prefix.length - 3); // "DD" or "DD:<path|ref>"
        const date = `${month}-${rest.slice(0, 2)}`;
        if (sink === 'bell') {
          out.bell[date] = val;
        } else {
          const key = rest.slice(3);
          out[sink][date] = out[sink][date] || {};
          out[sink][date][key] = val;
        }
      }
      cursor = page.list_complete ? null : page.cursor;
    } while (cursor);
  }
  return json(out);
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
}
