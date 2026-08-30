// The bell — first-party door counter. Writes daily aggregate counters to KV:
//   bell:t:<YYYY-MM-DD>            total door swings
//   bell:d:<YYYY-MM-DD>:<path>     per-page
//   bell:r:<YYYY-MM-DD>:<refhost>  per-referrer hostname
// Read-modify-write counters can drop a beat under simultaneous writes;
// at door-swing scale that is a rounding error and the simplicity is the
// point (Keeper's charter). Mirrored to CSV daily by tools/pull_ledger.py.

export async function onRequestPost(context) {
  const { request, env } = context;
  try {
    const data = await request.json();
    let path = typeof data.p === 'string' ? data.p : '/';
    if (!path.startsWith('/')) path = '/';
    path = path.split('?')[0].slice(0, 96);
    if (path.startsWith('/pressroom') || path.startsWith('/ledger') || path.startsWith('/api/')) {
      return new Response(null, { status: 204 });
    }
    let ref = typeof data.r === 'string' ? data.r.toLowerCase().slice(0, 64) : '';
    ref = ref.replace(/^www\./, '').replace(/[^a-z0-9.-]/g, '') || 'direct';
    // utm_source arrives as a first-party aggregate referrer so the
    // Chronicler can grade paid channels against our own ledger
    // (docs/GROWTH.md); still no per-visitor anything [D2].
    let utm = typeof data.u === 'string' ? data.u.toLowerCase().slice(0, 24) : '';
    utm = utm.replace(/[^a-z0-9_-]/g, '');

    const day = new Date().toISOString().slice(0, 10);
    const bump = async (key) => {
      const cur = parseInt(await env.SHOPKV.get(key), 10) || 0;
      await env.SHOPKV.put(key, String(cur + 1), { expirationTtl: 60 * 60 * 24 * 400 });
    };
    await bump(`bell:t:${day}`);
    await bump(`bell:d:${day}:${path}`);
    await bump(`bell:r:${day}:${ref}`);
    if (utm) await bump(`bell:r:${day}:utm-${utm}`);
    return new Response(null, { status: 204 });
  } catch (e) {
    return new Response(null, { status: 204 }); // the bell never errors outward
  }
}
