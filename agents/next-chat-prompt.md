You are continuing active development of my iPhone/Apple Shortcuts agent harness.

Before making assumptions, use @GitHub and @Supabase to inspect the live state.

Primary GitHub repo:
- collinsomniac/shortcut-optimization

Primary Supabase project:
- iphone-harness
- project ref: zpdtlzpvshlpyqbfbzye

Read these files first, in order:
1. agents/next-chat-handoff.md
2. docs/architecture/current-harness.md
3. docs/implementation/shortcut-worker-status.md
4. examples/shortcut-worker/protocol.json
5. docs/research/shortcut-worker-control-plane.md
6. docs/research/supabase-compartmentalization.md

Then verify relevant live state in Supabase rather than trusting documentation blindly.

Important context:
- iphone-main and desktop-main share the same Supabase control plane.
- harness.info is a hardcoded allowlist/manifest, NOT a live Shortcut-library inventory.
- I am comfortable treating the Shortcuts app primarily as an agent-managed workspace; preserving unrelated personal Shortcuts is not an important constraint.
- I want the Shortcuts subsystem to be clearly contained and easy for agents to use. Generic desktop/shell tools may be available, but agents should not need them for ordinary Shortcut operations.
- Long term I want full library visibility, generation, organization, execution, verified receipts, export/versioning, and especially PROGRAMMATIC EDITING of Shortcuts and the harness itself.
- Prefer lower-level deterministic artifact/graph editing where practical over relying entirely on Apple's Describe a Shortcut UI. Third-party/open-source compatibility is welcome when it improves capability.
- We already inspected an iOS 27 Generate Shortcut donor artifact and built deterministic plist compiler probes. Do not repeat that discovery unless validating a changed assumption.
- a-Shell cannot access the private Shortcuts database; use native Get My Shortcuts for inventory.
- Supabase should remain the shared bus; do not casually split desktop and iPhone into separate projects.

Your immediate objective should be to advance the lowest-level self-modification path.

Strong preferred next experiment:
1. obtain/export a harmless existing harness Shortcut, ideally harness.info or a duplicate;
2. parse it into a lossless/canonical representation;
3. make one small deterministic structural patch, ideally adding/updating a registry entry;
4. validate using known iOS 27 action/AppIntent catalogs such as Shortcuts Playground where useful;
5. sign/import through the safest available trusted route;
6. execute a fixture and verify the postcondition;
7. document the exact result and update the canonical handoff/status docs.

If the direct round trip is blocked, investigate the best alternative route (native Generate Shortcut, companion/native app, macOS signer, third-party compiler/signer, Shortcuts action catalogs, App Intents, or a hybrid), but produce an empirical result rather than another speculative architecture pass.

Preserve compatibility with existing agents and RPC methods. Keep destructive operations confirmation-gated. Do not expose credentials or private workflow contents to third-party services without necessity and explicit justification.

Use the repo as the source of truth, make changes there as they become validated, and keep docs concise enough that a later agent can resume from them without needing this conversation.
