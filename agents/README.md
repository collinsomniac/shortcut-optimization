# Agent entry point

For active continuation, begin with:

1. [Next-chat handoff](next-chat-handoff.md)
2. [Current harness architecture](../docs/architecture/current-harness.md)
3. [Shortcut Worker implementation status](../docs/implementation/shortcut-worker-status.md)
4. [Shortcut Worker protocol](../examples/shortcut-worker/protocol.json)
5. [Research brief](research-brief.md)

The project now has both a research corpus **and live harness infrastructure**. Do not assume that every proposed semantic method is already routable on the phone; verify live state against Supabase and the target device before claiming support.

## Operating principles

- Prefer the contained `shortcuts.*` subsystem for Shortcut work.
- Treat generic shell/desktop execution as a fallback, not the default abstraction.
- `harness.info` is scoped to four fixed harness folders; its supplied export dynamically lists their members. It is not full-library discovery and does not establish dispatcher policy.
- Use Get My Shortcuts for native collection inventory; do not crawl a-Shell's filesystem looking for the private Shortcuts database.
- Distinguish launch, execution and verified postcondition.
- Preserve exact identity/version/hash for mutations where possible.
- Require confirmation for destructive deletion.
- Keep credentials and private exported workflows out of GitHub and untrusted signing services.

## Research work

For source/evidence work, also read:
- [Research home base](../docs/research/index.md)
- [Research methodology](../docs/research/methodology.md)
- [Evidence policy](../docs/evidence.md)
- [Source ledger](../docs/research/source-ledger.md)

Use the repository as the durable source of truth. When a live experiment changes a claim, update the implementation status and next-chat handoff in the same pass.
