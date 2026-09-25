# shortcut-public-artifact

Deployment note for generic signed Shortcut fixtures.

The live Edge Function is intentionally public (`verify_jwt=false`) but serves
only two hardcoded, non-sensitive fixtures:

- `hubsign-probe`
- `copy-actions`

It cannot enumerate or request arbitrary rows from `shortcuts.artifacts`.
The currently deployed version embeds the two signed AEA containers at deploy
time so serving them has no runtime database dependency.

Do not add private/user-specific Shortcut artifacts to this endpoint.

The signed fixture provenance and hashes live in:
- `experiments/hubsign-import-probe/README.md`
- `experiments/ios-action-pasteboard/README.md`
