// The drafting desk — token-guarded relay to the Anthropic API for the
// clerks' drafting tasks. Internal only: no customer-facing chat exists in
// this store [D1]. Drafts are not decisions; humans sign [D9].
//   POST { task, input, context? } → { task, text }
// Model comes from env.LLM_MODEL (Keeper pins it; docs/DEPLOY.md §3).

const HOUSE = `You draft for Thomas Broadside Co., a family print shop in
Austin, Texas that prints founding documents on its own press. House rules:
(1) Cited — never state a quote, date, or attribution as fact without
flagging what must be verified against a primary source; you draft, a human
verifies. (2) Pre-partisan — the founding era, never party politics.
(3) Printed here — the press, the paper, the place are the story.
Voice: a letter from a shop. Plain, warm, certain. Short sentences carrying
real facts. No hype, no emoji, no exclamation points, never the word
"elevate", and never any mention of AI or machines on customer surfaces.
Sign customer letters "The Shop Desk, Thomas Broadside Co." Every draft is
reviewed by a human before use; write so that review is easy.`;

const TASKS = {
  label_draft: `Draft a museum-label provenance paragraph (60-110 words) for a product page: what the object is, its source, its typeface, its press. End with a bracketed list of every claim a human must verify.`,
  journal_draft: `Draft a journal entry (250-450 words) for the given anniversary or shop event. One idea, told plainly, with one concrete craft detail from the pressroom. End with a bracketed list of claims to verify.`,
  pin_batch: `Draft 5 Pinterest pin descriptions (each ≤160 characters) plus alt text for the given design and tier. Same three facts in the same order: the document, the press, the place. Three lowercase hashtags maximum per pin.`,
  reply_draft: `Draft a reply letter from the shop desk to the given customer message. Answer the actual question in the first two sentences with concrete facts (ship day, paper, source). Warm close, no apology theater. Flag anything that needs Ben (dates) or Jacob (prices, refunds).`,
  provenance_questions: `You are a hostile historian reviewing the given design's label and excerpt. Return only the numbered list of questions that must be answered from primary sources before this may be called cited. Never render verdicts; questions only.`,
  wholesale_letter: `Draft a wholesale quote letter for the given inquiry: acknowledge the institution, restate the request, present per-unit and set pricing as provided (never invent prices — leave [PRICE] markers if absent), note invoicing terms and Austin production, close with Ben's follow-up call.`,
};

function authed(request, env) {
  const h = request.headers.get('authorization') || '';
  return env.PRESS_TOKEN && h.replace(/^Bearer\s+/i, '') === env.PRESS_TOKEN;
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!authed(request, env)) return json({ error: 'the shop token is required' }, 401);
  if (!env.ANTHROPIC_API_KEY) return json({ error: 'drafting desk not configured (ANTHROPIC_API_KEY unset)' }, 503);
  if (!env.LLM_MODEL) return json({ error: 'no model pinned (LLM_MODEL unset — Keeper, see docs/DEPLOY.md)' }, 503);

  let data;
  try { data = await request.json(); } catch { return json({ error: 'bad request' }, 400); }
  const task = TASKS[data.task];
  if (!task) return json({ error: `task must be one of: ${Object.keys(TASKS).join(', ')}` }, 400);
  const input = String(data.input || '').slice(0, 12000);
  const extra = String(data.context || '').slice(0, 8000);
  if (!input) return json({ error: 'input is required' }, 400);

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: env.LLM_MODEL,
      max_tokens: 1500,
      temperature: data.task === 'provenance_questions' ? 0.2 : 0.6,
      system: `${HOUSE}\n\nTASK: ${task}`,
      messages: [{ role: 'user', content: extra ? `${input}\n\n---\ncontext:\n${extra}` : input }],
    }),
  });

  if (!res.ok) {
    const detail = await res.text();
    return json({ error: 'the drafting desk is down', detail: detail.slice(0, 400) }, 502);
  }
  const body = await res.json();
  const text = (body.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('\n');
  return json({ task: data.task, text, note: 'Draft only. A human signs [D9].' });
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
}
