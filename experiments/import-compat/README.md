# iOS Shortcut import compatibility matrix

Updated 2026-09-25.

## Why

The target iPhone successfully imported `SO-Copy-Actions`, but later
ChatGPT-hosted download links for `harness.shortcuts.library` v0.3 and
`harness.shortcuts.stage` v0.1 failed in the generic file viewer with
"The file download failed." Shortcuts never saw those artifacts, so that result
is a **transport failure**, not an import failure.

The successful SO helper and the newer controller also differ in construction:
SO-Copy-Actions was assembled with repository plist tooling; the new artifacts
are Cherri-compiled.

A further build audit found that Cherri `--comments` can materialize included
library documentation as real Shortcut Comment actions. A tiny one-action
fixture previously expanded to 37 actions. Compact and comment-heavy Cherri
builds are therefore separate compatibility variables.

## Result stages

Record each fixture independently at five stages:

1. **transported** — iOS obtains the bytes;
2. **recognized** — iOS offers Open in Shortcuts / the Shortcut import UI;
3. **imported** — Add Shortcut succeeds;
4. **executed** — fixture runs;
5. **verified** — expected postcondition/output is observed.

Never collapse these into one `success` state.

## Fixture order

1. `known-good-copy-actions`
   - exact previously imported positive control;
   - repo plist tooling + HubSign.
2. `manual-hubsign-probe`
   - tiny repo-built Comment + Show Result artifact.
3. `cherri-basic`
   - minimal compact Cherri Show Result.
4. `cherri-basic-comments`
   - same semantic source with Cherri `--comments`.
5. `cherri-inventory`
   - compact Cherri + first-party Get My Shortcuts.
6. `cherri-create`
   - compact Cherri + current Create Shortcut AppIntent.
7. `cherri-controlflow`
   - compact Cherri conditional grouping.
8. `manager-v03-compact`
   - full pure-native manager source, compact compile.
9. `manager-v03-comments`
   - same manager source using old comment-heavy build mode.
10. `stager-v01-compact`
    - file/network bootstrap source, compact compile.
11. `stager-v01-comments`
    - same stager source using old comment-heavy build mode.

Do not infer anything from a later fixture until the earlier control passes.

## Interpretation

- #1 transport fails:
  delivery surface is broken; artifact construction is not yet under test.
- #1 works but #2 import fails:
  current signing/artifact acceptance changed or the manual artifact is invalid.
- #2 imports but #3 fails:
  compact Cherri serialization/top-level metadata is implicated.
- #3 imports but #4 fails:
  `--comments` / emitted comment graph is implicated.
- #3/#4 import and #5 fails:
  Get My Shortcuts or its representation is implicated.
- #5 imports and #6 fails:
  Create Shortcut AppIntent descriptor/serialization is implicated.
- #6 imports and #7 fails:
  control-flow grouping is implicated.
- #1–#7 import but compact manager fails:
  complexity or another management action family is implicated.
- compact manager imports but comments manager fails:
  comment bloat/build mode is the likely cause.
- manager imports but compact stager fails:
  document/network action family or stager graph is implicated.

Importability and runtime correctness remain separate questions.

## Delivery

The preferred test transport is the public Supabase Edge Function:

`shortcut-import-compat?name=<fixture-slug>`

It:
- reads only the source-controlled public compatibility manifest;
- fetches only a filename named in that manifest;
- verifies exact byte count;
- verifies SHA-256;
- verifies `AEA1`;
- returns `application/x-apple-shortcut` with an attachment filename.

It has no database/service-role access and is intentionally public only because
all fixtures are generic/non-sensitive.

## Native fetch bootstrap

If direct HTTPS attachment handling is inconsistent on iOS, a separate
Apple-generated `harness.shortcuts.fetch` experiment is available. It uses
Get Contents of URL → Save File → Open File. This is a bootstrap transport, not
a silent Shortcuts-library writer.

See:
`examples/shortcut-worker/fetch-bootstrap-builder-prompt.txt`.
