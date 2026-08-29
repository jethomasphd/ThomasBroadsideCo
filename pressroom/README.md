# The Pressroom Folder

Generated paper for Ben and David [D5]. Never hand-edited — the Foreman's
tool writes it fresh each morning:

```bash
python3 tools/make_job_tickets.py            # from the live order book
python3 tools/make_job_tickets.py --sample   # rehearsal from sample orders
```

- `RUN_SHEET.md` — today's queue, oldest first, editions starred. Print it
  and leave it on the bench, or read the same queue at `/pressroom` on the
  shop tablet.
- `tickets/TICKET-<id>.md` — one page per physical order: the job, the
  address, and the four boxes (pulled · **inspected — David's box, no
  exceptions [D6]** · packed · shipped w/ tracking).
- `specs/` — the Typographer's print-layout specs per design, for David.

The plain-language rules of the room are in `docs/PRESSROOM_RUNBOOK.md`.
