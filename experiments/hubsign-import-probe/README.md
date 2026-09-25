# HubSign generic import probe

Status: **signing verified; iOS import/execution not yet verified**  
Updated: 2026-09-25 UTC.

The existing Supabase `shortcut-artifact` bridge successfully signed two
credential-free artifacts through RoutineHub HubSign:

| Fixture | Bytes | SHA-256 |
|---|---:|---|
| SO HubSign Probe | 22,152 | `733eea54bc8bbbda4d48ccd3177d0007243fadba770c304f660b859ad2fd9b43` |
| SO Copy Actions | 22,337 | `384763f4cd4e2a5012950820a5c803dfac352f9f40f585a5a8f6ce202c8f5088` |

Both cached outputs begin with `AEA1`.

The first probe contains only a Comment and Show Result. The second is the
generic pasteboard helper documented in
[../ios-action-pasteboard/README.md](../ios-action-pasteboard/README.md).

No private `harness.info` bytes were sent to HubSign.

A stable public Edge Function, `shortcut-public-artifact`, is intentionally
whitelisted to these generic fixtures only. The live helper endpoint was
downloaded from `desktop-main` and reproduced the expected 22,337-byte AEA1
container and SHA-256.

The remaining question is whether iOS accepts and installs the signed helper.
Automatic `shortcuts://import-shortcut` dispatch was blocked by the execution
guard in the agent environment, so the device import should be performed by the
user opening the fixture normally. Do not route around that guard.
