# GitHub Pages preparation

The repo is organized so documentation can be published later without a separate application stack.

Proposed publishing source: the repository root, preserving relative links between docs, packages, and agent resources. Add a Jekyll-compatible home page or static build when publication is requested. Keep machine-readable catalog files directly fetchable.

Before publishing:
- Render Markdown and check internal links.
- Label experimental packages and missing artifacts visibly.
- Keep installation links separate from run links.
- Launch only after an explicit user action.
- Do not put private input, tokens, or automatic callbacks into public pages.
- Test project-subpath URLs on Safari and ChatGPT's link-opening flow.
- Verify hosting/build configuration and the resulting live URL.

Pages is not enabled or deployed by this foundation change. No runtime shortcut functionality depends on hosting.
